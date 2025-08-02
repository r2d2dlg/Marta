#!/bin/bash

echo "🚀 Starting Marta AI development server..."
echo "📍 Working directory: $(pwd)"
echo "🔧 Node version: $(node --version)"
echo "📦 NPM version: $(npm --version)"
echo ""

# Kill any existing processes on port 9002
echo "🧹 Cleaning up existing processes..."
lsof -ti:9002 | xargs kill -9 2>/dev/null || echo "No existing processes on port 9002"

# Clear Next.js cache
echo "🗑️  Clearing Next.js cache..."
rm -rf .next

# Set up environment
export NODE_ENV=development
export NODE_OPTIONS="--max-old-space-size=4096"

echo "🌍 Environment variables loaded"
echo "🎯 Starting Next.js development server on port 9002..."
echo ""

# Start with timeout and proper signal handling
timeout 300s npm run dev || {
    echo "❌ Dev server failed to start within 5 minutes"
    echo "💡 Try running manually with: npx next dev -p 9002"
    exit 1
}