
import sys
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request, jsonify
from marta_core.crm import CRM, Client
from marta_core.agent import ask_marta

app = Flask(__name__)

crm = CRM()

@app.route("/marta", methods=["POST"])
def marta_endpoint():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    response = ask_marta(query)
    return jsonify({"response": response})


@app.route("/client", methods=["POST"])
def add_client():
    data = request.get_json()
    client = Client(
        name=data["name"],
        email=data["email"],
        phone_number=data["phone_number"],
        company=data.get("company"),
    )
    crm.add_client(client)
    return jsonify(client.to_dict()), 201

@app.route("/client/<email>", methods=["GET"])
def get_client(email):
    client = crm.get_client(email)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"message": "Client not found"}), 404

@app.route("/client/<email>", methods=["PUT"])
def update_client(email):
    data = request.get_json()
    crm.update_client(email, data["notes"])
    client = crm.get_client(email)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"message": "Client not found"}), 404

if __name__ == "__main__":

    app.run(debug=True)
