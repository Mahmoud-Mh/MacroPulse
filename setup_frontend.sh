#!/bin/bash

# Create frontend directory
mkdir -p frontend

# Navigate to frontend directory
cd frontend

# Initialize a new Vite project with React
npm create vite@latest . -- --template react-ts

# Install additional dependencies
npm install

# Install required packages
npm install @mui/material @emotion/react @emotion/styled  # Material-UI for components
npm install @mui/icons-material  # Material Icons
npm install react-query  # For API data fetching
npm install react-router-dom  # For routing
npm install recharts  # For charts
npm install axios  # For HTTP requests
npm install @tanstack/react-query  # For data fetching and caching
npm install date-fns  # For date formatting 