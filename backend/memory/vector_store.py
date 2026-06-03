import chromadb
import hashlib
from chromadb.utils import embedding_functions


# Initialize kr diya locally
client = chromadb.PersistentClient(path="./memory/chroma_db")

# Sentence transformer use kro embedding bnane ke liye
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

#Collection create kro , jaha ye sb embedding store hongi
collection = client.get_or_create_collection(
    name = "research_memory", 
    embedding_function=embedding_fn
)

#Ye bo function hai jo embeddings ko store krega
def store(tool_name: str, query: str, content: str) -> None:
    """Store a tool result in vector store"""
    
    #chunk = 1000 chars, isliye hr 1000 char ke liye use chunks list me add kr diya 
    chunks = [content[i: i+1000] for i in range(0, len(content), 1000)]
    
    for i, chunk in enumerate(chunks):
        
        # Create unique ID from tool + query + chunk index
        doc_id = hashlib.md5(f"{tool_name}: {query} :{i}".encode()).hexdigest()
        
        try:
            collection.upsert(
                ids=[doc_id],
                documents=[chunk],
                metadatas=[{
                    'tool': tool_name,
                    'query':query,
                    'chunk':i
                }]
            )
            
        except Exception as e:
            print(f"[VECTOR STORE] Store error: {e}")
            
    print(f"[vector Store] stored {len(chunks)} chunks from {tool_name}")
    
# Ab bo function jo retrieve krega -> semantic search
def retrieve(query: str, n_results: int = 3) -> str:
    """Retrieve semantically similar content from vector store."""
    
    try:
        count = collection.count()
        if count == 0:
            return ""
        
        # Don't request more results than we have
        n_results = min(n_results, count)
        
        results = collection.query(
            query_texts=[query], n_results=n_results
        )
        
        if not results["documents"][0]:
            return ""

        retrieved = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            retrieved.append(
                f"[From {meta['tool']} — '{meta['query']}']\n{doc}"
            )
            
        return "\n\n---\n\n".join(retrieved)
    
    except Exception as e:
        print(f"[VECTOR STORE] Retrieve error: {e}")
        return ""
    
def clear() -> None:
    """Clear all stored memory."""
    global collection
    client.delete_collection("research_memory")
    collection = client.get_or_create_collection(
        name="research_memory",
        embedding_function=embedding_fn
    )
    print("[VECTOR STORE] Memory cleared")


def count() -> int:
    """Return number of stored chunks."""
    return collection.count()