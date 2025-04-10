#!/bin/bash

# Start the backend server
echo "Starting backend server..."
cd backend
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f2)
echo "Using Anthropic API key: $ANTHROPIC_API_KEY"

# Check if the API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Error: ANTHROPIC_API_KEY is not set in .env file"
  echo "Please add your Anthropic API key to the .env file"
  exit 1
fi

# Start the backend server
python3 run.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start the frontend server
echo "Starting frontend server..."
cd ../frontend

# Check if node_modules directory exists
if [ ! -d "node_modules" ]; then
  echo "Error: node_modules directory not found"
  echo "Please run 'npm install' in the frontend directory"
  kill $BACKEND_PID
  exit 1
fi

# Check if react-bootstrap is installed
if [ ! -d "node_modules/react-bootstrap" ]; then
  echo "Error: react-bootstrap not found"
  echo "Please run 'npm install react-bootstrap bootstrap' in the frontend directory"
  kill $BACKEND_PID
  exit 1
fi

# Start the frontend server
npm start &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

# Function to handle script termination
cleanup() {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

# Keep script running
echo "Both servers are running. Press Ctrl+C to stop."
echo "You can access the chatbot at http://localhost:3000/chatbot"
wait
