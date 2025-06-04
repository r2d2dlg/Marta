'use server';

/**
 * @fileOverview This flow enables the AI to search the web for information relevant to client emails.
 *
 * - searchWebForEmailContext - A function that handles the web search and context retrieval process.
 * - SearchWebForEmailContextInput - The input type for the searchWebForEmailContext function.
 * - SearchWebForEmailContextOutput - The return type for the searchWebForEmailContext function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SearchWebForEmailContextInputSchema = z.object({
  emailContent: z.string().describe('The content of the client email.'),
  searchQuery: z.string().optional().describe('Optional. The query to use to search the web.'),
});
export type SearchWebForEmailContextInput = z.infer<typeof SearchWebForEmailContextInputSchema>;

const SearchWebForEmailContextOutputSchema = z.object({
  searchResult: z.string().describe('The search result from the web.'),
});
export type SearchWebForEmailContextOutput = z.infer<typeof SearchWebForEmailContextOutputSchema>;

export async function searchWebForEmailContext(input: SearchWebForEmailContextInput): Promise<SearchWebForEmailContextOutput> {
  return searchWebForEmailContextFlow(input);
}

const webSearchTool = ai.defineTool({
  name: 'webSearch',
  description: 'Searches the web for relevant information.',
  inputSchema: z.object({
    query: z.string().describe('The search query.'),
  }),
  outputSchema: z.string(),
}, async (input) => {
  // TODO: Replace with actual web search implementation.
  // This is just a placeholder.
  console.log(`Simulating web search for query: ${input.query}`);
  return `Simulated search result for query: ${input.query}`;
});

const searchWebForEmailContextPrompt = ai.definePrompt({
  name: 'searchWebForEmailContextPrompt',
  tools: [webSearchTool],
  input: {schema: SearchWebForEmailContextInputSchema},
  output: {schema: SearchWebForEmailContextOutputSchema},
  prompt: `You are assisting a user in responding to client emails. To provide well-informed and accurate responses, you can search the web for relevant information.

The content of the email is as follows:

{{emailContent}}

If the user has provided a specific search query, use it. Otherwise, derive a suitable search query from the email content.
Use the webSearch tool to search the web and provide the search result.
`,
});

const searchWebForEmailContextFlow = ai.defineFlow(
  {
    name: 'searchWebForEmailContextFlow',
    inputSchema: SearchWebForEmailContextInputSchema,
    outputSchema: SearchWebForEmailContextOutputSchema,
  },
  async input => {
    const {output} = await searchWebForEmailContextPrompt(input);
    return output!;
  }
);
