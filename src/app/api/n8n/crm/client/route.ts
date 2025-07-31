import { NextRequest, NextResponse } from 'next/server';
import { CRMService } from '@/lib/crm';

// GET: Find client by phone or email
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const phone = searchParams.get('phone');
    const email = searchParams.get('email');

    if (!phone && !email) {
      return NextResponse.json(
        { error: 'Phone or email parameter required' },
        { status: 400 }
      );
    }

    let client = null;
    
    if (phone) {
      client = CRMService.getClientByPhone(phone);
    } else if (email) {
      client = CRMService.getClientByEmail(email);
    }

    return NextResponse.json({
      found: !!client,
      client: client || null,
    });
  } catch (error) {
    console.error('Error finding client:', error);
    return NextResponse.json(
      { error: 'Failed to find client' },
      { status: 500 }
    );
  }
}

// POST: Create or update client
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { phone, name, email, company, notes, messageText, last_contact_source, ai_insights } = body;

    if (!phone || !name) {
      return NextResponse.json(
        { error: 'Phone and name are required' },
        { status: 400 }
      );
    }

    // Check if client exists
    let client = CRMService.getClientByPhone(phone);
    
    if (client) {
      // Update existing client
      const timestamp = new Date().toLocaleString();
      const newNote = messageText 
        ? `[${timestamp}] WhatsApp: "${messageText}"`
        : `[${timestamp}] Contact updated via n8n`;
      
      const updatedNotes = client.notes 
        ? `${client.notes}\n\n${newNote}`
        : newNote;

      client = CRMService.updateClient(client.id, {
        name: name || client.name,
        email: email || client.email,
        company: company || client.company,
        notes: updatedNotes,
        last_contact_source: last_contact_source || client.last_contact_source,
        ai_insights: ai_insights || client.ai_insights,
      });

      CRMService.updateLastContact(client.id);

      return NextResponse.json({
        action: 'updated',
        client: client,
      });
    } else {
      // Create new client
      const initialNotes = messageText 
        ? `Initial contact via WhatsApp: "${messageText}"\nReceived at: ${new Date().toLocaleString()}`
        : notes || 'Created via n8n workflow';

      client = CRMService.createClient({
        name,
        email: email || '',
        phone,
        company: company || '',
        notes: initialNotes,
        last_contact_source: last_contact_source,
        ai_insights: ai_insights,
      });

      return NextResponse.json({
        action: 'created',
        client: client,
      });
    }
  } catch (error: any) {
    console.error('Error creating/updating client:', error);
    
    if (error.message?.includes('already exists')) {
      return NextResponse.json(
        { error: error.message },
        { status: 409 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to process client' },
      { status: 500 }
    );
  }
}

// PUT: Update client contact
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { phone, messageText, last_contact_source, ai_insights } = body;

    if (!phone) {
      return NextResponse.json(
        { error: 'Phone parameter required' },
        { status: 400 }
      );
    }

    const client = CRMService.getClientByPhone(phone);
    
    if (!client) {
      return NextResponse.json(
        { error: 'Client not found' },
        { status: 404 }
      );
    }

    // Update last contact
    const updatedClient = CRMService.updateLastContact(client.id);

    // Add message to notes if provided
    if (messageText) {
      const timestamp = new Date().toLocaleString();
      const newNote = `[${timestamp}] WhatsApp: "${messageText}"`;
      const updatedNotes = client.notes 
        ? `${client.notes}\n\n${newNote}`
        : newNote;

      CRMService.updateClient(client.id, { 
        notes: updatedNotes,
        last_contact_source: last_contact_source || client.last_contact_source,
        ai_insights: ai_insights || client.ai_insights,
      });
    }

    return NextResponse.json({
      action: 'contact_updated',
      client: updatedClient,
    });
  } catch (error) {
    console.error('Error updating client contact:', error);
    return NextResponse.json(
      { error: 'Failed to update client contact' },
      { status: 500 }
    );
  }
}