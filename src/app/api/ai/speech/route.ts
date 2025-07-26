import { NextRequest, NextResponse } from 'next/server';
import { GoogleAIService } from '@/ai/google-ai-service';

const googleAI = new GoogleAIService({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
  location: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
});

// Speech-to-Text
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const audioFile = formData.get('audio') as File;
    const languageCode = formData.get('languageCode') as string || 'es-ES';

    if (!audioFile) {
      return NextResponse.json(
        { error: 'Audio file is required' },
        { status: 400 }
      );
    }

    const audioBuffer = Buffer.from(await audioFile.arrayBuffer());
    const transcription = await googleAI.transcribeAudio(audioBuffer, languageCode);

    return NextResponse.json({
      success: true,
      transcription,
      languageCode,
      fileName: audioFile.name,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error transcribing audio:', error);
    return NextResponse.json(
      { error: 'Failed to transcribe audio' },
      { status: 500 }
    );
  }
}

// Text-to-Speech
export async function PUT(request: NextRequest) {
  try {
    const { text, languageCode = 'es-ES' } = await request.json();

    if (!text) {
      return NextResponse.json(
        { error: 'Text is required' },
        { status: 400 }
      );
    }

    const audioBuffer = await googleAI.synthesizeSpeech(text, languageCode);

    return new NextResponse(audioBuffer, {
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': 'attachment; filename="speech.mp3"',
        'Content-Length': audioBuffer.length.toString(),
      },
    });
  } catch (error) {
    console.error('Error synthesizing speech:', error);
    return NextResponse.json(
      { error: 'Failed to synthesize speech' },
      { status: 500 }
    );
  }
}