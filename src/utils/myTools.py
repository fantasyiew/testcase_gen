import os
import re

from docx import Document
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages.tool import tool_call
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import *

def print_response_details(response):
    """
    打印大模型返回的 response 中不同类型消息的详细内容。
    """

    results=[]
    answer= None
    messages = response.get('messages', [])
    
    # 遍历消息列表并根据角色打印内容
    for  message in messages:
        if hasattr(message, 'additional_kwargs') and "tool_calls" in message.additional_kwargs:
            tool_calls= message.additional_kwargs["tool_calls"]
            for tool_call in tool_calls:
                tool_name= tool_call["function"]["name"]
                tool_args= tool_call["function"]["arguments"]
                results.append(f"调用工具: {tool_name}({tool_args})")
        elif message.type == "tool":
            tool_name= message.name
            tool_result= message.content
            results.append(f"{tool_name}的调用结果:{tool_result}")
        elif message.type == "ai":
            answer= message.content
    for result in results:
        print(f"- {result}")
    if answer:
        print(f"[最终的回复] {answer}")


# def print_stream_response_details(response):
#     """
#     打印大模型返回的流式输出 response 中不同类型消息的详细内容。
#     """
#
#     results = []
#     answer = None
#     messages = response.get('messages', [])
#
#     # 遍历消息列表并根据角色打印内容
#     for message in messages:
#         if hasattr(message, 'additional_kwargs') and "tool_calls" in message.additional_kwargs:
#             tool_calls = message.additional_kwargs["tool_calls"]
#             for tool_call in tool_calls:
#                 tool_name = tool_call["function"]["name"]
#                 tool_args = tool_call["function"]["arguments"]
#                 results.append(f"调用工具: {tool_name}({tool_args})")
#         elif message.type == "tool":
#             tool_name = message.name
#             tool_result = message.content
#             results.append(f"{tool_name}的调用结果:{tool_result}")
#         elif message.type == "ai":
#             answer = message.content
#     for result in results:
#         print(f"- {result}")
#     if answer:
#         print(f"[最终的回复] {answer}")


def get_model(model_name="qwen-plus"):
    """
    根据模型名称返回对应的 ChatOpenAI 实例
    :param model_name: 模型名称，默认为 "qwen-plus"
    :return: ChatOpenAI 实例
    """
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"配置中不存在该模型: {model_name}")

    config = MODEL_CONFIGS[model_name]
    return ChatOpenAI(
        model=config["model"],
        api_key=config["openai_api_key"],
        base_url=config["openai_api_base"]
    )

def create_vectorstore(text_path, persist_directory="./chroma_db",create_new=False):
    db_path = os.path.join(persist_directory, "chroma.sqlite3")
    if os.path.exists(db_path) and not create_new:
        print("检测到已存在的向量数据库")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=DashScopeEmbeddings()
        )
        print("向量数据库加载完成！")
    else:
        print("正在加载文档...")
        loader = Docx2txtLoader(text_path)
        documents = loader.load()
        print(f"成功加载文档，共 {len(documents)} 个文档")

        print("正在分割文本...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=50,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        print(f"文本分割完成，共 {len(splits)} 个文本块")

        print("正在创建向量数据库...")
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=DashScopeEmbeddings(),
            persist_directory=persist_directory
        )
        print("向量数据库创建完成！")

    return vectorstore


def extract_toc_from_docx(docx_path: str) -> str:
    """从 Word 文档中提取目录（基于 Heading 样式）

    策略：
    1. 扫描全文，提取所有 Heading 样式段落
    2. 过滤掉封面标题（如文档名）和"目录"本身
    3. 按层级缩进格式化输出

    Args:
        docx_path: .docx 文件路径

    Returns:
        格式化的目录文本
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"文档不存在: {docx_path}")

    doc = Document(docx_path)

    heading_level_map = {
        'Heading 1': 1, 'Heading 2': 2, 'Heading 3': 3, 'Heading 4': 4,
        'Heading 5': 5, 'Heading 6': 6, 'Heading 7': 7, 'Heading 8': 8, 'Heading 9': 9,
    }

    headings_found = []
    for para in doc.paragraphs:
        level = heading_level_map.get(para.style.name)
        if level is not None:
            text = para.text.strip()
            if text:
                headings_found.append((level, text))

    skip_keywords = ['目  录', '目录', '目 录']
    filtered_headings = []
    for level, text in headings_found:
        if text in skip_keywords:
            continue
        if level == 1 and len(text) < 10 and '需求' not in text and '说明' not in text:
            continue
        filtered_headings.append((level, text))

    indent_size = 2
    toc_lines = []
    for level, text in filtered_headings:
        indent = ' ' * indent_size * (level - 1)
        toc_lines.append(f"{indent}{text}")

    return '\n'.join(toc_lines)


