import json
import re
import time

from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from utils.myTools import get_model, extract_toc_from_docx
from .models import TestCaseList, FeaturePointList
from .prompts import rag_prompt, testcase_gen_prompt, extract_features_prompt
from .vectorstore import get_retriever, retrieve_docs
from db.feature_repo import FeatureRepo


class TestCaseGenPipeline:
    """测试用例生成流水线，封装模型、检索器和chains"""

    def __init__(self, model_name="qwen-plus", text_path="A1-需求说明书.docx", persist_directory="./chroma_db", k=5):
        self._model = get_model(model_name)
        self._retriever = get_retriever(text_path, persist_directory, k)
        self._doc_path = text_path
        self._build_chains()

    def _build_chains(self):
        def retrieve_docs_wrapper(query):
            return retrieve_docs(query, self._retriever)

        self._rag_chain = (
            {"context": RunnableLambda(retrieve_docs_wrapper), "input": RunnablePassthrough()}
            | rag_prompt
            | self._model
            | StrOutputParser()
        )

        output_parser = PydanticOutputParser(pydantic_object=TestCaseList)
        testcase_gen_prompt_with_format = testcase_gen_prompt.partial(
            format_instructions=output_parser.get_format_instructions()
        )

        self._test_gen_chain = (
            {"context": RunnablePassthrough(), "input": RunnablePassthrough()}
            | testcase_gen_prompt_with_format
            | self._model
            | output_parser
        )

        feature_output_parser = PydanticOutputParser(pydantic_object=FeaturePointList)
        extract_features_prompt_with_format = extract_features_prompt.partial(
            format_instructions=feature_output_parser.get_format_instructions()
        )

        self._extract_features_chain = (
            {"toc_content": RunnablePassthrough()}
            | extract_features_prompt_with_format
            | self._model
            | StrOutputParser()
        )

    def invoke_rag(self, query):
        """调用RAG链进行问答检索"""
        return self._rag_chain.invoke(query)

    def invoke_test_gen(self, context, input_desc):
        """调用测试用例生成链"""
        return self._test_gen_chain.invoke({"context": context, "input": input_desc})

    def extract_features(self, toc_content: str) -> list[str]:
        """从目录页内容中提取格式化的功能点列表

        Args:
            toc_content: 目录页的文本内容

        Returns:
            功能点字符串列表，格式为 "[功能点分类]-[具体功能点]"
        """
        raw_response = self._extract_features_chain.invoke(toc_content)

        json_str = re.search(r'\{[\s\S]*\}', raw_response)
        if json_str:
            data = json.loads(json_str.group())
            feature_list = FeaturePointList.model_validate(data)
            return [f"{fp.category}-{fp.feature}" for fp in feature_list.feature_points]

        return []

    def extract_features_from_doc(self, doc_path: str = None) -> list[str]:
        """直接从 Word 文档提取功能点列表

        Args:
            doc_path: .docx 文件路径，默认为 None 时使用初始化时传入的 text_path

        Returns:
            功能点字符串列表，格式为 "[功能点分类]-[具体功能点]"
        """
        path = doc_path or self._doc_path
        toc_content = extract_toc_from_docx(path)
        return self.extract_features(toc_content)

    def extract_and_save_features(self, doc_path: str = None) -> dict:
        """从文档提取功能点并持久化存储

        若该文档已提取过，则跳过 LLM 调用，直接返回数据库中的数据。

        Args:
            doc_path: .docx 文件路径

        Returns:
            {"features": [...], "stats": {"inserted": int, "skipped": int, "cached": bool}}
        """
        path = doc_path or self._doc_path

        if FeatureRepo.exists_by_doc(path):
            print(f"已存储过文档 {path} 的功能点，正在读取")
            features = FeatureRepo.get_by_doc(path)
            return {
                "features": [f["full_name"] for f in features],
                "stats": {"inserted": 0, "skipped": len(features), "cached": True}
            }

        toc_content = extract_toc_from_docx(path)

        raw_response = self._extract_features_chain.invoke(toc_content)

        json_str = re.search(r'\{[\s\S]*\}', raw_response)
        if json_str:
            data = json.loads(json_str.group())
            feature_list = FeaturePointList.model_validate(data)
            features = [
                {"category": fp.category, "feature": fp.feature}
                for fp in feature_list.feature_points
            ]
            stats = FeatureRepo.batch_insert(features, doc_path=path)
            stats["cached"] = False
            return {"features": [f"{fp['category']}-{fp['feature']}" for fp in features], "stats": stats}

        return {"features": [], "stats": {"inserted": 0, "skipped": 0, "cached": False}}

    def generate_test_cases_for_feature(self, feature_name: str) -> dict:
        """为单个功能点生成测试用例（不保存，返回给前端审核）

        Args:
            feature_name: 功能点名称，如 "通用功能-登录"

        Returns:
            {"feature_name": str, "test_point": str, "test_cases": [dict, ...], "elapsed_time": float}
        """
        start_time = time.time()

        test_point = self.invoke_rag(f"{feature_name}功能的相关说明是什么？")
        test_case_result = self.invoke_test_gen(context=test_point, input_desc=feature_name)

        cases = [
            {
                "module_name": c.module_name,
                "function": c.function,
                "case_description": c.case_description,
                "precondition": c.precondition,
                "input_data": c.input_data,
                "steps": c.steps,
                "expected_result": c.expected_result,
                "priority": c.priority,
                "test_result": c.test_result,
            }
            for c in test_case_result.test_cases
        ]

        elapsed_time = round(time.time() - start_time, 1)

        return {
            "feature_name": feature_name,
            "test_point": test_point,
            "test_cases": cases,
            "elapsed_time": elapsed_time,
        }

    def generate_test_cases_for_all_features(self) -> list[dict]:
        """为所有功能点批量生成测试用例（不保存，返回给前端审核）

        Returns:
            [{"feature_name": str, "test_point": str, "test_cases": [...], "elapsed_time": float}, ...]
        """
        features = FeatureRepo.get_all()
        results = []

        for fp in features:
            feature_name = fp["full_name"]
            try:
                result = self.generate_test_cases_for_feature(feature_name)
                results.append(result)
            except Exception as e:
                results.append({
                    "feature_name": feature_name,
                    "test_point": "",
                    "test_cases": [],
                    "elapsed_time": 0,
                    "error": str(e),
                })

        return results
