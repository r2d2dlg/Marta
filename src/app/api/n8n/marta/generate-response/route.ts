import { NextRequest, NextResponse } from 'next/server';
import { ai } from '@/ai/genkit';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      clientName, 
      clientCompany, 
      messageText, 
      responseType = 'acknowledgment',
      context = '',
      urgency = 'medium'
    } = body;

    if (!clientName || !messageText) {
      return NextResponse.json(
        { error: 'clientName and messageText are required' },
        { status: 400 }
      );
    }

    const response = await generateResponse({
      clientName,
      clientCompany: clientCompany || '',
      messageText,
      responseType,
      context,
      urgency,
    });

    return NextResponse.json({
      response,
      generatedAt: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error generating response:', error);
    return NextResponse.json(
      { error: 'Failed to generate response' },
      { status: 500 }
    );
  }
}

async function generateResponse(input: {
  clientName: string;
  clientCompany: string;
  messageText: string;
  responseType: string;
  context: string;
  urgency: string;
}) {
  const { clientName, clientCompany, messageText, responseType, context, urgency } = input;

  const systemPrompt = `
Eres Marta, una asistente de IA profesional para atención al cliente vía WhatsApp.
Ayudas a empresas a comunicarse efectivamente con sus clientes hispanohablantes.

Pautas:
- Sé cálida, profesional y servicial
- Usa gramática y vocabulario español apropiado
- Mantén las respuestas concisas pero completas
- Siempre reconoce al cliente por su nombre
- Mantén un tono amigable pero profesional
- Considera el contexto cultural para comunicaciones empresariales latinoamericanas

Tipos de respuesta:
- acknowledgment: Confirmar recepción del mensaje
- answer: Responder una pregunta específica
- followup: Hacer seguimiento de una consulta previa
- escalation: Derivar a un especialista humano
- information: Proporcionar información solicitada
`;

  const userPrompt = `
Cliente: ${clientName}${clientCompany ? ` de ${clientCompany}` : ''}
Su mensaje: "${messageText}"
Tipo de respuesta requerida: ${responseType}
Contexto adicional: ${context || 'Sin contexto adicional'}
Nivel de urgencia: ${urgency}

Genera una respuesta apropiada para WhatsApp en español.
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

    return {
      message: response.text(),
      tone: 'professional',
      responseType,
      length: response.text().length,
    };
  } catch (error) {
    console.error('Error generating AI response:', error);
    
    // Fallback response based on type
    let fallbackMessage = '';
    
    switch (responseType) {
      case 'acknowledgment':
        fallbackMessage = `Hola ${clientName}, gracias por contactarnos. Hemos recibido tu mensaje y nos pondremos en contacto contigo lo antes posible.`;
        break;
      case 'escalation':
        fallbackMessage = `Hola ${clientName}, gracias por tu consulta. Un especialista de nuestro equipo se comunicará contigo en breve para brindarte la mejor atención.`;
        break;
      case 'followup':
        fallbackMessage = `Hola ${clientName}, queremos hacer seguimiento a tu consulta. ¿Hay algo más en lo que podamos ayudarte?`;
        break;
      default:
        fallbackMessage = `Hola ${clientName}, gracias por tu mensaje. Estamos revisando tu consulta y te responderemos pronto.`;
    }

    return {
      message: fallbackMessage,
      tone: 'professional',
      responseType,
      length: fallbackMessage.length,
    };
  }
}