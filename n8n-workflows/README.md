# n8n Workflows for Marta AI

This directory contains n8n workflow templates for integrating WhatsApp Business with your CRM using Marta AI.

## Available Workflows

### 1. Basic WhatsApp Workflow (`basic-whatsapp-workflow.json`)
**Best for**: Getting started with basic WhatsApp to CRM integration

**Features**:
- Simple message extraction from WhatsApp webhooks
- Basic client lookup and creation
- Standard Marta AI message processing
- Response generation based on analysis

**Setup Requirements**:
- Marta AI running on `http://localhost:9002`
- Environment variables: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`

### 2. Simple Gemini Workflow (`simple-gemini-workflow.json`)
**Best for**: Adding AI intelligence without complex integrations

**Features**:
- Direct Gemini API integration for message analysis
- Priority and sentiment detection
- Entity extraction from messages
- AI-enhanced CRM updates
- Smart urgency detection

**Setup Requirements**:
- Google AI API key: `GOOGLE_AI_API_KEY`
- Marta AI running on `http://localhost:9002`
- Environment variables: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`

## Quick Start

### Option 1: Basic Integration
1. Import `basic-whatsapp-workflow.json` into n8n
2. Configure WhatsApp webhook URL to point to the n8n webhook
3. Set up environment variables
4. Test with a WhatsApp message

### Option 2: AI-Enhanced Integration
1. Import `simple-gemini-workflow.json` into n8n
2. Add your Google AI API key to n8n variables
3. Configure WhatsApp webhook URL
4. Test with a WhatsApp message

## Environment Variables Required

### For Basic Workflow:
```bash
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

### For Gemini Workflow (additional):
```bash
GOOGLE_AI_API_KEY=your_google_ai_api_key
```

## Workflow Flow

### Basic Workflow:
```
WhatsApp Webhook → Extract Data → Check Client → Create/Update Client → Process with Marta → Generate Response → Send WhatsApp
```

### Gemini Workflow:
```
WhatsApp Webhook → Extract Data → Gemini Analysis → Parse AI Results → Update CRM with AI Insights → Check Urgency → Generate Response → Send WhatsApp
```

## Advanced Features

### Gemini AI Analysis Provides:
- **Priority Detection**: Automatically identifies urgent messages
- **Sentiment Analysis**: Positive, negative, or neutral sentiment
- **Category Classification**: Support, sales, inquiry, complaint
- **Entity Extraction**: Names, products, dates mentioned in messages
- **Smart Routing**: Different handling based on message priority

### CRM Integration Features:
- **Automatic Client Creation**: New clients added automatically
- **Interaction History**: All messages logged with timestamps
- **AI Insights Storage**: Sentiment and priority data stored
- **Contact Updates**: Last contact date automatically updated

## Customization

### Modifying AI Analysis:
Edit the Gemini prompt in the "Gemini Analysis" node to customize:
- Analysis categories
- Priority levels
- Entity types to extract
- Response triggers

### Adding Custom Routing:
Add conditional nodes after AI analysis to:
- Route urgent messages to human agents
- Send different responses based on sentiment
- Trigger specific actions for certain categories

### Integration with Other Services:
Extend workflows to integrate with:
- Email systems
- Calendar applications
- Project management tools
- Customer support platforms

## Troubleshooting

### Common Issues:
1. **Webhook not receiving messages**: Check webhook URL and verify token
2. **Gemini API errors**: Verify API key and quota limits
3. **Client creation failures**: Check Marta AI API accessibility
4. **Response generation errors**: Verify all required fields are passed

### Debug Mode:
Enable debug mode in n8n to see:
- Webhook payload structure
- AI analysis results
- API response details
- Error messages

## Performance Tips

1. **Use appropriate Gemini model**: `gemini-pro` for complex analysis, `gemini-pro-vision` for images
2. **Optimize prompts**: Keep prompts focused and specific
3. **Implement caching**: Cache frequently used AI results
4. **Monitor quotas**: Keep track of Google AI API usage
5. **Error handling**: Implement fallbacks for API failures

## Security Considerations

1. **Protect API keys**: Store in n8n environment variables, never in workflow code
2. **Validate webhooks**: Implement webhook signature validation
3. **Limit access**: Restrict webhook URLs to known sources
4. **Monitor usage**: Track API calls and unusual activity
5. **Data privacy**: Ensure customer data handling complies with regulations

## Support

For issues with:
- **n8n workflows**: Check n8n documentation and community
- **Marta AI integration**: Refer to project documentation
- **Google AI APIs**: Check Google AI documentation and status page
- **WhatsApp Business API**: Refer to Meta developer documentation