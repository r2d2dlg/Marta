import { NextRequest, NextResponse } from 'next/server';
import { GoogleAIService } from '@/ai/google-ai-service';

// Initialize Google AI Service
const googleAI = new GoogleAIService({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
  location: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const text = formData.get('text') as string;
    const file = formData.get('file') as File;
    const contentType = formData.get('contentType') as string || 'text';

    if (!text && !file) {
      return NextResponse.json(
        { error: 'Either text or file is required' },
        { status: 400 }
      );
    }

    let analysis;
    
    if (file) {
      const buffer = Buffer.from(await file.arrayBuffer());
      const fileType = file.type.startsWith('image/') ? 'image' : 
                      file.type.startsWith('audio/') ? 'audio' : 
                      file.type === 'application/pdf' ? 'document' : 'text';
      
      analysis = await googleAI.comprehensiveAnalysis(
        file.name,
        fileType,
        buffer
      );
    } else {
      analysis = await googleAI.comprehensiveAnalysis(text, 'text');
    }

    return NextResponse.json({
      success: true,
      analysis,
      processedAt: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error in AI analysis:', error);
    return NextResponse.json(
      { error: 'Failed to analyze content' },
      { status: 500 }
    );
  }
}

// GET endpoint for health check
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    services: [
      'Natural Language API',
      'Translation API',
      'Speech-to-Text API',
      'Text-to-Speech API',
      'Vision API',
      'Document AI',
      'Video Intelligence API',
      'Vertex AI',
    ],
    timestamp: new Date().toISOString(),
  });
}