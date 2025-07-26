import { NextRequest, NextResponse } from 'next/server';
import { WhatsAppWebhookPayload, WhatsAppMessage } from '@/types/whatsapp';
import { WhatsAppService } from '@/lib/whatsapp';
import { CRMService } from '@/lib/crm';

const whatsappService = new WhatsAppService();

export async function GET(request: NextRequest) {
  // Webhook verification for Meta
  const { searchParams } = new URL(request.url);
  const mode = searchParams.get('hub.mode');
  const token = searchParams.get('hub.verify_token');
  const challenge = searchParams.get('hub.challenge');

  const verifyToken = process.env.WHATSAPP_VERIFY_TOKEN;

  if (mode === 'subscribe' && token === verifyToken) {
    console.log('WhatsApp webhook verified');
    return new NextResponse(challenge, { status: 200 });
  }

  console.error('WhatsApp webhook verification failed');
  return NextResponse.json({ error: 'Verification failed' }, { status: 403 });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();
    const signature = request.headers.get('x-hub-signature-256');

    // Validate webhook signature (optional but recommended for production)
    if (signature && !whatsappService.validateWebhookSignature(body, signature)) {
      console.error('Invalid webhook signature');
      return NextResponse.json({ error: 'Invalid signature' }, { status: 403 });
    }

    const webhookData: WhatsAppWebhookPayload = JSON.parse(body);

    // Process each entry in the webhook
    for (const entry of webhookData.entry) {
      for (const change of entry.changes) {
        if (change.field === 'messages') {
          await processMessages(change.value);
        }
      }
    }

    return NextResponse.json({ status: 'success' }, { status: 200 });
  } catch (error) {
    console.error('Error processing WhatsApp webhook:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

async function processMessages(value: any) {
  const { messages, contacts, metadata } = value;

  if (!messages || messages.length === 0) {
    return;
  }

  for (const message of messages) {
    try {
      await processIncomingMessage(message, contacts, metadata);
    } catch (error) {
      console.error('Error processing individual message:', error);
    }
  }
}

async function processIncomingMessage(
  message: WhatsAppMessage,
  contacts: any[],
  metadata: any
) {
  console.log('Processing WhatsApp message:', message.id);

  // Get sender phone number
  const senderPhone = whatsappService.formatPhoneNumber(message.from);
  
  // Get contact name from WhatsApp if available
  const contact = contacts?.find(c => c.wa_id === message.from);
  const senderName = contact?.profile?.name || 'Unknown';

  // Only process text messages for now
  if (message.type !== 'text' || !message.text?.body) {
    console.log('Skipping non-text message');
    return;
  }

  const messageText = message.text.body;

  // Try to find existing client by phone number
  let client = CRMService.getClientByPhone(senderPhone);

  if (!client) {
    // Create new client if doesn't exist
    try {
      client = CRMService.createClient({
        name: senderName,
        email: '', // We'll need to ask for this later
        phone: senderPhone,
        company: '',
        notes: `Initial contact via WhatsApp. Message: "${messageText}"\nReceived at: ${new Date(parseInt(message.timestamp) * 1000).toLocaleString()}`,
      });

      console.log(`Created new client: ${client.name} (${client.phone})`);

      // Send welcome message for new clients
      await whatsappService.sendMessage(
        message.from,
        `¡Hola ${senderName}! Gracias por contactarnos. Tu mensaje ha sido recibido y será procesado por nuestro equipo. Te responderemos lo antes posible.`
      );
    } catch (error) {
      console.error('Error creating new client:', error);
      return;
    }
  } else {
    // Update existing client's notes and last contact
    const updatedNotes = client.notes + `\n\n[${new Date().toLocaleString()}] WhatsApp: "${messageText}"`;
    
    CRMService.updateClient(client.id, {
      notes: updatedNotes,
    });

    CRMService.updateLastContact(client.id);

    console.log(`Updated existing client: ${client.name} (${client.phone})`);
  }

  // Mark message as read
  await whatsappService.markMessageAsRead(message.id);

  // TODO: Process message with Marta AI for intelligent responses
  await processMessageWithMarta(client, messageText, message);
}

async function processMessageWithMarta(client: any, messageText: string, message: WhatsAppMessage) {
  // This will be implemented next - integration with Marta AI
  console.log(`TODO: Process message with Marta AI for client ${client.name}: "${messageText}"`);
  
  // For now, just log the message processing
  console.log('Message processed and stored in CRM');
}