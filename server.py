from flask import Flask, request, jsonify
import requests
import json
import database
import os

app = Flask(__name__)

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

#TODO FIX MULTIPLE MESSAGES ISSUE
response_received = True

@app.route("/slack/actions", methods=["POST"])
def handle_action():
    """Handles Slack button responses."""

    data = request.form
    payload = json.loads(data["payload"])  
    action = payload["actions"][0]  
    action_value = action["value"]  
    user_id = payload["user"]["id"]
    response_url = payload["response_url"]

    action_type, cabinet, supply = action_value.split("|")

    if action_type == "yes":
        database.update_printer_supplies(cabinet, supply, 1)
        message = f"🔄 Information updated as provided by <@{user_id}>."
    elif action_type == "no":
        message = f"❌ <@{user_id}> please notify Robert about the shortage of {supply}."

    # Send message to Slack
    requests.post(response_url, json={"text": message})

    global response_received
    response_received = True

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
