"""
Index Documents Script
Indexes PDF and Excel files into the Qdrant vector database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils import config, VectorDBManager


def main():
    """Main function to index all documents"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Medical Center AI - Document Indexing                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize vector DB manager
    print("🔧 Initializing Vector DB Manager...")
    vector_manager = VectorDBManager(
        qdrant_url=config.QDRANT_URL,
        qdrant_api_key=config.QDRANT_API_KEY,
        collection_name=config.COLLECTION_NAME,
        ollama_base_url=config.OLLAMA_BASE_URL,
        embedding_model=config.EMBEDDING_MODEL
    )
    print(f"✅ Connected to Qdrant: {config.COLLECTION_NAME}")
    print(f"✅ Using Ollama embeddings: {config.EMBEDDING_MODEL}")
    
    # Define file paths
    data_dir = project_root / "data"
    
    # PDF files
    pdf_files = [
        data_dir / "Doctor_Information_Guide.pdf",
        data_dir / "Physical_Therapy_Clinic_Guide.pdf"
    ]
    
    # Excel files
    excel_files = [
        data_dir / "Simple_Clinic_Database.xlsx"
    ]
    
    # Check if files exist
    print("\n📁 Checking files...")
    missing_files = []
    
    for file in pdf_files + excel_files:
        if file.exists():
            print(f"✅ Found: {file.name}")
        else:
            print(f"❌ Missing: {file.name}")
            missing_files.append(str(file))
    
    if missing_files:
        print(f"\n⚠️  Warning: {len(missing_files)} file(s) not found!")
        print("Please ensure all files are in the 'data' directory:")
        for file in missing_files:
            print(f"  - {file}")
        
        response = input("\nContinue with available files? (y/n): ")
        if response.lower() != 'y':
            print("Indexing cancelled.")
            return
    
    # Filter to only existing files
    pdf_files = [f for f in pdf_files if f.exists()]
    excel_files = [f for f in excel_files if f.exists()]
    
    if not pdf_files and not excel_files:
        print("\n❌ No files to index!")
        return
    
    print(f"\n📊 Files to index:")
    print(f"  - PDF files: {len(pdf_files)}")
    print(f"  - Excel files: {len(excel_files)}")
    
    # Confirm before proceeding
    print("\n⚠️  This will recreate the Qdrant collection and index all files.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Indexing cancelled.")
        return
    
    # Index all files
    print("\n🚀 Starting indexing process...\n")
    try:
        vector_manager.index_all_files(pdf_files, excel_files)
        print("\n✅ Indexing completed successfully!")
        print(f"📦 Collection: {config.COLLECTION_NAME}")
        print(f"🌐 Qdrant URL: {config.QDRANT_URL}")
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        return
    
    print("\n" + "="*60)
    print("You can now run the chatbot application!")
    print("Run: python app.py")
    print("="*60)


if __name__ == "__main__":
    main()
