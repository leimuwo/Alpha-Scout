import os
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 路径配置
DB_PATH = "./data_source/vector_db"
DATA_PATH = "./data_source/rag_data"

# 确保目录存在
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)

# 初始化 Embeddings
# 注意：这需要 OPENAI_API_KEY
def get_vectorstore():
    embedding_func = OpenAIEmbeddings()
    
    # 检查向量库是否已经有数据，这里做一个简单的逻辑
    # 实际生产中应该单独运行一个 ingestion 脚本
    if not os.listdir(DB_PATH) and os.listdir(DATA_PATH):
        # 如果 DB 为空但有数据文件，进行加载
        loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_func, persist_directory=DB_PATH)
    else:
        # 加载现有 DB 或创建一个空的
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embedding_func)
    
    return vectorstore

@tool
def query_financial_reports(query: str):
    """
    Searches internal financial reports (PDFs) for relevant information using RAG.
    Use this to find specific details from annual reports or research papers.
    """
    try:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant information found in internal reports."
        
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"RAG Error: {str(e)}. (Ensure OpenAI Key is set and PDFs are in data_source/rag_data)"