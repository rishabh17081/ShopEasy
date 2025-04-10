#!/usr/bin/env python3
"""
Java Code QA System using Chroma DB + Ollama
This script retrieves relevant context from a Chroma vector DB and uses Ollama with CodeLlama
to generate answers to user queries about a Java codebase.
"""

import os
import argparse
import ollama
import time
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

# Import Chroma and LangChain components
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
# Import the custom SeldonOpenAIEmbeddings
from openai_seldon_integration import SeldonOpenAIEmbeddings

console = Console()


class ChromaOllamaQA:
    """
    QA system for Java codebases using Chroma DB and Ollama's CodeLlama.
    """

    def __init__(
            self,
            chroma_db_path: str = './chroma_db',
            collection_name: str = "java_code_chunks",
            model_name: str = "codellama",
            temperature: float = 0.1,
            max_context_length: int = 80000,
            max_results: int = 2,
            # Seldon embedding parameters
            host_url: str = None,
            seldon_model_name: str = None,
            api_key: str = "EMPTY"
    ):
        """
        Initialize the Chroma + Ollama QA system.

        Args:
            chroma_db_path: Path to the Chroma DB directory
            collection_name: Name of the Chroma collection
            model_name: Ollama model to use (default: codellama)
            temperature: Generation temperature (lower = more deterministic)
            embedding_model: HuggingFace model for query embeddings
            max_context_length: Maximum context length to send to CodeLlama
            max_results: Maximum number of results to retrieve from Chroma
        """
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.model_name = model_name
        self.temperature = temperature
        self.max_context_length = max_context_length
        self.max_results = max_results

        # Seldon embedding parameters
        self.host_url = host_url
        self.seldon_model_name = seldon_model_name
        self.api_key = api_key

        # Connect to the Chroma DB
        self._connect_to_chroma()

        # Check if Ollama is available and pull model if needed
        self._check_ollama()

    def _connect_to_chroma(self):
        """Connect to the Chroma vector database."""
        console.print(f"[bold blue]Connecting to Chroma DB:[/] {self.chroma_db_path}")

        if not os.path.exists(self.chroma_db_path):
            console.print(f"[bold red]Error:[/] Chroma DB directory not found at {self.chroma_db_path}")
            raise FileNotFoundError(f"Chroma DB directory not found: {self.chroma_db_path}")

        try:
            # Initialize the embedding model for queries

            if self.host_url and self.seldon_model_name:
                console.print(f"[bold blue]Using Seldon embeddings:[/] {self.seldon_model_name}")
                # Initialize SeldonOpenAIEmbeddings (identical to what's used during indexing)
                self.embeddings = SeldonOpenAIEmbeddings(
                    host_url=self.host_url,
                    model_name=self.seldon_model_name,
                    api_key=self.api_key
                )
            else:
                console.print("[bold yellow]Warning:[/] No Seldon embeddings configured - using default embeddings")
                console.print("[bold yellow]This might cause embedding inconsistency with your indexed data[/]")
                # Fall back to using a local model with matching dimension
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            # Connect to Chroma
            self.db = Chroma(
                persist_directory=self.chroma_db_path,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )

            # Get collection info
            collection_data = self.db.get()
            collection_size = len(collection_data.get('ids', [])) if collection_data else 0

            console.print(f"[green]✓[/] Connected to Chroma DB collection: '{self.collection_name}'")
            console.print(f"  - Documents in collection: {collection_size}")

        except Exception as e:
            console.print(f"[bold red]Error connecting to Chroma:[/] {str(e)}")
            raise

    def _check_ollama(self):
        """Check if Ollama is available and the model is installed."""
        try:
            models = ollama.list()
            model_names = [model.get('model').split(':')[0] for model in models.get('models', [])]

            if self.model_name not in model_names:
                console.print(f"[yellow]Warning:[/] Model '{self.model_name}' not found in Ollama.")
                console.print(f"Available models: {', '.join(model_names)}")
                console.print(f"Pulling the model '{self.model_name}'...")

                # Pull the model
                with console.status(f"[bold green]Pulling {self.model_name}...[/]"):
                    ollama.pull(self.model_name)

                console.print(f"[green]✓[/] Model '{self.model_name}' pulled successfully.")
            else:
                console.print(f"[green]✓[/] Using Ollama model: {self.model_name}")

        except Exception as e:
            console.print(f"[bold red]Error connecting to Ollama:[/] {str(e)}")
            console.print("Make sure Ollama is running. You can start it with 'ollama serve'")
            raise

    def query(self, query_text: str) -> str:
        """
        Query the Java codebase using CodeLlama.

        Args:
            query_text: The user's query about the codebase

        Returns:
            Generated answer from CodeLlama
        """
        console.print(f"\n[bold blue]Query:[/] {query_text}")

        # Step 1: Retrieve relevant context from Chroma
        with console.status("[bold green]Retrieving relevant code chunks...[/]"):
            context_docs = self.db.similarity_search(
                query_text,
                k=self.max_results
            )

        console.print(f"[green]✓[/] Retrieved {len(context_docs)} relevant code chunks")

        # Step 2: Format context for the LLM
        context_text = self._format_context(context_docs)

        # Step 3: Create the prompt for CodeLlama
        prompt = self._create_prompt(query_text, context_text)

        # Step 4: Call Ollama API to generate answer
        console.print("[bold green]Generating answer with CodeLlama...[/]")

        # Stream the response
        response_text = ""
        try:
            stream = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": self.temperature,
                    "num_ctx": 16384
                }
            )

            # Initialize output
            console.print("\n[bold cyan]Answer:[/]")

            # Handle streaming response
            for chunk in stream:
                chunk_text = chunk.get('response', '')
                response_text += chunk_text
                console.print(chunk_text, end='')

            console.print("\n")

        except Exception as e:
            console.print(f"[bold red]Error generating response:[/] {str(e)}")
            response_text = f"Error generating response: {str(e)}"

        return response_text

    # Add this to backend_query.py
    def query_stream_sync(self, query_text: str):
        """
        Synchronous version of query_stream that returns a generator.

        Args:
            query_text: The user's query about the codebase

        Returns:
            Generator yielding chunks of the response
        """
        # (Same code as query_stream but without the async/await)
        console.print(f"\n[bold blue]Query:[/] {query_text}")

        # Step 1: Retrieve relevant context from Chroma
        with console.status("[bold green]Retrieving relevant code chunks...[/]"):
            context_docs = self.db.similarity_search(
                query_text,
                k=self.max_results
            )

        console.print(f"[green]✓[/] Retrieved {len(context_docs)} relevant code chunks")

        # Step 2: Format context for the LLM
        context_text = self._format_context(context_docs)

        # Step 3: Create the prompt for CodeLlama
        prompt = self._create_prompt(query_text, context_text)

        # Step 4: Call Ollama API to generate answer
        console.print("[bold green]Generating answer with CodeLlama...[/]")

        # Stream the response
        try:
            stream = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": self.temperature,
                    "num_ctx": 16384
                }
            )

            # Initialize output for console
            console.print("\n[bold cyan]Answer:[/]")

            # Accumulate response for UI updates
            response_so_far = ""

            # Handle streaming response
            for chunk in stream:
                chunk_text = chunk.get('response', '')
                response_so_far += chunk_text
                yield response_so_far  # Yield accumulated response

            console.print("\n")

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            console.print(f"[bold red]{error_msg}[/]")
            yield error_msg

    async def query_stream(self, query_text: str):
        """
        Query the Java codebase using CodeLlama and stream the response.

        Args:
            query_text: The user's query about the codebase

        Yields:
            Chunks of the generated answer as they become available
        """
        console.print(f"\n[bold blue]Query:[/] {query_text}")

        # Step 1: Retrieve relevant context from Chroma
        with console.status("[bold green]Retrieving relevant code chunks...[/]"):
            context_docs = self.db.similarity_search(
                query_text,
                k=self.max_results
            )

        console.print(f"[green]✓[/] Retrieved {len(context_docs)} relevant code chunks")

        # Step 2: Format context for the LLM
        context_text = self._format_context(context_docs)

        # Step 3: Create the prompt for CodeLlama
        prompt = self._create_prompt(query_text, context_text)

        # Step 4: Call Ollama API to generate answer
        console.print("[bold green]Generating answer with CodeLlama...[/]")

        # Stream the response
        try:
            stream = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": self.temperature,
                    "num_ctx": 16384
                }
            )

            # Initialize output for console
            console.print("\n[bold cyan]Answer:[/]")

            # Handle streaming response
            for chunk in stream:
                chunk_text = chunk.get('response', '')
                console.print(chunk_text, end='')
                yield chunk_text  # Yield each chunk to be sent to the UI

            console.print("\n")

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            console.print(f"[bold red]{error_msg}[/]")
            yield error_msg

    def _format_context(self, docs: List[Document]) -> str:
        """
        Format the retrieved documents into a context string for the LLM.

        Args:
            docs: List of retrieved Document objects

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, doc in enumerate(docs):
            # Format based on document type
            doc_type = doc.metadata.get('type', 'unknown')
            doc_name = doc.metadata.get('name', 'unnamed')

            if doc_type == 'class':
                header = f"CLASS: {doc_name}"
            elif doc_type == 'method':
                class_name = doc.metadata.get('class', 'unknown_class')
                header = f"METHOD: {class_name}.{doc_name}()"
            elif doc_type == 'field':
                class_name = doc.metadata.get('class', 'unknown_class')
                header = f"FIELD: {class_name}.{doc_name}"
            elif doc_type == 'package':
                header = f"PACKAGE: {doc_name}"
            elif doc_type == 'imports':
                header = "IMPORTS"
            else:
                filename = doc.metadata.get('filename', 'unknown_file')
                header = f"FILE: {filename}"

            # Add the document with its header
            context_parts.append(f"--- {header} ---\n{doc.page_content}\n")

        # Combine all parts and limit to max context length
        full_context = "\n".join(context_parts)
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "...[truncated]"

        return full_context

    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for CodeLlama based on the query and context.

        Args:
            query: User's query
            context: Retrieved context from Chroma DB

        Returns:
            Formatted prompt
        """
        return f"""I'm going to provide you with relevant Java code snippets from a codebase, and then ask you a question about it.
Please analyze the code thoroughly and answer the question based only on the provided context.

JAVA CODE CONTEXT:
{context}

USER QUESTION: 
{query}

Please provide a comprehensive answer to the question. If the provided code context doesn't contain enough information to answer fully, please mention that in your response.
"""

    def search_by_metadata(self, metadata_dict: Dict[str, Any]) -> List[Document]:
        """
        Search for documents by metadata.

        Args:
            metadata_dict: Dictionary of metadata key-value pairs

        Returns:
            List of matching documents
        """
        filter_dict = {"$and": []}
        for key, value in metadata_dict.items():
            filter_dict["$and"].append({key: value})

        results = self.db.get(where=filter_dict)

        documents = []
        if results['documents'] and results['metadatas']:
            for i in range(len(results['documents'])):
                doc = Document(
                    page_content=results['documents'][i],
                    metadata=results['metadatas'][i]
                )
                documents.append(doc)

        return documents

    def find_class(self, class_name: str) -> List[Document]:
        """
        Find a specific class by name.

        Args:
            class_name: Name of the class to find

        Returns:
            List of matching class documents
        """
        return self.search_by_metadata({"type": "class", "name": class_name})

    def find_method(self, method_name: str, class_name: Optional[str] = None) -> List[Document]:
        """
        Find a specific method by name and optional class name.

        Args:
            method_name: Name of the method to find
            class_name: Optional class name to filter by

        Returns:
            List of matching method documents
        """
        metadata = {"type": "method", "name": method_name}
        if class_name:
            metadata["class"] = class_name

        return self.search_by_metadata(metadata)


def main():
    """Main function to run the QA system from the command line."""
    parser = argparse.ArgumentParser(
        description="Query a Java codebase using Chroma DB and Ollama"
    )
    parser.add_argument(
        "--db-path", default= "./chroma_db",
        required=False,
        help="Path to the Chroma DB directory"
    )
    parser.add_argument(
        "--collection",
        default="java_code_chunks",
        help="Name of the Chroma collection (default: java_code_chunks)"
    )
    parser.add_argument(
        "--model",
        default="codellama",
        help="Ollama model to use (default: codellama)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Temperature for generation (default: 0.1)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of chunks to retrieve (default: 10)"
    )
    parser.add_argument(
        "--host-url",
        help="Host URL for Seldon deployment (for embedding consistency)"
    )
    parser.add_argument(
        "--seldon-model",
        help="Model name for Seldon embedding API"
    )
    parser.add_argument(
        "--api-key",
        default="EMPTY",
        help="API key for Seldon (default: EMPTY)"
    )

    args = parser.parse_args()

    # Initialize the QA system
    qa_system = ChromaOllamaQA(
        chroma_db_path=args.db_path,
        collection_name=args.collection,
        model_name=args.model,
        temperature=args.temperature,
        max_results=args.max_results,
        host_url=args.host_url,
        seldon_model_name=args.seldon_model,
        api_key=args.api_key
    )

    console.print(Panel.fit(
        "[bold green]Java Code QA System[/]\n"
        "Ask questions about your Java codebase. Type 'exit' to quit.",
        title="Chroma DB + Ollama"
    ))

    # Interactive query loop
    while True:
        try:
            query = input("\nYour question (type 'exit' to quit): ")

            if query.lower() in ('exit', 'quit', 'q'):
                break

            if not query.strip():
                continue

            # Process the query
            answer = qa_system.query(query)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user.[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/] {str(e)}")

    console.print("[bold blue]Thank you for using the Java Code QA System![/]")


if __name__ == "__main__":
    main()
