import { NextRequest, NextResponse } from 'next/server';
import { ai } from '@/ai/genkit';
import { GoogleAIService } from '@/ai/google-ai-service';

// Initialize Google AI Service for enhanced analysis
const googleAI = new GoogleAIService({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
  location: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      clientName, 
      clientCompany, 
      messageText, 
      clientHistory,
      phone,
      geminiPreAnalysis,
      useGeminiPreAnalysis = false
    } = body;

    if (!clientName || !messageText) {
      return NextResponse.json(
        { error: 'clientName and messageText are required' },
        { status: 400 }
      );
    }

    // Analyze message with Marta AI (enhanced with Gemini pre-analysis)
    const analysis = await analyzeMessage({
      clientName,
      clientCompany: clientCompany || '',
      messageText,
      clientHistory: clientHistory || '',
      geminiPreAnalysis,
      useGeminiPreAnalysis,
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
  geminiPreAnalysis?: any;
  useGeminiPreAnalysis?: boolean;
}) {
  const { clientName, clientCompany, messageText, clientHistory, geminiPreAnalysis, useGeminiPreAnalysis } = input;

  try {
    // Use Google AI Service for comprehensive analysis
    const googleAnalysis = await googleAI.analyzeText(messageText);
    
    // Enhanced AI prompt with Google AI insights AND Gemini pre-analysis
    const systemPrompt = `
You are Marta, an advanced AI assistant specialized in customer relationship management for Latin American businesses.
You have access to comprehensive Google AI analysis ${useGeminiPreAnalysis ? 'AND Gemini document analysis' : ''} and should provide enhanced insights.

Google AI Analysis Results:
- Sentiment Score: ${googleAnalysis.sentiment.score} (${googleAnalysis.sentiment.label})
- Detected Language: ${googleAnalysis.language}
- Entities: ${JSON.stringify(googleAnalysis.entities)}
- Categories: ${JSON.stringify(googleAnalysis.categories)}

${useGeminiPreAnalysis && geminiPreAnalysis ? `
Gemini Pre-Analysis Results:
- Priority: ${geminiPreAnalysis.priority}
- Category: ${geminiPreAnalysis.category}
- Sentiment: ${geminiPreAnalysis.sentiment}
- Language: ${geminiPreAnalysis.language}
- Extracted Entities: ${JSON.stringify(geminiPreAnalysis.entities)}
- Urgency Indicators: ${JSON.stringify(geminiPreAnalysis.urgencyIndicators)}
` : ''}

Respond with a JSON object containing:
- summary: Brief summary of the message
- sentiment: "positive", "negative", "neutral", or "urgent" (enhanced with all AI data)
- responseRequired: boolean indicating if a response is needed
- suggestedResponse: Spanish response if responseRequired is true
- categories: Array of enhanced categories based on all AI analysis
- priority: "low", "medium", "high", or "urgent"
- extractedInfo: Enhanced information extraction using all AI data
- confidence: Confidence score (0-1) based on all AI analysis
- languageDetected: Language detected by AI
- translation: Auto-translation if message is not in Spanish
${useGeminiPreAnalysis ? '- geminiEnhanced: true to indicate Gemini pre-analysis was used' : ''}
`;

    const userPrompt = `
Cliente: ${clientName}
Empresa: ${clientCompany || 'No especificada'}
Historial previo: ${clientHistory || 'Sin historial previo'}

Nuevo mensaje de WhatsApp:
"${messageText}"

Using the ${useGeminiPreAnalysis ? 'Google AI analysis AND Gemini pre-analysis' : 'Google AI analysis'} provided above, give me your enhanced evaluation in JSON format.
Focus on the entities detected, sentiment analysis, and provide intelligent categorization.
${useGeminiPreAnalysis ? 'Leverage the Gemini pre-analysis to enhance your understanding and provide even more accurate insights.' : ''}
`;

    const response = await ai.generate({
      model: 'vertexai/gemini-1.5-pro', // Use Vertex AI Gemini Pro
      system: systemPrompt,
      prompt: userPrompt,
      config: {
        temperature: 0.2, // Lower temperature for more consistent analysis
        maxOutputTokens: 1500,
        topP: 0.8,
        topK: 40,
      },
    });

    const analysis = response.text();
    
    try {
      const parsedAnalysis = JSON.parse(analysis);
      
      // Enhance with Google AI data
      return {
        ...parsedAnalysis,
        googleAI: {
          sentiment: googleAnalysis.sentiment,
          entities: googleAnalysis.entities,
          categories: googleAnalysis.categories,
          language: googleAnalysis.language,
          translation: googleAnalysis.translation,
        },
        enhancedWithGoogleAI: true,
      };
    } catch (parseError) {
      console.error('Error parsing enhanced AI response, using Google AI fallback');
      return createEnhancedFallbackAnalysis(clientName, messageText, googleAnalysis);
    }
  } catch (error) {
    console.error('Error in enhanced analysis, falling back to basic:', error);
    return createFallbackAnalysis(clientName, messageText);
  }
}

function createEnhancedFallbackAnalysis(clientName: string, messageText: string, googleAnalysis: any) {
  return {
    summary: `Mensaje de ${clientName}: ${messageText.substring(0, 100)}${messageText.length > 100 ? '...' : ''}`,
    sentiment: googleAnalysis.sentiment.label,
    responseRequired: true,
    suggestedResponse: `Hola ${clientName}, gracias por tu mensaje. Hemos recibido tu consulta y te responderemos lo antes posible.`,
    categories: googleAnalysis.categories.length > 0 ? googleAnalysis.categories.map((c: any) => c.name) : ['general'],
    priority: googleAnalysis.sentiment.score < -0.5 ? 'high' : 'medium',
    extractedInfo: {
      customerNeed: 'Consulta general',
      requestType: 'información',
      entities: googleAnalysis.entities,
    },
    confidence: 0.7,
    languageDetected: googleAnalysis.language,
    translation: googleAnalysis.translation,
    googleAI: googleAnalysis,
    enhancedWithGoogleAI: true,
  };
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
    confidence: 0.5,
    enhancedWithGoogleAI: false,
  };
}