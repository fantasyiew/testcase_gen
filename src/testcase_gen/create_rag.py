import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 配置环境变量（从 .env 文件读取）
os.environ['LANGSMITH_TRACING'] = os.getenv('LANGSMITH_TRACING', 'true')
os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY', '')
os.environ['DASHSCOPE_API_KEY'] = os.getenv('DASHSCOPE_API_KEY', '')

QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
QWEN_API_URL = os.getenv('QWEN_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com')

# 初始化模型
model = ChatOpenAI(
    model="qwen-plus",
    openai_api_key=os.getenv('QWEN_API_KEY', ''),
    openai_api_base=os.getenv('QWEN_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
)

# 加载 Word 文档
print("正在加载文档...")
loader = Docx2txtLoader("/A1-需求说明书.docx")
documents = loader.load()
print(f"成功加载文档，共 {len(documents)} 个文档")

# 文本分割
print("正在分割文本...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=50,
    length_function=len,
)
splits = text_splitter.split_documents(documents)
print(f"文本分割完成，共 {len(splits)} 个文本块")

# 创建向量数据库
print("正在创建向量数据库...")
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=DashScopeEmbeddings(),
    persist_directory="./chroma_db"
)
print("向量数据库创建完成！")
