from flask import Flask, request, jsonify
import requests
import json
import database
import os
from dotenv import load_dotenv
    
load_dotenv()

app = Flask(__name__)

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

@app.route("/slack/actions", methods=["POST"])
def handle_action():
    data = request.form
    payload = json.loads(data["payload"])
    
    if payload["type"] == "view_submission":
        values = payload["view"]["state"]["values"]
        cabinet = values["cabinet_block"]["cabinet_action"]["selected_option"]["value"]
        supply = values["supply_block"]["supply_action"]["selected_option"]["value"]
        user_id = payload["user"]["id"]

        # Subtract 1 from the selected supply
        database.update_printer_supplies(cabinet, supply, -1)

        return jsonify({"response_action": "clear"})  # Closes modal

    # Handle button press logic
    action = payload["actions"][0]
    action_value = action["value"]
    user_id = payload["user"]["id"]
    response_url = payload["response_url"]

    action_type, cabinet, supply = action_value.split("|")

    if action_type == "yes":
        database.update_printer_supplies(cabinet, supply, 1)
        message = f"🔄 Info updated by <@{user_id}>."
    elif action_type == "no":
        message = f"❌ <@{user_id}>, please notify Robert about the {supply} shortage."

    requests.post(response_url, json={"text": message})
    return jsonify({"status": "ok"})


@app.route("/slack/command", methods=["POST"])
def open_modal():
    trigger_id = request.form.get("trigger_id")

    cabinets = ["Music", "Science", "Maxey", "Olin", "Penrose", "Reid"]
    supplies = ["tonerBlack", "tonerCian", "tonerMagenta", "tonerYellow",
                "drumBlack", "drumCian", "drumMagenta", "drumYellow",
                "belt", "fuser"]

    modal_view = {
        "type": "modal",
        "callback_id": "supply_used_modal",
        "title": {"type": "plain_text", "text": "Supply Used"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "cabinet_block",
                "label": {"type": "plain_text", "text": "Select Cabinet"},
                "element": {
                    "type": "static_select",
                    "action_id": "cabinet_action",
                    "options": [
                        {"text": {"type": "plain_text", "text": c}, "value": c}
                        for c in cabinets
                    ]
                }
            },
            {
                "type": "input",
                "block_id": "supply_block",
                "label": {"type": "plain_text", "text": "Select Supply"},
                "element": {
                    "type": "static_select",
                    "action_id": "supply_action",
                    "options": [
                        {"text": {"type": "plain_text", "text": s}, "value": s}
                        for s in supplies
                    ]
                }
            }
        ]
    }

    response = requests.post(
        "https://slack.com/api/views.open",
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "trigger_id": trigger_id,
            "view": modal_view
        })
    )

    return "", 200


if __name__ == "__main__":
    app.run(port=5000)
