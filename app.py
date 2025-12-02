from flask import Flask, jsonify, request
from supabase import create_client, Client
import os

app = Flask(__name__)

# Initialize Supabase Client
# We get these secrets from the Environment Variables (see Phase 4)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Create the connection
supabase: Client = create_client(url, key)


@app.route("/")
def home():
    return "Hello! The service is running."


@app.route("/users", methods=["GET"])
def get_users():
    # Query the 'users' table in Supabase
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)


@app.route("/add_user", methods=["POST"])
def add_user():
    # Insert a new user sent via JSON
    data = request.json
    response = supabase.table("users").insert(data).execute()
    return jsonify(response.data)


if __name__ == "__main__":
    app.run(debug=True)
