#!/usr/bin/env node

console.log('Starting Next.js test...');
console.log('Node version:', process.version);
console.log('Platform:', process.platform);
console.log('CWD:', process.cwd());

try {
  console.log('Loading Next.js...');
  const { createServer } = require('http');
  const { parse } = require('url');
  const next = require('next');
  
  const dev = process.env.NODE_ENV !== 'production';
  const hostname = 'localhost';
  const port = 9002;
  
  console.log('Creating Next.js app...');
  const app = next({ dev, hostname, port });
  const handle = app.getRequestHandler();
  
  console.log('Preparing Next.js...');
  app.prepare().then(() => {
    console.log('Next.js prepared successfully!');
    
    createServer(async (req, res) => {
      try {
        const parsedUrl = parse(req.url, true);
        await handle(req, res, parsedUrl);
      } catch (err) {
        console.error('Error handling request:', err);
        res.statusCode = 500;
        res.end('Internal Server Error');
      }
    })
    .once('error', (err) => {
      console.error('Server error:', err);
      process.exit(1);
    })
    .listen(port, () => {
      console.log(`> Ready on http://${hostname}:${port}`);
    });
  }).catch((err) => {
    console.error('Failed to prepare Next.js:', err);
    process.exit(1);
  });
  
} catch (error) {
  console.error('Failed to load Next.js:', error);
  process.exit(1);
}