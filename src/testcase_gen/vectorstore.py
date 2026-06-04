from utils.myTools import create_vectorstore


def get_retriever(text_path="A1-需求说明书.docx", persist_directory="./chroma_db", k=5):
    """创建并返回向量数据库检索器"""
    vectorstore = create_vectorstore(text_path, persist_directory,create_new=True)
    print("=== 知识库已就绪 ===")
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_docs(query, retriever):
    """检索相关文档并返回合并后的字符串"""
    docs = retriever.invoke(query)
    print(f"\n{'='*60}")
    print(f"[RAG检索] 查询: {query}")
    print(f"[RAG检索] 命中 {len(docs)} 个文档片段:")
    print(f"{'-'*60}")
    for i, doc in enumerate(docs, 1):
        content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        print(f"  [{i}] {content}")
    print(f"{'='*60}\n")
    return "\n\n".join([doc.page_content for doc in docs])
