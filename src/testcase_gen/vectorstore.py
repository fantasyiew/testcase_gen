from utils.myTools import create_vectorstore


def get_retriever(text_path="A1-需求说明书.docx", persist_directory="./chroma_db", k=5):
    """创建并返回向量数据库检索器"""
    vectorstore = create_vectorstore(text_path, persist_directory,create_new=True)
    print("=== 知识库已就绪 ===")
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_docs(query, retriever):
    """检索相关文档并返回合并后的字符串"""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])
