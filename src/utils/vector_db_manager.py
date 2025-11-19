"""
Vector Database Manager
Handles document indexing and retrieval using OpenRouter LLM and Ollama embeddings with Qdrant
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2
import uuid


class OllamaEmbeddings:
    """Ollama embeddings wrapper"""
    
    def __init__(self, base_url: str, model: str):
        """Initialize Ollama embeddings"""
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.embed_url = f"{self.base_url}/api/embeddings"
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        try:
            response = requests.post(
                self.embed_url,
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise


class VectorDBManager:
    """Manages vector database operations"""
    
    def __init__(
        self,
        qdrant_url: str,
        qdrant_api_key: str,
        collection_name: str,
        ollama_base_url: str,
        embedding_model: str
    ):
        """Initialize Vector DB Manager"""
        self.collection_name = collection_name
        
        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(ollama_base_url, embedding_model)
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=300
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Get embedding dimension
        self.embedding_dim = len(self.embeddings.embed_query("test"))
    
    def recreate_collection(self):
        """Recreate the Qdrant collection"""
        try:
            # Delete existing collection if it exists
            try:
                self.qdrant_client.delete_collection(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except:
                pass
            
            # Create new collection
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error recreating collection: {e}")
            raise
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                            text += "\n"
                    except Exception as e:
                        print(f"Warning: Failed to extract text from page {page_num + 1}: {e}")
                        continue
            
            if not text.strip():
                raise Exception("No text could be extracted from the PDF")
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    def process_pdf_file(self, file_path: Path) -> List[Dict]:
        """Process PDF file into chunks"""
        try:
            print(f"Processing PDF: {file_path.name}")
            
            # Extract text
            pdf_text = self.extract_text_from_pdf(file_path)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(pdf_text)
            
            # Create documents
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'text': chunk,
                    'metadata': {
                        'filename': file_path.name,
                        'source_type': 'pdf',
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                })
            
            print(f"✅ PDF {file_path.name}: Created {len(documents)} chunks")
            return documents
        except Exception as e:
            print(f"Error processing PDF {file_path.name}: {e}")
            return []
    
    def process_excel_file(self, file_path: Path) -> List[Dict]:
        """Process Excel file into chunks"""
        try:
            print(f"Processing Excel: {file_path.name}")
            
            documents = []
            excel_file = pd.ExcelFile(file_path)
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert sheet to text
                sheet_text = f"Data from sheet: {sheet_name}\n\n"
                sheet_text += df.to_string(index=False)
                
                # Split into chunks
                chunks = self.text_splitter.split_text(sheet_text)
                
                for i, chunk in enumerate(chunks):
                    documents.append({
                        'text': chunk,
                        'metadata': {
                            'filename': file_path.name,
                            'source_type': 'excel',
                            'sheet_name': sheet_name,
                            'chunk_index': i,
                            'total_chunks': len(chunks)
                        }
                    })
            
            print(f"✅ Excel {file_path.name}: Created {len(documents)} chunks")
            return documents
        except Exception as e:
            print(f"Error processing Excel {file_path.name}: {e}")
            return []
    
    def upload_documents(self, documents: List[Dict]):
        """Upload documents to Qdrant"""
        if not documents:
            print("No documents to upload")
            return
        
        try:
            print(f"Generating embeddings for {len(documents)} documents...")
            
            # Extract texts
            texts = [doc['text'] for doc in documents]
            
            # Generate embeddings in batches
            batch_size = 10
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.embeddings.embed_documents(batch_texts)
                all_embeddings.extend(batch_embeddings)
                print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            # Upload to Qdrant
            print("Uploading to Qdrant...")
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, all_embeddings)):
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            'text': doc['text'],
                            **doc['metadata']
                        }
                    )
                )
            
            # Upload in batches
            for i in range(0, len(points), batch_size):
                batch_points = points[i:i + batch_size]
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=batch_points
                )
                print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
            print(f"✅ Successfully uploaded {len(documents)} documents!")
        except Exception as e:
            print(f"Error uploading documents: {e}")
            raise
    
    def search(self, query: str, limit: int = 5, score_threshold: float = 0.3) -> List[Dict]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'text': result.payload['text'],
                    'score': result.score,
                    'metadata': {k: v for k, v in result.payload.items() if k != 'text'}
                })
            
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def index_all_files(self, pdf_files: List[Path], excel_files: List[Path]):
        """Index all PDF and Excel files"""
        try:
            # Recreate collection
            self.recreate_collection()
            
            # Process all files
            all_documents = []
            
            # Process PDFs
            for pdf_file in pdf_files:
                documents = self.process_pdf_file(pdf_file)
                all_documents.extend(documents)
            
            # Process Excel files
            for excel_file in excel_files:
                documents = self.process_excel_file(excel_file)
                all_documents.extend(documents)
            
            # Upload all documents
            if all_documents:
                self.upload_documents(all_documents)
                print(f"✅ Successfully indexed {len(all_documents)} documents from {len(pdf_files) + len(excel_files)} files!")
            else:
                print("No documents to index")
        except Exception as e:
            print(f"Error indexing files: {e}")
            raise
