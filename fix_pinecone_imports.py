import os
import re

# Directory containing the files
directory = "/opt/saas-case-analysis/SaasDeployClean"

# Files that import pinecone
files_to_fix = [
    "delete_pinecone_index.py",
    "normalize_and_embed.py",
    "test_retrieval.py",
    "test_similarity.py"
]

for filename in files_to_fix:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        # Read the file content
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Replace the import statement
        new_content = re.sub(
            r'import pinecone', 
            'import pinecone_client as pinecone', 
            content
        )
        
        # Write the modified content back to the file
        with open(filepath, 'w') as file:
            file.write(new_content)
        
        print(f"Fixed import in {filename}")
    else:
        print(f"File not found: {filename}")

print("All imports fixed!")
