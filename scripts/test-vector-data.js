const fs = require('fs').promises;
const path = require('path');

async function testVectorData() {
  try {
    const dataPath = path.join(process.cwd(), 'data', 'vertex_ai_vector_data.jsonl');
    console.log('Testing file:', dataPath);
    
    // Read first 100KB of the file
    const file = await fs.open(dataPath, 'r');
    const buffer = Buffer.alloc(100000); // 100KB
    const { bytesRead } = await file.read(buffer, 0, buffer.length, 0);
    await file.close();
    
    const content = buffer.toString('utf8', 0, bytesRead);
    const lines = content.split('\n').filter(Boolean);
    
    console.log(`Read ${lines.length} lines`);
    
    // Test parsing first few lines
    for (let i = 0; i < Math.min(5, lines.length); i++) {
      try {
        const obj = JSON.parse(lines[i]);
        console.log(`Line ${i + 1}: Valid JSON, id: ${obj.id}`);
      } catch (error) {
        console.error(`Error parsing line ${i + 1}:`, error.message);
        console.error('Line content:', lines[i].substring(0, 200) + '...');
      }
    }
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

testVectorData();
