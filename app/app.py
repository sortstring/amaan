"""This module contains the Flask application that creates a flow for the WhatsApp Business API."""
import os
import json
import uuid
import requests
from flask import Flask, request, make_response
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')

messaging_url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
auth_header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
messaging_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

created_flow_id = None  # pylint: disable=invalid-name


@app.route("/create-flow", methods=["POST"])
def create_flow():
    """Create a flow for the WhatsApp Business API."""
    flow_base_url = f"https://graph.facebook.com/v18.0/{WHATSAPP_BUSINESS_ACCOUNT_ID}/flows"
    flow_creation_payload = {
        "name": "survey_flow",
        "categories": '["SURVEY"]'
    }
    response = requests.post(
        flow_base_url,
        headers=auth_header,
        data=flow_creation_payload,
        timeout=5
    )
    try:
        global created_flow_id  # pylint: disable=global-statement
        created_flow_id = response.json()["id"]
        upload_flow_json(f"https://graph.facebook.com/v18.0/{created_flow_id}/assets")
        publish_flow(created_flow_id)
        return make_response("FLOW CREATED", 200)
    except requests.exceptions.RequestException:
        return make_response("ERROR", 500)


def upload_flow_json(url):
    """Upload the flow JSON to the WhatsApp Business API."""
    with open("survey.json", "rb") as f:
        files = [("file", ("survey.json", f, "application/json"))]
        response = requests.post(
            url, headers=auth_header, files=files, timeout=5
        )
        print(response.json())


def publish_flow(flow_id):
    """Publish the flow to the WhatsApp Business API."""
    publish_url = f"https://graph.facebook.com/v18.0/{flow_id}/publish"
    requests.post(
        publish_url, headers=auth_header, timeout=5
    )


def send_flow(flow_id, recipient_phone_number):
    """Send the flow to a recipient."""
    flow_token = str(uuid.uuid4())
    flow_payload = json.dumps({
        "type": "flow",
        "header": {"type": "text", "text": "Survey"},
        "body": {"text": "Please complete our survey."},
        "footer": {"text": "Click below to start"},
        "action": {
            "name": "flow",
            "parameters": {
                "flow_message_version": "3",
                "flow_token": flow_token,
                "flow_id": flow_id,
                "flow_cta": "Start",
                "flow_action": "navigate",
                "flow_action_payload": {"screen": "SURVEY_SCREEN"}
            }
        }
    })
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(recipient_phone_number),
        "type": "interactive",
        "interactive": json.loads(flow_payload),
    })
    requests.post(
        messaging_url,
        headers=messaging_headers,
        data=payload,
        timeout=5
    )
    print("MESSAGE SENT")


@app.route("/webhook", methods=["GET"])
def webhook_get():
    """Handle the GET request from the WhatsApp Business API."""
    if request.args.get("hub.mode") == "subscribe" and \
            request.args.get("hub.verify_token") == VERIFY_TOKEN:

        return make_response(request.args.get("hub.challenge"), 200)

    return make_response("Forbidden", 403)


@app.route("/webhook", methods=["POST"])
def webhook_post():
    """Handle the POST request from the WhatsApp Business API."""
    data = json.loads(request.get_data())
    if data["entry"][0]["changes"][0]["value"].get("messages"):
        user_phone_number = data["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        send_flow(created_flow_id, user_phone_number)
    return make_response("PROCESSED", 200)
