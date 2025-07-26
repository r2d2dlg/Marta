import { NextRequest, NextResponse } from 'next/server';
import { CRMService } from '@/lib/crm';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const client = CRMService.updateLastContact(params.id);
    
    if (!client) {
      return NextResponse.json(
        { error: 'Client not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({ 
      client,
      message: 'Last contact updated successfully' 
    });
  } catch (error) {
    console.error('Error updating last contact:', error);
    return NextResponse.json(
      { error: 'Failed to update last contact' },
      { status: 500 }
    );
  }
}