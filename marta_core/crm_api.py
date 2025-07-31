
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
from flask_cors import CORS
from marta_core.crm import CRM, Client
from marta_core.agent import ask_marta

app = Flask(__name__)
CORS(app)

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
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone_number=data["phone_number"],
        company=data.get("company"),
        position=data.get("position"),
    )
    crm.add_client(client)
    return jsonify(client.to_dict()), 201

@app.route("/client/<email>", methods=["GET"])
def get_client(email):
    client = crm.get_client(email)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"message": "Client not found"}), 404

@app.route("/clients", methods=["GET"])
def get_all_clients():
    clients = crm.get_all_clients()
    return jsonify([client.to_dict() for client in clients])

@app.route("/client/<email>", methods=["PUT"])
def update_client(email):
    data = request.get_json()
    crm.update_client(email, data)
    client = crm.get_client(email)
    if client:
        return jsonify(client.to_dict())
    return jsonify({"message": "Client not found"}), 404

@app.route("/sales_funnel", methods=["GET"])
def get_all_sales_funnel_entries():
    entries = crm.get_all_sales_funnel_entries()
    return jsonify([dict(entry) for entry in entries])

@app.route("/sales_funnel/<company_name>", methods=["GET"])
def get_sales_funnel_entry(company_name):
    entry = crm.get_sales_funnel_entry(company_name)
    if entry:
        return jsonify(dict(entry))
    return jsonify({"message": "Sales funnel entry not found"}), 404

@app.route("/sales_funnel", methods=["POST"])
def add_sales_funnel_entry():
    data = request.get_json()
    crm.add_sales_funnel_entry(data)
    return jsonify({"message": "Sales funnel entry created"}), 201

@app.route("/sales_funnel/<company_name>", methods=["PUT"])
def update_sales_funnel_entry(company_name):
    data = request.get_json()
    crm.update_sales_funnel_entry(company_name, data)
    return jsonify({"message": "Sales funnel entry updated"})

@app.route("/sales_funnel/<company_name>", methods=["DELETE"])
def delete_sales_funnel_entry(company_name):
    crm.delete_sales_funnel_entry(company_name)
    return jsonify({"message": "Sales funnel entry deleted"})

if __name__ == "__main__":

    app.run(debug=True)
