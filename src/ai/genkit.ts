import {genkit} from 'genkit';
import {googleAI} from '@genkit-ai/googleai';

export const ai = genkit({
  plugins: [
    googleAI({
      // You can specify API key, version, etc. here if needed
      // apiKey: process.env.GOOGLE_GENAI_API_KEY, 
    })
  ],
  // Models and embedders are typically made available by name
  // by the googleAI() plugin itself in this version of Genkit.
});
