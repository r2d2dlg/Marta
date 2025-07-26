import { NextRequest, NextResponse } from 'next/server';
import { ai } from '@/ai/genkit';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      clientName, 
      clientCompany, 
      messageText, 
      clientHistory,
      phone 
    } = body;

    if (!clientName || !messageText) {
      return NextResponse.json(
        { error: 'clientName and messageText are required' },
        { status: 400 }
      );
    }

    // Analyze message with Marta AI
    const analysis = await analyzeMessage({
      clientName,
      clientCompany: clientCompany || '',
      messageText,
      clientHistory: clientHistory || '',
    });

    return NextResponse.json({
      analysis,
      processedAt: new Date().toISOString(),
      clientPhone: phone,
    });
  } catch (error) {
    console.error('Error processing message with Marta:', error);
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    );
  }
}

async function analyzeMessage(input: {
  clientName: string;
  clientCompany: string;
  messageText: string;
  clientHistory: string;
}) {
  const { clientName, clientCompany, messageText, clientHistory } = input;

  const systemPrompt = `
You are Marta, an AI assistant specialized in customer relationship management for Latin American businesses.
Analyze WhatsApp messages and provide structured insights for the business team.

Respond with a JSON object containing:
- summary: Brief summary of the message
- sentiment: "positive", "negative", "neutral", or "urgent"
- responseRequired: boolean indicating if a response is needed
- suggestedResponse: Spanish response if responseRequired is true
- categories: Array of categories like ["inquiry", "support", "complaint", "information"]
- priority: "low", "medium", "high", or "urgent"
- extractedInfo: Object with any useful extracted information
`;

  const userPrompt = `
Cliente: ${clientName}
Empresa: ${clientCompany || 'No especificada'}
Historial previo: ${clientHistory || 'Sin historial previo'}

Nuevo mensaje de WhatsApp:
"${messageText}"

Analiza este mensaje y proporciona tu evaluación en formato JSON.
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
    
    // Try to parse JSON response
    try {
      return JSON.parse(analysis);
    } catch (parseError) {
      console.error('Error parsing AI response, using fallback');
      return createFallbackAnalysis(clientName, messageText);
    }
  } catch (error) {
    console.error('Error calling AI:', error);
    return createFallbackAnalysis(clientName, messageText);
  }
}

function createFallbackAnalysis(clientName: string, messageText: string) {
  return {
    summary: `Mensaje de ${clientName}: ${messageText.substring(0, 100)}${messageText.length > 100 ? '...' : ''}`,
    sentiment: 'neutral',
    responseRequired: true,
    suggestedResponse: `Hola ${clientName}, gracias por tu mensaje. Hemos recibido tu consulta y te responderemos lo antes posible.`,
    categories: ['general'],
    priority: 'medium',
    extractedInfo: {
      customerNeed: 'Consulta general',
      requestType: 'información',
    },
  };
}