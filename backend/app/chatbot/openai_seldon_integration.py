"""
Integration module for Seldon OpenAI embeddings.
This module provides a wrapper for using Seldon's API with OpenAI-compatible interface.
"""

from typing import List, Optional
from langchain.embeddings.base import Embeddings
import requests


class SeldonOpenAIEmbeddings(Embeddings):
    """
    A class for generating embeddings using Seldon's API with OpenAI-compatible interface.
    """

    def __init__(
            self,
            host_url: str,
            model_name: str,
            api_key: str = "EMPTY",
            timeout: int = 60
    ):
        """
        Initialize the Seldon OpenAI embeddings wrapper.

        Args:
            host_url: The URL of the Seldon deployment
            model_name: The name of the model to use
            api_key: API key for authentication (if required)
            timeout: Request timeout in seconds
        """
        self.host_url = host_url
        self.model_name = model_name
        self.api_key = api_key
        self.timeout = timeout

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embeddings, one for each text
        """
        if not texts:
            return []

        # Prepare the request payload
        payload = {
            "input": texts,
            "model": self.model_name
        }

        # Prepare headers
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key and self.api_key != "EMPTY":
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Make the request to the Seldon API
        try:
            response = requests.post(
                f"{self.host_url}/v1/embeddings",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract embeddings from the response
            embeddings = [item["embedding"] for item in result["data"]]
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Return zero embeddings as fallback
            return [[0.0] * 768] * len(texts)  # Assuming 768-dimensional embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.

        Args:
            texts: List of documents to generate embeddings for

        Returns:
            List of embeddings, one for each document
        """
        return self._embed_texts(texts)

    def embed_query(self, text: str) -> List[float]:
        """
        Generate an embedding for a query text.

        Args:
            text: Query text to generate an embedding for

        Returns:
            Embedding for the query text
        """
        embeddings = self._embed_texts([text])
        return embeddings[0] if embeddings else [0.0] * 768  # Assuming 768-dimensional embeddings
