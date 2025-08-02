#!/bin/bash

echo "=== Debug npm run dev ==="
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "Current directory: $(pwd)"
echo "Port 9002 status:"
lsof -i :9002 || echo "Port 9002 is free"
echo ""

echo "=== Environment Variables ==="
echo "NODE_ENV: $NODE_ENV"
echo "NEXTAUTH_URL: $NEXTAUTH_URL"
echo "GOOGLE_CLIENT_ID length: ${#GOOGLE_CLIENT_ID}"
echo ""

echo "=== Starting Next.js dev server with verbose output ==="
echo "Command: npm run dev"
echo "Time: $(date)"
echo ""

# Run with timeout and capture exit code
timeout 10s npm run dev &
DEV_PID=$!
sleep 2

if kill -0 $DEV_PID 2>/dev/null; then
    echo "✅ Dev server is running (PID: $DEV_PID)"
    echo "Visit: http://localhost:9002"
    kill $DEV_PID
else
    echo "❌ Dev server exited immediately"
    echo "Exit code: $?"
fi

echo ""
echo "=== Checking for common issues ==="
echo "TypeScript check:"
npm run typecheck 2>&1 | head -5

echo ""
echo "Next.js cache:"
ls -la .next/ | head -5