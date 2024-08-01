"""
Take a string and embed it for the qdrant search
"""
import logging
from typing import List
import os
import openai
from dataclasses import dataclass

# def get_query_embedding(user_query: str, deployment_name: str="random") -> List[float]:
#     # Placeholder function since the original code uses OpenAI's API.
#     # Replace this with your embedding logic.
#     return [0.0] * 1536

# OPENAI VARS
OPENAI_API_TYPE = os.environ.get('OPENAI_API_TYPE') or 'azure'
OPENAI_API_VERSION = os.environ.get('OPENAI_API_VERSION') or '2023-08-01-preview'

OPENAI_API_BASE_EMBEDDING = os.environ.get('OPENAI_API_BASE_EMBEDDING') or 'https://aoai-aur-foundationmodel-aue-prod.openai.azure.com/'
OPENAI_KEY_EMBEDDING = os.environ.get('OPENAI_KEY_EMBEDDING') or '5a466142287f4366820a5f1dd456a83a'
EMBEDDING_DEPLOYMENT_NAME = os.environ.get('EMBEDDING_DEPLOYMENT_NAME') or 'embeddings'
OPENAI_EMBEDDING_VERSION = os.environ.get('OPENAI_EMBEDDING_VERSION') or '2023-08-01-preview'

@dataclass
class OpenAIConfig:
    """
    All of the OpenAI variables
    """
    
    # Global API vars
    api_type: str
    api_version: str
    api_version_embeddings: str

    # Embedding vars
    api_base_embedding: str
    api_key_embedding: str
    embedding_deployment_name: str

    # Agent vars
    MAX_SOURCE_TOKENS: int = 10_000
    N_SOURCES: int = 10_000
    AGENT_TEMPERATURE: float = 0.0

openai_config = OpenAIConfig(
    # Global vars
    api_type = OPENAI_API_TYPE,
    api_version = OPENAI_API_VERSION,
    api_version_embeddings = OPENAI_EMBEDDING_VERSION,

    # Embedding vars
    api_base_embedding = OPENAI_API_BASE_EMBEDDING,
    api_key_embedding = OPENAI_KEY_EMBEDDING,
    embedding_deployment_name = EMBEDDING_DEPLOYMENT_NAME,
    # Agent vars
    MAX_SOURCE_TOKENS = 10_000,
    N_SOURCES = 5,
    AGENT_TEMPERATURE = 0.0,
)

def get_query_embedding(
        user_query: str,
        deployment_name: str = openai_config.embedding_deployment_name
    ) -> List[float]:
    """Take a query and embed it using a model."""

    openai_response = openai.Embedding.create(
        input=[user_query],
        engine=deployment_name,
        api_base = openai_config.api_base_embedding,
        api_key = openai_config.api_key_embedding,
        api_version = openai_config.api_version_embeddings,
        api_type = openai_config.api_type
    )

    logging.info("** Response received from OpenAI::")
    logging.info("** - model: %s", openai_response['model'])
    logging.info("** - prompt tokens: %s", openai_response['usage']['prompt_tokens'])
    logging.info("** - total tokens: %s", openai_response['usage']['total_tokens'])

    # return vector
    return openai_response["data"][0]["embedding"]

if __name__ == "__main__":
    from scipy.spatial.distance import cosine

    query = "What is the best way to learn Python?"
    query_embedding = get_query_embedding(query)

    # # Test cosine similarity between closed sentences
    source = "The best way to learn Python is to practice writing code."
    source_embedding = get_query_embedding(source)
    similarity = 1 - cosine(query_embedding, source_embedding)
    print(f"Similarity between closed sentences: {similarity}")

    # Test cosine similarity between closed sentences
    distant_source = "Bad weather today!"
    distant_source_embedding = get_query_embedding(distant_source)
    similarity = 1 - cosine(query_embedding, distant_source_embedding)
    print(f"Similarity between distance sentences: {similarity}")


