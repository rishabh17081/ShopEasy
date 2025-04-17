# E-commerce Chatbot with Anthropic Claude

This project integrates Anthropic Claude with the e-commerce platform, providing an AI assistant that can help users with various tasks including creating invoices, listing products, and more.

## Features

- AI-powered chatbot using Anthropic Claude
- Integration with PayPal API for e-commerce operations
- Tool-using capabilities for performing actions
- User-friendly chat interface

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Node.js and npm
- Anthropic API key

### Installation

1. Clone the repository
2. Add your Anthropic API key to `backend/.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
3. Run the setup script:
   ```
   ./setup_and_start.sh
   ```

This script will:
- Install backend dependencies
- Install frontend dependencies including react-bootstrap
- Start both the backend and frontend servers

## Usage

1. Navigate to http://localhost:3000/chatbot in your browser
2. Start chatting with the AI assistant
3. Ask about products, orders, or payment options
4. The assistant can perform actions like creating invoices or listing products

## Architecture

### Backend

- Flask API with a dedicated chatbot route
- AnthropicToolsHandler class for managing interactions with Claude
- Integration with PayPal API functions

### Frontend

- React components for the chatbot interface
- Support for displaying:
  - Regular chat messages
  - Tool calls (when Claude uses tools)
  - Tool results (responses from tools)
  - Follow-up responses

## Troubleshooting

If you encounter any issues:

1. Make sure your Anthropic API key is correctly set in `backend/.env`
2. Check that all dependencies are installed:
   ```
   cd backend && pip3 install -r requirements.txt
   cd frontend && npm install && npm install react-bootstrap bootstrap
   ```
3. Ensure ports 3000 (frontend) and 5000 (backend) are available

## License

This project is licensed under the MIT License - see the LICENSE file for details.
