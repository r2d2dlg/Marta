const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const htmlPath = path.resolve(__dirname, 'marketing', 'ad1.html');
  const pdfPath = path.resolve(__dirname, 'marketing', 'ad1.pdf');

  if (!fs.existsSync(htmlPath)) {
    console.error('HTML file not found:', htmlPath);
    process.exit(1);
  }

  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Open the HTML file using the file:// protocol
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle0' });

  await page.pdf({
    path: pdfPath,
    format: 'A4',
    printBackground: true,
    margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' },
  });

  await browser.close();
  console.log('PDF exported successfully to:', pdfPath);
})(); 