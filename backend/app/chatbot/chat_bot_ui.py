#!/usr/bin/env python3
"""
Advanced Java Code QA System with Gradio UI
This script creates a full-featured web interface for the ChromaOllamaQA system using Gradio.
"""

import os
import argparse
import time

import gradio as gr
import tempfile
from typing import List, Dict, Any, Optional
from query_backend import ChromaOllamaQA

# Import the ChromaOllamaQA class from the original script
# Assuming the original code is saved as ChromaOllamaQA.py
class GradioJavaQAInterface:
    """
    Advanced Gradio interface for the Java Code QA system.
    """

    def __init__(self, qa_system: ChromaOllamaQA):
        """
        Initialize the Gradio interface.

        Args:
            qa_system: An instance of ChromaOllamaQA
        """
        self.qa_system = qa_system
        self.chat_history = []

        # Store last retrieved documents for context display
        self.last_retrieved_docs = []

        # Default settings
        self.current_settings = {
            "model": qa_system.model_name,
            "temperature": qa_system.temperature,
            "max_results": qa_system.max_results
        }

    def query_with_context(self, message: str) -> tuple:
        """
        Query the QA system and get both the answer and context.

        Args:
            message: User's question

        Returns:
            Tuple of (answer, context_docs)
        """
        if not message.strip():
            return "Please enter a question.", []

        try:
            # Get relevant context from Chroma
            context_docs = self.qa_system.db.similarity_search(
                message,
                k=self.qa_system.max_results
            )
            self.last_retrieved_docs = context_docs

            # Get the answer
            answer = self.qa_system.query(message)
            return answer, context_docs
        except Exception as e:
            return f"Error: {str(e)}", []

    def respond(self, message: str, history: List) -> str:
        """
        Process user input and generate a response for the chat interface.
        Uses streaming to provide real-time updates to the UI.

        Args:
            message: User's question
            history: Chat history

        Returns:
            Response string (streamed)
        """
        # Use the streaming version from query_backend
        for response_chunk in self.qa_system.query_stream_sync(message):
            yield response_chunk

    def get_context_display(self, message: str) -> str:
        """
        Retrieve and format code context for display.

        Args:
            message: User's question

        Returns:
            Formatted context string
        """
        if not message.strip():
            return "Ask a question to see relevant code context."

        try:
            # Use the similarity search directly to get context
            context_docs = self.qa_system.db.similarity_search(
                message,
                k=self.qa_system.max_results
            )

            # Format the context
            formatted_context = ""
            for i, doc in enumerate(context_docs):
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
                else:
                    filename = doc.metadata.get('filename', 'unknown_file')
                    header = f"FILE: {filename}"

                formatted_context += f"\n## {header}\n```java\n{doc.page_content}\n```\n"

            if not formatted_context:
                return "No relevant code context found."

            return formatted_context
        except Exception as e:
            return f"Error retrieving context: {str(e)}"

    def update_settings(self, model: str, temperature: float, max_results: int) -> str:
        """
        Update QA system settings.

        Args:
            model: Model name
            temperature: Temperature value
            max_results: Max results to retrieve

        Returns:
            Status message
        """
        try:
            # Update settings
            self.qa_system.model_name = model
            self.qa_system.temperature = temperature
            self.qa_system.max_results = max_results

            # Update current settings
            self.current_settings = {
                "model": model,
                "temperature": temperature,
                "max_results": max_results
            }

            return f"Settings updated: Model={model}, Temperature={temperature}, Max Results={max_results}"
        except Exception as e:
            return f"Error updating settings: {str(e)}"

    def create_interface(self) -> gr.Blocks:
        """
        Create the full Gradio interface.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(theme=gr.themes.Soft()) as demo:
            gr.Markdown("# Java Code QA System")
            gr.Markdown(
                "Ask questions about your Java codebase and get answers from CodeLlama, powered by relevant code context from ChromaDB.")

            with gr.Tabs():
                with gr.TabItem("Chat"):
                    with gr.Row():
                        with gr.Column(scale=3):
                            # Chat interface
                            chatbot = gr.ChatInterface(
                                fn=self.respond,
                                examples=[
                                    "What classes are present in the codebase?",
                                    "How does the authentication system work?",
                                    "Explain the main functionality of the ServiceManager class.",
                                    "What is the purpose of the DataProcessor interface?",
                                    "How are exceptions handled in this application?"
                                ]
                            )

                        with gr.Column(scale=2):
                            # Context display - updated when message is sent
                            gr.Markdown("### Code Context")
                            context_display = gr.Markdown("Ask a question to see relevant code context.")

                            # Update context button
                            with gr.Row():
                                context_input = gr.Textbox(label="Message to get context for")
                                context_btn = gr.Button("Get Code Context")

                            context_btn.click(
                                fn=self.get_context_display,
                                inputs=context_input,
                                outputs=context_display
                            )

                with gr.TabItem("Settings"):
                    with gr.Group():
                        gr.Markdown("### Model Settings")
                        model_input = gr.Dropdown(
                            choices=["codellama", "llama2", "mistral", "phi"],
                            label="Ollama Model",
                            value=self.current_settings["model"]
                        )
                        temp_input = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            label="Temperature",
                            value=self.current_settings["temperature"]
                        )
                        results_input = gr.Slider(
                            minimum=1,
                            maximum=20,
                            step=1,
                            label="Max Results from DB",
                            value=self.current_settings["max_results"]
                        )

                        settings_btn = gr.Button("Update Settings")
                        settings_result = gr.Textbox(label="Status")

                        settings_btn.click(
                            fn=self.update_settings,
                            inputs=[model_input, temp_input, results_input],
                            outputs=settings_result
                        )

                with gr.TabItem("About"):
                    gr.Markdown("""
                    ## Java Code QA System

                    This system uses:

                    - **ChromaDB**: Vector database to store code embeddings and enable similarity search
                    - **Ollama**: Local deployment of LLM models for code understanding
                    - **LangChain**: Framework for connecting components
                    - **Gradio**: Web UI framework

                    ### How it works

                    1. Your Java code has been processed and stored in ChromaDB
                    2. When you ask a question, the system finds the most relevant code chunks
                    3. These code chunks are sent as context to the LLM (CodeLlama)
                    4. The LLM generates an answer based on the provided code context

                    ### Tips for good results

                    - Be specific in your questions
                    - Refer to class/method names when possible
                    - Check the "Code Context" panel to see what context the AI is using
                    """)

        return demo


def main():
    """Main function to run the Gradio UI for the QA system."""
    parser = argparse.ArgumentParser(
        description="Advanced Java Code QA System with Gradio UI"
    )
    parser.add_argument(
        "--db-path",
        default="./chroma_db",
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
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a shareable link (useful for remote access)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the Gradio app (default: 7860)"
    )

    args = parser.parse_args()

    # Initialize the QA system
    print(f"Initializing QA system with DB path: {args.db_path}")
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

    # Create and launch the Gradio interface
    interface = GradioJavaQAInterface(qa_system)
    demo = interface.create_interface()
    demo.launch(share=args.share, server_port=args.port)


if __name__ == "__main__":
    main()
