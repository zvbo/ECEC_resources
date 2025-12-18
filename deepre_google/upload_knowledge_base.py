import os
import glob
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configuration
# TODO: Update this path to your actual PDF directory
DOCS_DIR = os.getenv("DOCS_DIR", "/path/to/your/literature/folder") 
STORE_NAME = "Child Development Research 0-8yrs"

def upload_to_gemini(client, docs_dir):
    """Uploads files from a directory to a new Gemini File Search Store."""
    
    print(f"Scanning directory: {docs_dir}")
    if not os.path.exists(docs_dir) or docs_dir == "/path/to/your/literature/folder":
        print(f"WARNING: Directory '{docs_dir}' does not exist or is the default placeholder.")
        print("Please set DOCS_DIR in your .env file or update the script.")
        return None

    files_to_upload = []
    # Support common document formats
    extensions = ['*.pdf', '*.csv', '*.doc', '*.docx', '*.txt']
    for ext in extensions:
        files_to_upload.extend(glob.glob(os.path.join(docs_dir, ext)))

    if not files_to_upload:
        print("No matching files found.")
        return None

    print(f"Found {len(files_to_upload)} files.")

    
    # 1. Create the File Search Store first
    print("Creating File Search Store...")
    try:
        # Create the store
        # Using correct client namespace
        store = client.file_search_stores.create(
            config={
                "display_name": STORE_NAME
            }
        )
        print(f"Store created: {store.name}")
    except Exception as e:
        print(f"Store creation failed: {e}")
        return None

    # MIME type mapping
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.csv': 'text/csv',
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.doc': 'application/msword', 
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    print("Uploading and adding files to store...")
    uploaded_count = 0
    for file_path in files_to_upload:
        try:
            print(f"Processing {os.path.basename(file_path)}...")
            
            # Determine MIME type
            _, ext = os.path.splitext(file_path)
            mime_type = MIME_TYPES.get(ext.lower(), 'text/plain')

            # Use the helper method to upload directly to the store
            # This handles file upload + linking
            client.file_search_stores.upload_to_file_search_store(
                file_search_store_name=store.name,
                file=file_path,
                config={
                    'display_name': os.path.basename(file_path),
                    'mime_type': mime_type,
                    # Metadata tagging logic (optimistic)
                    # Note: We rely on the SDK helper passing this config to the file upload
                }
            )
            print(f"Uploaded: {os.path.basename(file_path)}")
            uploaded_count += 1
            
            # Optional: Add delay to avoid rate limits if SDK doesn't handle it
            # time.sleep(0.5) 
            
        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")

    print(f"Successfully added {uploaded_count} files to store {store.name}.")
    
    if uploaded_count == 0:
        print("Warning: No files were added to the store.")
        # We still return the store name as it was created
        
    return store.name

def update_env_file(store_name):
    """Updates the .env file with the new FILE_STORE_NAME."""
    env_path = ".env"
    new_lines = []
    
    # Read existing
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("FILE_STORE_NAME="):
                    new_lines.append(line)
    
    # Add new
    new_lines.append(f"FILE_STORE_NAME={store_name}\n")
    
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print(f"Updated {env_path} with FILE_STORE_NAME.")

if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment.")
    else:
        client = genai.Client(api_key=api_key)
        store_name = upload_to_gemini(client, DOCS_DIR)
        if store_name:
            update_env_file(store_name)
            print(f"\nSUCCESS: Knowledge base ready. Name: {store_name}")
