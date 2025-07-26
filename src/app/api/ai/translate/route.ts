import { NextRequest, NextResponse } from 'next/server';
import { GoogleAIService } from '@/ai/google-ai-service';

const googleAI = new GoogleAIService({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
  location: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

export async function POST(request: NextRequest) {
  try {
    const { text, targetLanguage = 'es', sourceLanguage } = await request.json();

    if (!text) {
      return NextResponse.json(
        { error: 'Text is required' },
        { status: 400 }
      );
    }

    const translation = await googleAI.translateText(text, targetLanguage, sourceLanguage);

    return NextResponse.json({
      success: true,
      original: text,
      translated: translation.text,
      detectedLanguage: translation.detectedLanguage,
      targetLanguage,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error translating text:', error);
    return NextResponse.json(
      { error: 'Failed to translate text' },
      { status: 500 }
    );
  }
}