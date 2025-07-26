import { z } from 'zod';
import { ai } from '../genkit';
import { defineFlow } from 'genkit';

export const ProcessWhatsAppMessageInputSchema = z.object({
  clientName: z.string(),
  clientCompany: z.string().optional(),
  messageText: z.string(),
  clientHistory: z.string().optional(),
});

export const ProcessWhatsAppMessageOutputSchema = z.object({
  summary: z.string(),
  sentiment: z.enum(['positive', 'negative', 'neutral', 'urgent']),
  responseRequired: z.boolean(),
  suggestedResponse: z.string().optional(),
  categories: z.array(z.string()),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  extractedInfo: z.object({
    customerNeed: z.string().optional(),
    requestType: z.string().optional(),
    contactInfo: z.object({
      email: z.string().optional(),
      alternativePhone: z.string().optional(),
    }).optional(),
  }),
});

export const processWhatsAppMessageFlow = defineFlow(
  ai,
  {
    name: 'processWhatsAppMessage',
    inputSchema: ProcessWhatsAppMessageInputSchema,
    outputSchema: ProcessWhatsAppMessageOutputSchema,
  },
  async (input) => {
    const { clientName, clientCompany, messageText, clientHistory } = input;

    const systemPrompt = `
You are Marta, an AI assistant specialized in customer relationship management. 
You analyze WhatsApp messages from clients and provide insights for business teams.

Your task is to analyze the incoming WhatsApp message and provide:
1. A concise summary of the message
2. Sentiment analysis (positive, negative, neutral, urgent)
3. Whether a response is required
4. Suggested response if needed
5. Message categories (inquiry, complaint, request, information, support, etc.)
6. Priority level based on urgency and importance
7. Extract any useful information like customer needs, contact details, etc.

Always respond in a professional, helpful manner and consider the cultural context for Spanish-speaking clients.
`;

    const userPrompt = `
Client Information:
- Name: ${clientName}
- Company: ${clientCompany || 'No company specified'}
- Previous interaction history: ${clientHistory || 'No previous history'}

New WhatsApp Message:
"${messageText}"

Please analyze this message and provide your assessment in JSON format according to the schema.
`;

    try {
      const response = await ai.generate({
        model: 'googleai/gemini-1.5-flash',
        system: systemPrompt,
        prompt: userPrompt,
        config: {
          temperature: 0.3,
          maxOutputTokens: 1000,
        },
      });

      const analysis = response.text();
      
      // Parse the JSON response
      let parsedAnalysis;
      try {
        parsedAnalysis = JSON.parse(analysis);
      } catch (parseError) {
        console.error('Error parsing AI response:', parseError);
        // Fallback response
        parsedAnalysis = {
          summary: `Message from ${clientName}: ${messageText.substring(0, 100)}...`,
          sentiment: 'neutral',
          responseRequired: true,
          suggestedResponse: `Hola ${clientName}, gracias por tu mensaje. Hemos recibido tu consulta y te responderemos lo antes posible.`,
          categories: ['general'],
          priority: 'medium',
          extractedInfo: {
            customerNeed: 'General inquiry',
          },
        };
      }

      return parsedAnalysis;
    } catch (error) {
      console.error('Error in processWhatsAppMessageFlow:', error);
      
      // Fallback response in case of AI failure
      return {
        summary: `Message from ${clientName}: ${messageText.substring(0, 100)}...`,
        sentiment: 'neutral' as const,
        responseRequired: true,
        suggestedResponse: `Hola ${clientName}, gracias por tu mensaje. Hemos recibido tu consulta y te responderemos lo antes posible.`,
        categories: ['general'],
        priority: 'medium' as const,
        extractedInfo: {
          customerNeed: 'General inquiry',
        },
      };
    }
  }
);

export const generateWhatsAppResponseFlow = defineFlow(
  ai,
  {
    name: 'generateWhatsAppResponse',
    inputSchema: z.object({
      clientName: z.string(),
      clientCompany: z.string().optional(),
      messageText: z.string(),
      context: z.string().optional(),
      responseType: z.enum(['acknowledgment', 'answer', 'followup', 'escalation']).default('acknowledgment'),
    }),
    outputSchema: z.object({
      response: z.string(),
      tone: z.enum(['formal', 'friendly', 'professional']),
      includeFollowUp: z.boolean(),
    }),
  },
  async (input) => {
    const { clientName, clientCompany, messageText, context, responseType } = input;

    const systemPrompt = `
You are Marta, a professional AI assistant for customer service via WhatsApp. 
You help businesses communicate effectively with their Spanish-speaking clients.

Guidelines:
- Be warm, professional, and helpful
- Use appropriate Spanish grammar and vocabulary
- Keep responses concise but complete
- Always acknowledge the client by name
- Maintain a friendly but professional tone
- Consider cultural context for Latin American business communications
`;

    const userPrompt = `
Client: ${clientName}${clientCompany ? ` from ${clientCompany}` : ''}
Their message: "${messageText}"
Context: ${context || 'No additional context'}
Response type needed: ${responseType}

Generate an appropriate WhatsApp response in Spanish.
`;

    try {
      const response = await ai.generate({
        model: 'googleai/gemini-1.5-flash',
        system: systemPrompt,
        prompt: userPrompt,
        config: {
          temperature: 0.4,
          maxOutputTokens: 300,
        },
      });

      const generatedResponse = response.text();

      return {
        response: generatedResponse,
        tone: 'professional' as const,
        includeFollowUp: responseType === 'followup',
      };
    } catch (error) {
      console.error('Error generating WhatsApp response:', error);
      
      // Fallback response
      return {
        response: `Hola ${clientName}, gracias por contactarnos. Hemos recibido tu mensaje y nos pondremos en contacto contigo lo antes posible.`,
        tone: 'professional' as const,
        includeFollowUp: false,
      };
    }
  }
);