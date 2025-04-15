# This is a compatibility module to handle the pinecone import issue
import pinecone as _pinecone

# Re-export everything from the original pinecone module
from pinecone import *
