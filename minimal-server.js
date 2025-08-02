const http = require('http');
const path = require('path');

console.log('Starting minimal server...');
console.log('Node version:', process.version);
console.log('Working directory:', process.cwd());
console.log('Environment:', process.env.NODE_ENV || 'development');

const server = http.createServer((req, res) => {
  console.log(`Request: ${req.method} ${req.url}`);
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end(`
    <html>
      <head><title>Marta AI - Test Server</title></head>
      <body>
        <h1>Marta AI Test Server</h1>
        <p>This is a minimal test server to verify WSL is working</p>
        <p>Time: ${new Date().toISOString()}</p>
        <p>Node: ${process.version}</p>
      </body>
    </html>
  `);
});

server.listen(9002, 'localhost', () => {
  console.log('✅ Server running at http://localhost:9002');
  console.log('Press Ctrl+C to stop');
});

server.on('error', (err) => {
  console.error('❌ Server error:', err.message);
  process.exit(1);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});