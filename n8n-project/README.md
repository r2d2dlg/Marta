
# Marta Assistant n8n Workflow

This workflow allows you to interact with the Marta AI assistant using n8n.

## Prerequisites

*   n8n instance running
*   Marta AI assistant project running on `http://localhost:3000`

## Setup

1.  **Import the workflow:**
    *   Open your n8n instance.
    *   Go to **Workflows** and click on **Import from File**.
    *   Select the `Marta-Assistant.json` file from this directory.

2.  **Start the Marta AI assistant:**
    *   Follow the instructions in the main `README.md` file of the `marta_ai` project to start the application.

## Usage

1.  **Activate the workflow:**
    *   In the n8n UI, open the **Marta Assistant** workflow.
    *   Click on the **Activate** button in the top right corner.

2.  **Trigger the webhook:**
    *   Send a POST request to the webhook URL provided in the Webhook node.
    *   The request body should be a JSON object with a `query` property.

    **Example using curl:**

    ```bash
    curl -X POST http://<your-n8n-instance>/webhook/marta-assistant -H "Content-Type: application/json" -d '{"query": "hola marta, tienes correos nuevos?"}'
    ```
