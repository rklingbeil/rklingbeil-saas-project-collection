# test_pinecone_service.py
import numpy as np  # We'll use this to create a dummy vector; ensure numpy is installed.
from .pinecone_service import initialize_pinecone, upsert_vectors, query_vectors

def main():
    # Step 2.1: Initialize the Pinecone index
    index = initialize_pinecone()
    print("Pinecone index initialized.")

    # Step 2.2: Create a dummy vector
    # Here, we assume the embedding dimension is 768 (change if needed).
    dummy_dimension = 768
    # Create a dummy vector with all values 0.1 (for example purposes)
    dummy_vector = [0.1] * dummy_dimension
    print("Dummy vector created with dimension:", dummy_dimension)

    # Step 2.3: Upsert the dummy vector into Pinecone
    # Define a unique vector ID and some sample metadata
    vector_id = "test-vector-1"
    metadata = {"case": "Dummy case for testing", "score": 0.95}
    
    # Upsert expects a list of tuples: (id, vector, metadata)
    upsert_response = upsert_vectors(vectors=[(vector_id, dummy_vector, metadata)])
    print("Upsert response from Pinecone:", upsert_response)

    # Step 2.4: Query Pinecone with the same dummy vector
    # We will request the top 1 match.
    query_response = query_vectors(query_vector=dummy_vector, top_k=1)
    print("Query response from Pinecone:", query_response)

if __name__ == "__main__":
    main()

