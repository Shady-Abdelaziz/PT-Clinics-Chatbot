"""
Setup Verification Script
Checks if all dependencies and services are properly configured
"""
import sys
import subprocess
import requests
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def check_python_version():
    """Check Python version"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False


def check_ollama():
    """Check if Ollama is running and models are available"""
    print("\n🤖 Checking Ollama...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            # Check for required models
            required_models = ['deepseek-r1:14b', 'nomic-embed-text']
            for model in required_models:
                if any(model in name for name in model_names):
                    print(f"✅ Model '{model}' is installed")
                else:
                    print(f"❌ Model '{model}' is NOT installed")
                    print(f"   Install with: ollama pull {model}")
            
            return True
        else:
            print("❌ Ollama is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def check_data_files():
    """Check if data files exist"""
    print("\n📁 Checking data files...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ 'data' directory not found")
        return False
    
    required_files = [
        "Doctor_Information_Guide.pdf",
        "Physical_Therapy_Clinic_Guide.pdf",
        "Simple_Clinic_Database.xlsx"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT found")
            all_exist = False
    
    return all_exist


def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n⚙️  Checking .env configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "OLLAMA_BASE_URL",
        "LLM_MODEL",
        "EMBEDDING_MODEL"
    ]
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    all_present = True
    for var in required_vars:
        if f"{var}=" in env_content:
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - NOT found in .env")
            all_present = False
    
    return all_present


def check_qdrant():
    """Check Qdrant connection"""
    print("\n☁️  Checking Qdrant connection...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            print("❌ Qdrant credentials not found in .env")
            return False
        
        from qdrant_client import QdrantClient
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=10)
        collections = client.get_collections()
        
        print("✅ Successfully connected to Qdrant")
        print(f"   Collections: {len(collections.collections)}")
        
        return True
    except Exception as e:
        print(f"❌ Cannot connect to Qdrant: {e}")
        return False


def main():
    """Run all checks"""
    print_header("🏥 Medical Center AI Chatbot - Setup Verification")
    
    checks = [
        ("Python Version", check_python_version),
        ("Ollama Service", check_ollama),
        ("Data Files", check_data_files),
        ("Environment Variables", check_env_file),
        ("Qdrant Connection", check_qdrant)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("📊 Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All checks passed! You're ready to run the application.")
        print("\n📝 Next steps:")
        print("   1. Index documents: python index_documents.py")
        print("   2. Start application: python app.py")
        print("   3. Open browser: http://localhost:5000")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
