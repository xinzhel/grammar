import requests

QDRANT_ENDPOINT = "http://localhost:6333"  # Adjust this to your Qdrant server address

def create_collection(collection_name):
    url = f"{QDRANT_ENDPOINT}/collections/{collection_name}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "vector_size": 512,
        "distance": "Cosine"
        
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.json()


def insert_documents(collection_name, documents):
    url = f"{QDRANT_ENDPOINT}/collections/{collection_name}/points"
    payload = {
            "points": [
                {
                    "id": idx,  # Assigning a unique ID to each document
                    "vector": [0] * 512,
                    "payload": {"text": doc}
                } 
                for idx, doc in enumerate(documents, start=1)  # Starting IDs from 1
            ]
        }
    response = requests.put(url, json=payload)
    return response.json()

# Example usage:
collection_name = "my_collection"

documents = ["Document 1 content", "Document 2 content", "Document 3 content"]
print(create_collection(collection_name))
print(insert_documents(collection_name, documents))

def delete_collection(collection_name):
    url = f"{QDRANT_ENDPOINT}/collections/{collection_name}"
    response = requests.delete(url)
    return response.json()

