# n8n Integration Setup for Marta AI - WhatsApp CRM

This guide will help you set up the complete n8n workflow for integrating WhatsApp Business with your CRM using Marta AI.

## Overview

The workflow automatically:
1. Receives WhatsApp messages via webhook
2. Identifies or creates clients in CRM
3. Processes messages with Marta AI for analysis
4. Generates intelligent responses
5. Sends automated replies back to WhatsApp

## Prerequisites

1. **n8n installed and running**
2. **WhatsApp Business API access** (your Meta App "Marta")
3. **Marta AI application running** on `http://localhost:9002`

## Step 1: Environment Variables

Set these environment variables in your Marta AI application (`.env.local`):

```bash
# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_APP_SECRET=your_app_secret
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token

# Google AI (for Marta)
GOOGLE_GENAI_API_KEY=your_google_ai_api_key
```

## Step 2: n8n Environment Variables

In your n8n instance, set these variables:

- `WHATSAPP_ACCESS_TOKEN`: Your WhatsApp access token
- `WHATSAPP_PHONE_NUMBER_ID`: Your phone number ID
- `MARTA_API_BASE_URL`: `http://localhost:9002` (or your Marta AI URL)

## Step 3: Import n8n Workflow

1. Copy the workflow from `n8n-workflows/whatsapp-crm-workflow.json`
2. In n8n, go to **Workflows** → **Import**
3. Paste the JSON content
4. Update the webhook URL in the workflow to match your n8n instance

## Step 4: Configure WhatsApp Webhook

1. Go to your Meta App Developer Console
2. Navigate to **WhatsApp** → **Configuration**
3. Set the webhook URL to: `https://your-n8n-instance.com/webhook/whatsapp-webhook`
4. Set the verify token to match `WHATSAPP_VERIFY_TOKEN`
5. Subscribe to `messages` events

## API Endpoints for n8n

Your Marta AI application exposes these endpoints for n8n:

### CRM Operations

**GET** `/api/n8n/crm/client?phone={phone}`
- Find client by phone number
- Returns: `{ found: boolean, client: Client | null }`

**POST** `/api/n8n/crm/client`
- Create or update client
- Body: `{ phone, name, email?, company?, messageText? }`
- Returns: `{ action: 'created'|'updated', client: Client }`

**PUT** `/api/n8n/crm/client`
- Update client last contact
- Body: `{ phone, messageText? }`
- Returns: `{ action: 'contact_updated', client: Client }`

### Marta AI Operations

**POST** `/api/n8n/marta/process-message`
- Analyze message with AI
- Body: `{ clientName, messageText, clientHistory?, clientCompany? }`
- Returns: `{ analysis: { summary, sentiment, responseRequired, priority, ... } }`

**POST** `/api/n8n/marta/generate-response`
- Generate intelligent response
- Body: `{ clientName, messageText, responseType?, urgency? }`
- Returns: `{ response: { message, tone, responseType } }`

## Workflow Logic

```
WhatsApp Message → Extract Data → Check Client → Create/Update Client
                                      ↓
Process with Marta AI → Check Response Needed → Generate Response → Send WhatsApp
                           ↓
                    Log Interaction → Webhook Response
```

## Testing the Integration

1. **Test CRM API**: Send a POST request to `/api/n8n/crm/client`
2. **Test Marta AI**: Send a POST request to `/api/n8n/marta/process-message`
3. **Test full workflow**: Send a WhatsApp message to your business number

## Customization Options

### Response Types
- `acknowledgment`: Basic confirmation message
- `answer`: Specific answer to a question
- `followup`: Follow-up on previous conversation
- `escalation`: Route to human agent
- `information`: Provide requested information

### Message Categories
Marta AI automatically categorizes messages:
- `inquiry`: General questions
- `support`: Support requests
- `complaint`: Customer complaints
- `information`: Information requests
- `urgent`: Urgent matters

### Priority Levels
- `low`: Non-urgent messages
- `medium`: Standard priority
- `high`: Important messages
- `urgent`: Immediate attention required

## Monitoring and Logs

- Check n8n execution logs for workflow status
- Monitor Marta AI logs for API calls
- Review CRM for new/updated clients
- Check WhatsApp Business Manager for message delivery

## Troubleshooting

1. **Webhook not receiving messages**: Check webhook URL and verify token
2. **Client not created**: Check API endpoint accessibility
3. **AI not responding**: Verify Google AI API key
4. **Messages not sending**: Check WhatsApp access token and permissions

## Security Considerations

1. **Use HTTPS** for all webhook URLs
2. **Validate webhook signatures** (implemented in WhatsApp service)
3. **Store secrets securely** in environment variables
4. **Limit API access** to trusted sources
5. **Monitor for unusual activity**

## Next Steps

1. Set up email integration workflow
2. Add more sophisticated AI prompts
3. Implement sentiment-based routing
4. Add integration with other business tools
5. Create dashboards for monitoring interactions

For support, check the logs in both n8n and your Marta AI application.