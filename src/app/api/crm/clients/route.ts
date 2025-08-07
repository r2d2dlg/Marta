import { NextRequest, NextResponse } from 'next/server';
import { CRMService } from '@/lib/crm';
import { CreateClientInput } from '@/types/crm';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('search');
    
    if (query) {
      const clients = await CRMService.searchClients(query);
      return NextResponse.json({ clients });
    }
    
    const clients = await CRMService.getAllClients();
    return NextResponse.json({ clients });
  } catch (error) {
    console.error('Error fetching clients:', error);
    return NextResponse.json(
      { error: 'Failed to fetch clients' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { first_name, last_name, position, email, phone, company, notes }: CreateClientInput = body;
    
    if (!first_name || !last_name || !email || !phone) {
      return NextResponse.json(
        { error: 'First name, last name, email, and phone are required' },
        { status: 400 }
      );
    }
    
    const client = CRMService.createClient({
      first_name,
      last_name,
      position,
      email,
      phone,
      company,
      notes,
    });
    
    return NextResponse.json({ client }, { status: 201 });
  } catch (error: any) {
    console.error('Error creating client:', error);
    
    if (error.message.includes('already exists')) {
      return NextResponse.json(
        { error: error.message },
        { status: 409 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to create client' },
      { status: 500 }
    );
  }
}