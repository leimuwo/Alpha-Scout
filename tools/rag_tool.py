import os
import json
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

# 路径配置
DB_PATH = "./data_source/vector_db"
DATA_PATH = "./data_source/rag_data"

# 确保目录存在
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)

class SimpleTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start += self.chunk_size - self.chunk_overlap
        return chunks

def get_chroma_client():
    return chromadb.PersistentClient(path=DB_PATH)

def get_embedding_function():
    # 使用 sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

def ingest_data():
    client = get_chroma_client()
    embedding_func = get_embedding_function()
    
    # 获取或创建 collection
    collection = client.get_or_create_collection(
        name="financial_reports",
        embedding_function=embedding_func
    )
    
    # 检查是否已经有文档 (简单的检查，实际生产可能需要更复杂的增量更新)
    if collection.count() > 0:
        return collection

    splitter = SimpleTextSplitter()
    
    for filename in os.listdir(DATA_PATH):
        filepath = os.path.join(DATA_PATH, filename)
        text = ""
        
        try:
            if filename.endswith(".pdf"):
                print(f"Ingesting PDF {filename}...")
                reader = PdfReader(filepath)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
                    
            elif filename.endswith(".txt") or filename.endswith(".md"):
                print(f"Ingesting Text {filename}...")
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            else:
                continue

            if not text:
                continue
                
            chunks = splitter.split_text(text)
            
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename, "type": os.path.splitext(filename)[1]} for _ in range(len(chunks))]
            
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"Error ingesting {filename}: {e}")
            
    return collection

def query_financial_reports(query: str):
    """
    Searches internal financial reports (PDFs, TXT, MD) for relevant information using RAG.
    Use this to find specific details from annual reports or research papers.
    """
    try:
        collection = ingest_data()
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No relevant information found in internal reports."
        
        return "\n\n".join(results['documents'][0])
    except Exception as e:
        return f"RAG Error: {str(e)}. (Ensure PDFs are in data_source/rag_data)"

if __name__ == "__main__":
    # Test
    print(query_financial_reports("贵州茅台的利润情况"))