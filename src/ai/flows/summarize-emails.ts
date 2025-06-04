'use server';
/**
 * @fileOverview Summarizes client emails to quickly understand the main points and prioritize responses.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { google, gmail_v1 } from 'googleapis'; // Import google and specific Gmail types

// Helper function to extract plain text content from Gmail message payload
// This is a simplified example; real email payloads can be complex.
function extractEmailContent(payload: gmail_v1.Schema$MessagePart | undefined): string {
  if (!payload) return '';

  let content = '';

  // Look for text/plain part first
  if (payload.mimeType === 'text/plain' && payload.body?.data) {
    content = Buffer.from(payload.body.data, 'base64').toString('utf-8');
  }
  // If no text/plain, look in parts (for multipart emails)
  else if (payload.parts) {
    for (const part of payload.parts) {
      if (part.mimeType === 'text/plain' && part.body?.data) {
        content = Buffer.from(part.body.data, 'base64').toString('utf-8');
        break; // Found plain text, stop searching
      }
      // You could recursively search nested parts if necessary
      // else if (part.parts) {
      //   content = extractEmailContent(part); // simplified recursive call
      //   if (content) break;
      // }
    }
  }
  // Fallback: If still no plain text, you might try to get HTML and strip tags,
  // or just indicate that plain text content was not found.
  // For simplicity, we are not handling HTML here.

  return content;
}


const SummarizeEmailsInputSchema = z.object({
  emailContent: z.string().optional().describe('The direct content of the email to summarize. Used if emailId and accessToken are not provided.'),
  accessToken: z.string().optional().describe('Google Access Token for API access. Required if using emailId.'),
  emailId: z.string().optional().describe('The ID of the email to fetch and summarize. Requires accessToken.'),
}).refine(data => {
  // If emailId is provided, accessToken must also be provided.
  if (data.emailId && !data.accessToken) {
    return false;
  }
  // If emailContent is not provided, then emailId and accessToken must be.
  if (!data.emailContent && (!data.emailId || !data.accessToken)) {
    return false;
  }
  return true;
}, {
  message: "If emailId is provided, accessToken is required. If emailContent is not provided, emailId and accessToken are required.",
});

export type SummarizeEmailsInput = z.infer<typeof SummarizeEmailsInputSchema>;

const SummarizeEmailsOutputSchema = z.object({
  summary: z.string().describe('A brief summary of the email content.'),
  fetchedEmailId: z.string().optional().describe('The ID of the email if it was fetched.'),
});
export type SummarizeEmailsOutput = z.infer<typeof SummarizeEmailsOutputSchema>;

export async function summarizeEmails(input: SummarizeEmailsInput): Promise<SummarizeEmailsOutput> {
  // The flow definition handles the input validation based on the schema
  return summarizeEmailsFlow(input);
}

// The prompt now focuses on the content, whether passed directly or fetched.
const summarizeEmailsPrompt = ai.definePrompt(
  {
    name: 'summarizeEmailsPrompt',
    // Input schema for the prompt itself, just needs the content.
    input: { schema: z.object({ contentForSummary: z.string() }) },
    output: { schema: SummarizeEmailsOutputSchema }, // Output will be just the summary
    prompt: `Summarize the following email content concisely:

{{{contentForSummary}}}`,
  }
);

const summarizeEmailsFlow = ai.defineFlow(
  {
    name: 'summarizeEmailsFlow',
    inputSchema: SummarizeEmailsInputSchema,
    outputSchema: SummarizeEmailsOutputSchema,
  },
  async (input) => {
    let contentToSummarize = input.emailContent;
    let fetchedEmailId: string | undefined = undefined;

    if (input.emailId && input.accessToken) {
      console.log(`Fetching email with ID: ${input.emailId} using access token.`);
      try {
        const oauth2Client = new google.auth.OAuth2();
        oauth2Client.setCredentials({ access_token: input.accessToken });

        const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

        const emailDetailsResponse = await gmail.users.messages.get({
          userId: 'me', // 'me' refers to the authenticated user
          id: input.emailId,
          format: 'full', // Get full payload to find text/plain part
        });
        
        const message = emailDetailsResponse.data;
        contentToSummarize = extractEmailContent(message.payload);
        fetchedEmailId = message.id ?? undefined; // Store the fetched email ID

        if (!contentToSummarize) {
          console.warn(`Could not extract plain text content for email ID: ${input.emailId}`);
          // Fallback or throw error - for now, we'll try to summarize an empty string or the original snippet if available
          contentToSummarize = input.emailContent || "Could not retrieve email content.";
        } else {
          console.log(`Successfully fetched content for email ID: ${input.emailId}`);
        }

      } catch (error) {
        console.error(`Error fetching email (ID: ${input.emailId}) with access token:`, error);
        // Fallback to original content if fetching fails and content was provided
        if (input.emailContent) {
          contentToSummarize = input.emailContent;
          console.warn(`Falling back to provided emailContent for email ID: ${input.emailId}`);
        } else {
          // If no fallback content, throw an error or return an error state
          throw new Error(`Failed to fetch email content for ID ${input.emailId} and no fallback content provided.`);
        }
      }
    }

    if (!contentToSummarize) {
      // If after all attempts, contentToSummarize is still empty or undefined
      console.error("No content available to summarize.");
      // You might want to throw an error or return a specific error object
      return { summary: "Error: No content available to summarize.", fetchedEmailId };
    }
    
    // Call the prompt with the content (either passed in or fetched)
    const { output } = await summarizeEmailsPrompt({ contentForSummary: contentToSummarize });
    
    // Ensure output is not null before accessing its properties
    if (!output) {
        throw new Error("Summarization prompt did not return an output.");
    }
    
    return { summary: output.summary, fetchedEmailId };
  }
);
