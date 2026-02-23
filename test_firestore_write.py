#!/usr/bin/env python3
"""Test Firestore write permissions."""
import os
from dotenv import load_dotenv
from google.cloud import firestore

# Load environment variables
load_dotenv()

# Get configuration
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
database_id = os.getenv('FIRESTORE_DATABASE_ID', '(default)')

print(f"Project ID: {project_id}")
print(f"Database ID: {database_id}")

try:
    # Initialize Firestore client
    db = firestore.Client(project=project_id, database=database_id)
    print(f"✅ Firestore client initialized")
    
    # Try to write a test document
    test_collection = db.collection('test_collection')
    doc_ref = test_collection.document('test_doc')
    
    doc_ref.set({
        'message': 'Hello from test script!',
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    print(f"✅ Successfully wrote test document!")
    
    # Try to read it back
    doc = doc_ref.get()
    if doc.exists:
        print(f"✅ Successfully read test document: {doc.to_dict()}")
    else:
        print(f"❌ Document doesn't exist")
    
    # Clean up
    doc_ref.delete()
    print(f"✅ Test document deleted")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
