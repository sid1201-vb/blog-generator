from helper_functions.chroma_search import ChromaSearch, get_chroma_hybrid_search
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


def embed(path: str, chroma_search: ChromaSearch):
    with open(path, 'r', encoding='utf-8') as f:
        file = f.read()

    name = path.split("\\")[-1]

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(file)

    for i, chunk in enumerate(chunks):
        chunk_name = f"{name}_part_{i}"
        chroma_search.upload_document(chunk, chunk_name, "all", chunk_name)
        
        
def get_markdown_files(folder_path):
    try:
        md_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".md")]
        return md_files
    except FileNotFoundError:
        return "Error: Folder not found."
    except Exception as e:
        return f"Error: {e}"