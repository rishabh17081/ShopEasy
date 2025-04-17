#!/bin/bash

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Failed to install backend dependencies. Exiting."
  exit 1
fi
echo "Backend dependencies installed successfully."

# Install frontend dependencies if needed
echo "Checking frontend dependencies..."
cd ../frontend
echo "Installing react-bootstrap..."
npm install react-bootstrap bootstrap
if [ $? -ne 0 ]; then
  echo "Failed to install react-bootstrap. Exiting."
  exit 1
fi
echo "react-bootstrap installed successfully."

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
  if [ $? -ne 0 ]; then
    echo "Failed to install frontend dependencies. Exiting."
    exit 1
  fi
  echo "Frontend dependencies installed successfully."
else
  echo "Frontend dependencies already installed."
fi

# Return to root directory
cd ..

# Start the servers
echo "Starting servers..."
./start_servers.sh
