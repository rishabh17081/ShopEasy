#!/usr/bin/env python3
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import gradio as gr
    print(f"Gradio imported successfully. Version: {gr.__version__}")
except ImportError as e:
    print(f"Failed to import gradio: {e}")
    print("Checking sys.path:")
    for path in sys.path:
        print(f"  - {path}")
