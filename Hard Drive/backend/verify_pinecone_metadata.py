# File: /Users/rick/CaseProject/backend/verify_pinecone_metadata.py

import os
from pinecone import Pinecone, ServerlessSpec

# Retrieve environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  # Example: "us-east-1"
INDEX_NAME = "legal-case-index"  # Your actual index name

if not PINECONE_API_KEY:
    raise Exception("Please set your PINECONE_API_KEY environment variable.")
if not PINECONE_ENV:
    raise Exception("Please set your PINECONE_ENV environment variable.")

# Create a Pinecone client instance
pc = Pinecone(api_key=PINECONE_API_KEY)

# List indexes and verify that INDEX_NAME exists
index_list = pc.list_indexes().names()
print("Available Indexes:", index_list)
if INDEX_NAME not in index_list:
    raise Exception(f"Index '{INDEX_NAME}' not found. Available indexes: {index_list}")

# Connect to the index
index = pc.Index(INDEX_NAME)

# Print index statistics
stats = index.describe_index_stats()
print("Index Statistics:")
print(stats)

# Create a dummy query vector with dimension 768 (matching your index)
dummy_vector = [0.0] * 768

# Query the index with the dummy vector to retrieve up to 5 vectors including metadata
query_response = index.query(
    vector=dummy_vector,
    top_k=5,
    include_metadata=True
)

print("\nQuery Response (Top 5 vectors):")
for match in query_response.get("matches", []):
    print(f"ID: {match.get('id')}")
    metadata = match.get("metadata", {})
    print("Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print("\n")

