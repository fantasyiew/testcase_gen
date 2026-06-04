from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_template(
    """你是一名专业的问答助手，基于以下提供的上下文信息来回答问题。
如果上下文中没有相关信息，请直接说明信息不足，不知道。

上下文信息：
{context}

问题：{input}
答案："""
)

testcase_gen_prompt = ChatPromptTemplate.from_template(
    """你是一名专业的软件测试工程师，基于以下提供的上下文信息来生成测试用例。
仿照参考的测试用例进行生成，尽可能覆盖所有的测试点。如果上下文中没有能够满足生成测试用例的相关信息，请直接说明信息不足。

你需要根据提供的功能点说明来生成测试用例，并以 JSON 格式输出，每个测试用例包含以下字段：
- module_name: 模块名称
- function: 功能项
- case_description: 用例说明
- precondition: 前置条件
- input_data: 输入
- steps: 执行步骤
- expected_result: 预期结果
- priority: 重要程度（高/中/低）
- test_result: 执行用例测试结果

其中module_name和function参考功能点：{input}的描述；test_result全部为未执行；precondition参考功能点说明，根据你生成测试用例的输入，系统预期会作何反馈；其余部分参考以下用例。
以下是一段软件的功能点说明及其对应的测试用例示例（JSON 格式）：

功能点说明：
-正确输入用户名、密码，点击【登录】，正确进入系统，默认打开对应角色左侧菜单首功能页面，系统右上角显示"个人中心"头像、"消息"图标，左侧显示系统 Logo、菜单；
-登录校验：
  -未输入用户名，提示："请输入用户名"；
  -未输入密码，提示："请输入密码"；
  -输入错误用户名，提示："登录账号不存在！"；
  -输入错误密码，提示："登录密码错误!"。

对应的测试用例（JSON 格式）：
{{
    "test_cases": [
        {{
            "module_name": "登录",
            "function": "登录",
            "case_description": "输入不存在的用户名校验（中文）",
            "precondition": "正确进入 ERP 管理平台",
            "input_data": "用户名：测试",
            "steps": "输入相关信息，点击【登录】",
            "expected_result": "提示："登录账号不存在！"。",
            "priority": "高",
            "test_result": "通过"
        }},
        {{
            "module_name": "登录",
            "function": "登录",
            "case_description": "输入用户名校验（为空）",
            "precondition": "正确进入 ERP 管理平台",
            "input_data": "用户名：",
            "steps": "输入相关信息，点击【登录】",
            "expected_result": "提示："请输入用户名"。",
            "priority": "高",
            "test_result": "通过"
        }}
    ]
}}

参考以上内容，给你以下功能点说明，请你生成关于{{input}}的测试用例，并以 JSON 格式返回：
{{context}}

请只返回 JSON 格式的数据，不要包含其他解释性文字。
"""
)

extract_features_prompt = ChatPromptTemplate.from_template(
    """你是一名专业的软件测试工程师，请根据以下软件需求文档的目录页内容，提取所有功能点。

要求：
1. 识别目录中的各级标题，将一级/二级标题作为功能点分类（category），将更细粒度的标题作为具体功能点（feature）
2. 每个功能点格式为 "[功能点分类]-[具体功能点]"，例如："通用功能-登录"、"用户管理-修改密码"
3. 尽可能全面地提取所有功能点，不要遗漏
4. 忽略与功能无关的目录项（如前言、附录、参考文献等）
5. 以 JSON 格式返回，不要包含其他解释性文字

目录内容：
{toc_content}

请以以下 JSON 格式返回：
{{
    "feature_points": [
        {{
            "category": "功能点分类",
            "feature": "具体功能点"
        }},
        ...
    ]
}}

请只返回 JSON 格式的数据。
"""
)
