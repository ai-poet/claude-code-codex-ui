#!/bin/bash

# setup.sh - Frontend container setup script
echo "🚀 Starting frontend container setup..."

# Set environment to development if not already set
export NODE_ENV=${NODE_ENV:-development}

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Build the Next.js application
echo "🔨 Building Next.js application..."
npm run build

# Start the development server
echo "🌟 Starting Next.js development server..."
echo "🎉 Frontend environment is ready!"

# Start the Next.js application
npm run dev