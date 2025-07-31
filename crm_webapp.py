
import os
import requests
from flask import Flask, render_template, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# The base URL for the CRM API
CRM_API_URL = "http://127.0.0.1:5000"

@app.route('/')
def client_list():
    try:
        response = requests.get(f"{CRM_API_URL}/clients")
        response.raise_for_status()  # Raise an exception for bad status codes
        clients = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Error fetching clients: {e}", "danger")
        clients = []
    return render_template('crm_clients.html', clients=clients)

@app.route('/client/<email>')
def client_profile(email):
    try:
        response = requests.get(f"{CRM_API_URL}/client/{email}")
        response.raise_for_status()
        client = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Error fetching client details: {e}", "danger")
        client = None
    return render_template('crm_client_profile.html', client=client)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
