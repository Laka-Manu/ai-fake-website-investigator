import os

# --- Loaders & Splitters ---
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Embedding Model Import with Fallback ---
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ModuleNotFoundError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Vector Store Import with Fallback ---
try:
    from langchain_chroma import Chroma
except ModuleNotFoundError:
    from langchain_community.vectorstores import Chroma


def create_rag_pipeline(
    data_path: str = "data/sample.txt",
    persist_directory: str = "./chroma_db"
):
    """
    1. Loads text documents.
    2. Splits them into chunks (~20 chunks).
    3. Generates vector embeddings using sentence-transformers (all-MiniLM-L6-v2).
    4. Saves/Persists vectors inside ChromaDB.
    """
    # 1. Document එක තිබේදැයි පරීක්ෂා කිරීම
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Source file not found at: '{data_path}'. "
            f"Please create a 'data/sample.txt' file with test text."
        )

    print(f"Loading document from: {data_path}")
    loader = TextLoader(data_path, encoding="utf-8")
    documents = loader.load()

    # 2. Text Splitting (RecursiveCharacterTextSplitter)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Successfully created {len(chunks)} chunks.")

    # 3. Free HuggingFace Embedding Model එක Load කිරීම
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 4. Vector Database එක (ChromaDB) සාදා Local Disk එකෙහි Save කිරීම
    print("Creating vector store in ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"Vector Database successfully saved at '{persist_directory}'!")

    return vectorstore


if __name__ == "__main__":
    # Test execution
    try:
        # data folder එක සහ sample.txt නොමැති නම් ස්වයංක්‍රීයව සාදනු ලැබේ
        os.makedirs("data", exist_ok=True)
        sample_path = "data/sample.txt"
        
        if not os.path.exists(sample_path):
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(
                    "AI Fake Website Investigator is a system designed to detect fraudulent e-commerce websites. "
                    "It uses RAG pipelines, machine learning models, and web scraping to evaluate suspicious URLs. "
                    "The system extracts text content, analyzes domain reputation, and flags scam indicators effectively."
                )
            print(f"Created a default test file at '{sample_path}'")

        db = create_rag_pipeline(data_path=sample_path)
        print("\n✅ RAG Pipeline completed successfully!")

    except Exception as e:
        print(f"\n❌ Error building pipeline: {e}")