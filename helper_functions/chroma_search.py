import os
import pickle
import numpy as np
from rank_bm25 import BM25Okapi
from langchain.embeddings import HuggingFaceEmbeddings
from chromadb import Client

from typing import List, Dict, Any

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")

class ChromaSearch:
    def __init__(self, collection_name: str, storage_path: str = "chroma_store.pkl"):
        """
        Initialize the ChromaSearch class with a specific collection name and model.
        """
        self.client = Client()
        self.collection_name = collection_name
        self.model = embedding_model
        self.storage_path = storage_path
        self.bm25 = None
        self.document_texts = []
        self.document_metadata = []

        # Create or fetch the collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(self.collection_name)

        # Load persisted data if available
        if self._is_collection_empty():
            self._load_persisted_data()
        # Initialize BM25 with loaded documents
        self._initialize_bm25()
        print(f"Collection initialized: {self.collection_name}")

    def _initialize_bm25(self):
        """
        Initialize or update the BM25 index with current documents.
        """
        if not self.document_texts:
            results = self.collection.get()
            self.document_texts = results.get("documents", [])
            self.document_metadata = results.get("metadatas", [])

        if self.document_texts:
            # Tokenize documents for BM25
            tokenized_docs = [doc.lower().split() for doc in self.document_texts]
            self.bm25 = BM25Okapi(tokenized_docs)


    def _persist_data(self):
        """
        Persist the collection's documents, embeddings, and metadata to a file.
        """
        data = self.collection.get()
        with open(self.storage_path, "wb") as f:
            pickle.dump(data, f)
        print(f"Data persisted to {self.storage_path}")
        # Update BM25 index after persisting
        self._initialize_bm25()


    def _load_persisted_data(self):
        """
        Load persisted data from the storage file and add it to the collection.
        """
      
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "rb") as f:
                data = pickle.load(f)

            self.collection.add(
                documents=data["documents"],
                embeddings=data["embeddings"],
                metadatas=data["metadatas"],
                ids=data["ids"],
            )
            print(f"Data loaded from {self.storage_path}")

    def upload_document(self, document_text: str, document_name: str, role: str, document_id: int):
        """
        Upload a document to the ChromaDB with its embedding and metadata.
        """
        # Create the embedding for the document text
        embedding = self.model.embed_documents([document_text])[0]

        # Create metadata for the document
        metadata = {
            "document_name": document_name,
            "role": role[0],
            "document_id": document_id.split("_")[0]
        }

        # Add the document to the collection (text, embedding, and metadata)
        self.collection.add(
            documents=[document_text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[str(document_id)]  # Use document_id as a unique identifier for this document
        )
        self._persist_data()  # Persist data after uploading a document
        # self._load_persisted_data()
        print(f"Document '{document_name}' uploaded successfully with ID: {document_id}")

    def delete_document(self, document_id: int):
        """
        Delete a document and its index from the Chroma database by document ID stored in metadata.
        Also, remove it from the persisted pickle file.
        """
        try:
            # Find documents matching the specified document_id in metadata
            results = self.collection.get()
            ids_to_delete = [
                doc_id
                for doc_id, metadata in zip(results["ids"], results["metadatas"])
                if document_id in metadata.get("document_id")
            ]

            if not ids_to_delete:
                print(f"No document found with ID {document_id}.")
                return

            # Delete the matching documents from the collection
            self.collection.delete(ids=ids_to_delete)
            print(f"Document(s) with ID {document_id} have been deleted from the collection.")

            # Update the persisted pickle file
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "rb") as f:
                    data = pickle.load(f)
                
                # Remove documents with the specified document_id
                remaining_indices = [
                    i
                    for i, metadata in enumerate(data["metadatas"])
                    if metadata.get("document_id") != document_id
                ]
                print(len(remaining_indices))
                print("data length", len(data), type(data))

                if data.get("documents"):
                    data["documents"] = [data["documents"][i] for i in remaining_indices if data["documents"][i] is not None]
                    print("ddoc done")

                if data.get("embeddings"):
                    data["embeddings"] = [data["embeddings"][i] for i in remaining_indices if data["embeddings"][i] is not None]
                    print("emb done")

                if data.get("metadatas"):
                    data["metadatas"] = [data["metadatas"][i] for i in remaining_indices if data["metadatas"][i] is not None]
                    print("meta done")

                if data.get("ids"):
                    data["ids"] = [data["ids"][i] for i in remaining_indices if data["ids"][i] is not None]
                    print("ids done")

                # Save the updated data back to the pickle file
                with open(self.storage_path, "wb") as f:
                    pickle.dump(data, f)

                print(f"Document(s) with ID {document_id} have been removed from the persisted file.")
                self._load_persisted_data()
        except Exception as e:
            e.__traceback__
            print(f"Error deleting document: {e}")
        
        
    def _keyword_search(self, query: str, top_k: int = 5, user_roles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search using BM25.
        
        Args:
            query (str): The search query
            top_k (int): Number of results to return
            user_roles (list): List of roles to filter results by
            
        Returns:
            list: Ranked search results with documents and metadata
        """
        if not self.bm25:
            return []

        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with non-zero scores
                metadata = self.document_metadata[idx]
                # Apply role filtering
                if not user_roles or metadata.get("role") in user_roles or metadata.get("role") == "all":
                    results.append({
                        "document": self.document_texts[idx],
                        "metadata": metadata,
                        "score": scores[idx]
                    })
        
        return results    
        
    def _is_collection_empty(self):
        """
        Check if the collection is empty.
        """
        return len(self.collection.get()["documents"]) == 0  # Adjust based on your collection structure
        
    def search(self, query: str, top_k: int = 5, user_roles: list = None) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and BM25 keyword search.
        
        Args:
            query (str): The search query
            top_k (int): Number of results to return
            user_roles (list): List of roles to filter results by
            
        Returns:
            list: Combined and ranked search results
        """
        # Get vector search results
        query_embedding = self.model.embed_documents([query])[0]
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Process vector search results
        vector_docs = []
        for doc, meta in zip(vector_results["documents"][0], vector_results["metadatas"][0]):
            if not user_roles or meta.get("role") in user_roles or meta.get("role") == "all" or "all" in meta.get("role"):
                vector_docs.append({
                    "document": doc,
                    "metadata": meta,
                    "source": "vector"
                })

        # Get keyword search results
        keyword_results = self._keyword_search(query, top_k, user_roles)
        keyword_docs = [{**res, "source": "keyword"} for res in keyword_results]

        # Combine results
        all_results = vector_docs + keyword_docs
        
        # Remove duplicates based on document content
        seen_docs = set()
        unique_results = []
        for result in all_results:
            doc_content = result["document"]
            if doc_content not in seen_docs:
                seen_docs.add(doc_content)
                unique_results.append(result)

        # Return top-k unique results
       
        return unique_results[:top_k]
    
    
    
    def list_all_documents(self):
        """
        Fetch and return all documents from the ChromaDB collection along with their metadata.
        """
        # Retrieve all documents in the collection
        try:
            results = self.collection.get()
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            ids = results.get("ids", [])
            
            # Combine the documents, metadata, and IDs for easier viewing
            all_documents = [
                {
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta
                }
                for doc_id, doc, meta in zip(ids, documents, metadatas)
            ]
            
            return all_documents
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []
    
    def clear_collection(self):
        """
        Clear all documents and embeddings from the ChromaDB collection and delete persisted data.
        """
        try:
            # Delete all documents and embeddings from the collection
            all_docs = self.collection.get()["ids"]
            if all_docs:
                self.collection.delete(ids=all_docs)
                print(f"All documents and embeddings cleared from the collection '{self.collection_name}'.")
            
            # Delete the persisted storage file
            if os.path.exists(self.storage_path):
                os.remove(self.storage_path)
                print(f"Persisted data file '{self.storage_path}' has been deleted.")
        except Exception as e:
            print(f"Error clearing collection: {e}")





def get_chroma_hybrid_search(collection_name, storage_path):
    """
    Get the ChromaSearch instance.
    """
    return ChromaSearch(collection_name=collection_name, storage_path=storage_path)
