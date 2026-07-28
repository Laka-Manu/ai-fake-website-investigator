import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def create_rag_pipeline(
    data_path: str = "data/sample.txt",
    persist_directory: str = "./chroma_db"
):
    """
    Loads a document, splits it into chunks using RecursiveCharacterTextSplitter,
    generates embeddings using all-MiniLM-L6-v2, and stores them in ChromaDB.
    """
    # 1. Load the document
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Source file not found at: {data_path}")

    print(f"Loading document from: {data_path}")
    loader = TextLoader(data_path, encoding="utf-8")
    documents = loader.load()

    # 2. Split into roughly 20 chunks using RecursiveCharacterTextSplitter
    # Adjust chunk_size according to total length to yield around ~20 chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Successfully created {len(chunks)} chunks.")

    # 3. Initialize free HuggingFace Embedding model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 4. Save/Persist to Vector Database (ChromaDB)
    print("Creating vector store in ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"Vector Database successfully saved at '{persist_directory}'!")

    return vectorstore


if __name__ == "__main__":
    # Test script execution locally
    try:
        db = create_rag_pipeline()
        print("Pipeline built successfully!")
    except Exception as e:
        print(f"Error building pipeline: {e}")