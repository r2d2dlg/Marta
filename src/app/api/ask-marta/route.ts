import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { query } = body;

    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Forward the request to the Python backend
    const pythonBackendUrl = 'http://localhost:5000/marta';
    const response = await fetch(pythonBackendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Error from Python backend:', errorData);
      return NextResponse.json({ error: 'Error from backend service' }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error in /api/ask-marta:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}