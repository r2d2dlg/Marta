import { config } from 'dotenv';
config();

import './flows/summarize-emails'; // Assuming you want to keep these. Adjusted path.
import './flows/search-web-for-email-context'; // Adjusted path.
import './flows/suggest-email-responses'; // Adjusted path.
import { queryProjectDatabaseFlow } from './flows/query-project-database'; // Import the specific flow. Adjusted path.

// Function to test the queryProjectDatabaseFlow
async function testQueryProjectDatabase() {
  console.log('Testing queryProjectDatabaseFlow...');
  try {
    const sampleQuery = "What is the main purpose of this project?"; // Or any other test query
    const result = await queryProjectDatabaseFlow(sampleQuery);
    console.log('Flow Result:', result);
  } catch (error) {
    console.error('Error testing flow:', error);
  }
}

// Run the test
testQueryProjectDatabase();
