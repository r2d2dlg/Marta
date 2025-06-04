import { NextResponse } from 'next/server';
import { handleAssistantQuery } from '@/app/(app)/inbox/actions';

export async function POST(request: Request) {
  try {
    const { query } = await request.json();
    
    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required and must be a string' },
        { status: 400 }
      );
    }

    const result = await handleAssistantQuery(query);
    return NextResponse.json(result);
    
  } catch (error: any) {
    console.error('Error in assistant API route:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ message: 'Assistant API is running' });
}
