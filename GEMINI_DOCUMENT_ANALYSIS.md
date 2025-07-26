# Gemini Document Analysis Integration - Enhanced n8n Workflow

This document explains how to replace the basic "Extract Enhanced Message Data" node with Gemini's powerful "Analyze Document" capability for intelligent WhatsApp payload processing.

## Overview

The **Gemini-Enhanced WhatsApp Workflow** uses Gemini's document analysis capabilities to intelligently parse and analyze WhatsApp webhook payloads, providing much more sophisticated data extraction and initial message analysis.

## Benefits of Using Gemini Document Analysis

### Traditional Approach (Manual Data Extraction):
```javascript
// Basic manual extraction
{
  "phone": "={{ $json.entry[0].changes[0].value.messages[0].from }}",
  "messageText": "={{ $json.entry[0].changes[0].value.messages[0].text.body }}",
  "contactName": "={{ $json.entry[0].changes[0].value.contacts?.[0]?.profile?.name || 'Unknown' }}"
}
```

### Gemini Approach (Intelligent Analysis):
```json
{
  "messageInfo": {
    "id": "extracted message ID",
    "type": "intelligently detected message type",
    "body": "extracted content with context understanding"
  },
  "messageAnalysis": {
    "priority": "AI-determined priority level",
    "category": "intelligent categorization",
    "sentiment": "AI sentiment analysis",
    "urgencyIndicators": ["detected urgent keywords"],
    "extractedEntities": ["important information extracted"]
  }
}
```

## Workflow Structure

### 1. WhatsApp Webhook Reception
Standard webhook receives the Meta WhatsApp payload.

### 2. Gemini Document Analysis Node
**Type**: `@n8n/n8n-nodes-langchain.documentAnalyzer`

**Configuration**:
- **Model**: Google Gemini
- **System Message**: Expert WhatsApp payload analyzer
- **Human Message**: Comprehensive analysis prompt

**Key Features**:
- ✅ **Intelligent Data Extraction**: Gemini understands the webhook structure
- ✅ **Context Analysis**: Analyzes message content for priority and category
- ✅ **Sentiment Detection**: Initial sentiment analysis
- ✅ **Entity Extraction**: Finds important information (names, dates, products)
- ✅ **Urgency Detection**: Identifies urgent keywords and phrases
- ✅ **Media Detection**: Analyzes media attachments and context

### 3. Parse Gemini Response Node
**Type**: `n8n-nodes-base.code`

Parses Gemini's JSON response and structures it for the workflow:

```javascript
const structuredOutput = {
  // Message basics
  messageId: parsedData.messageInfo?.id,
  messageType: parsedData.messageInfo?.type,
  messageBody: parsedData.messageInfo?.body,
  
  // AI Analysis from Gemini
  aiPriority: parsedData.messageAnalysis?.priority,
  aiCategory: parsedData.messageAnalysis?.category,
  aiSentiment: parsedData.messageAnalysis?.sentiment,
  aiUrgencyIndicators: parsedData.messageAnalysis?.urgencyIndicators,
  aiExtractedEntities: parsedData.messageAnalysis?.extractedEntities,
  
  // Full analysis for reference
  geminiFullAnalysis: parsedData
};
```

### 4. Intelligent Routing
Routes messages based on Gemini's analysis:
- **Urgent Priority**: Immediate human agent notification
- **Text Processing**: Enhanced Google AI analysis
- **Media Processing**: Vision AI with Gemini context

## Gemini Analysis Prompt

The Gemini node uses this comprehensive prompt:

```
You are an expert at analyzing WhatsApp Business API webhook payloads. 
Extract and structure all relevant information from the webhook data.

Return a JSON object with the following fields:

{
  "messageInfo": {
    "id": "message ID",
    "timestamp": "message timestamp", 
    "type": "message type (text, image, audio, document, video, etc.)",
    "from": "sender phone number",
    "body": "message text content (if text message)"
  },
  "senderInfo": {
    "phoneNumber": "formatted phone number",
    "name": "contact name if available",
    "profileName": "WhatsApp profile name if available"
  },
  "mediaInfo": {
    "hasMedia": true/false,
    "mediaType": "type of media if present",
    "mediaId": "media ID if present",
    "mimeType": "media MIME type if present",
    "filename": "original filename if document",
    "caption": "media caption if present"
  },
  "contextInfo": {
    "isReply": true/false,
    "quotedMessageId": "ID of quoted message if reply",
    "quotedMessage": "content of quoted message if reply"
  },
  "businessInfo": {
    "phoneNumberId": "business phone number ID",
    "displayPhoneNumber": "business display phone number",
    "webhookId": "webhook entry ID"
  },
  "messageAnalysis": {
    "priority": "low/medium/high/urgent based on content",
    "category": "inquiry/support/complaint/information/sales/etc",
    "requiresResponse": true/false,
    "language": "detected language of message",
    "sentiment": "positive/negative/neutral based on content",
    "urgencyIndicators": ["list of words/phrases indicating urgency"],
    "extractedEntities": ["important entities like names, dates, products mentioned"]
  }
}
```

## Enhanced Processing Flow

### Traditional Flow:
```
Webhook → Manual Extract → Basic Route → Process → Respond
```

### Gemini-Enhanced Flow:
```
Webhook → Gemini Analysis → Intelligent Parse → Smart Route → Enhanced Process → Contextual Response
```

## Integration with Existing APIs

The enhanced workflow integrates seamlessly with existing APIs:

### Enhanced Message Processing
```json
POST /api/n8n/marta/process-message
{
  "clientName": "{{ $json.senderName }}",
  "messageText": "{{ $json.messageBody }}",
  "geminiPreAnalysis": {
    "priority": "{{ $json.aiPriority }}",
    "category": "{{ $json.aiCategory }}",
    "sentiment": "{{ $json.aiSentiment }}",
    "entities": "{{ $json.aiExtractedEntities }}",
    "urgencyIndicators": "{{ $json.aiUrgencyIndicators }}"
  },
  "useGeminiPreAnalysis": true
}
```

### Benefits of Pre-Analysis:
1. **Faster Processing**: Initial analysis done by Gemini
2. **Better Context**: Google AI gets Gemini's insights
3. **Higher Accuracy**: Combined AI intelligence
4. **Smart Routing**: Immediate priority-based routing
5. **Cost Optimization**: Avoid redundant analysis

## Setup Instructions

### 1. Install n8n Langchain Integration
```bash
npm install @n8n/n8n-nodes-langchain
```

### 2. Configure Gemini Credentials
In n8n, add Google AI credentials:
- API Key: Your Google AI API key
- Project ID: Your Google Cloud project
- Model: `gemini-1.5-pro` or `gemini-1.5-flash`

### 3. Import Enhanced Workflow
Import `n8n-workflows/gemini-enhanced-whatsapp-workflow.json`

### 4. Configure Variables
Set these n8n variables:
- `WHATSAPP_ACCESS_TOKEN`: Your WhatsApp token
- `WHATSAPP_PHONE_NUMBER_ID`: Your phone number ID
- `URGENT_ALERT_WEBHOOK`: URL for urgent notifications
- `MARTA_API_BASE_URL`: Your Marta AI base URL

## Comparison: Before vs After

### Before (Manual Extraction):
```json
{
  "phone": "+1234567890",
  "messageText": "Urgente! Necesito ayuda con mi pedido",
  "contactName": "Unknown",
  "messageType": "text"
}
```

### After (Gemini Analysis):
```json
{
  "phone": "+1234567890",
  "messageText": "Urgente! Necesito ayuda con mi pedido",
  "contactName": "Cliente Premium",
  "messageType": "text",
  "aiPriority": "urgent",
  "aiCategory": "support",
  "aiSentiment": "negative",
  "aiUrgencyIndicators": ["Urgente", "Necesito ayuda"],
  "aiExtractedEntities": ["pedido"],
  "aiLanguage": "es",
  "geminiConfidence": 0.95
}
```

## Advanced Features

### 1. Multi-Language Support
Gemini automatically detects and analyzes messages in any language:
```json
{
  "messageAnalysis": {
    "language": "en",
    "translationNeeded": true,
    "translatedContent": "Urgent! I need help with my order"
  }
}
```

### 2. Media Context Analysis
For media messages, Gemini analyzes captions and context:
```json
{
  "mediaInfo": {
    "hasMedia": true,
    "mediaType": "image",
    "caption": "This is broken, please help",
    "contextAnalysis": {
      "isComplaint": true,
      "priority": "high",
      "category": "technical_support"
    }
  }
}
```

### 3. Smart Escalation
Automatic routing based on Gemini's analysis:
```javascript
if (aiPriority === 'urgent' || aiUrgencyIndicators.length > 0) {
  // Route to human agent immediately
  // Send alert with full context
}
```

## Performance Benefits

1. **Reduced API Calls**: Single Gemini call vs multiple service calls
2. **Faster Response**: Initial analysis provides immediate insights
3. **Better Accuracy**: AI understands context and nuance
4. **Cost Effective**: Intelligent routing avoids unnecessary processing
5. **Scalable**: Handles complex scenarios automatically

## Monitoring and Debugging

### Gemini Response Logging
```json
{
  "geminiProcessing": {
    "analysisTime": "234ms",
    "confidence": 0.94,
    "tokensUsed": 892,
    "model": "gemini-1.5-pro"
  }
}
```

### Fallback Mechanism
If Gemini analysis fails, the workflow falls back to basic extraction:
```javascript
catch (error) {
  console.error('Gemini analysis failed:', error);
  // Use basic webhook parsing as fallback
  return basicExtraction(originalWebhookData);
}
```

## Next Steps

1. **A/B Testing**: Compare Gemini vs traditional extraction
2. **Custom Training**: Fine-tune Gemini for your specific business domain
3. **Advanced Routing**: Implement more sophisticated routing rules
4. **Analytics Dashboard**: Track Gemini analysis accuracy and performance
5. **Multi-Modal Enhancement**: Process images, audio, and documents with context

This Gemini-powered approach transforms your WhatsApp automation from basic data extraction to intelligent customer interaction management with human-level understanding and contextual processing.