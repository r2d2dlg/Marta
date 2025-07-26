
# Project: Marta - n8n Integration with CRM, WhatsApp, and Email

## Project Vision

The goal of this project is to create an automated system that uses Marta to enrich a central CRM with client information from WhatsApp messages and emails. This will provide a unified view of all client interactions and enable more effective communication and relationship management.

## CRM Requirements

The CRM will be a basic client management system with the following features:

*   **Client Database**: A simple database to store client information.
*   **Client Profile**: Each client will have a profile with the following fields:
    *   `Name`: The client's full name.
    *   `Email`: The client's email address.
    *   `Phone Number`: The client's WhatsApp number.
    *   `Company`: The client's company (optional).
    *   `Notes`: A summary of key information and interactions with the client.
    *   `Last Contact`: The date of the last interaction with the client.

## Integration Points

The system will be integrated using n8n workflows that connect the following services:

*   **Email**: The system will monitor a designated inbox for new emails from clients.
*   **WhatsApp**: The system will connect to a WhatsApp Business account to receive messages from clients.
*   **CRM**: The CRM will be updated with information from emails and WhatsApp messages.

## Marta's Role

Marta will be the intelligent core of the system, responsible for the following tasks:

*   **Message Processing**: Marta will analyze incoming emails and WhatsApp messages to identify the client and extract relevant information.
*   **Information Summarization**: Marta will summarize the key points from each interaction and update the client's `Notes` in the CRM.
*   **Sentiment Analysis**: Marta can optionally perform sentiment analysis on messages to gauge client satisfaction.

## n8n Workflow

The n8n workflow will be designed as follows:

1.  **Trigger**: The workflow will be triggered by:
    *   A new email in the designated inbox.
    *   A new message in the connected WhatsApp account.
2.  **Client Identification**: The workflow will identify the client based on their email address or phone number.
    *   If the client exists in the CRM, the workflow will retrieve their profile.
    *   If the client does not exist, the workflow will create a new profile.
3.  **Marta Processing**: The workflow will send the message content to Marta for processing.
4.  **CRM Update**: The workflow will update the client's profile in the CRM with the information provided by Marta.
    *   The `Notes` field will be updated with a summary of the interaction.
    *   The `Last Contact` date will be updated to the current date.
5.  **Notification**: The workflow can optionally send a notification to a designated user or channel to alert them of the new interaction.
