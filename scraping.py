import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import requests
import json
import database
import server
import os
from dotenv import load_dotenv

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')  
SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID') 

OPEN_HOUR = datetime.strptime("08:00", "%H:%M").time()
CLOSE_HOUR = datetime.strptime("17:00", "%H:%M").time()

CABINETS = {'Music', 'Science', 'Maxey', 'Olin', 'Penrose', 'Reid'}

# Function to scrape printer statuses
def scrape_printer_status():
    url = os.getenv('URL')
    now = datetime.now().time()
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    printers = soup.find_all("td", width="18%")
    
    if not printers:
        print("Status website issue.")
        return

    reidPrinter = 1

    for printer in printers:
        printer_name = printer.text.strip()

        # Handle that both Reid printers have the same name
        if printer_name == "Reid Campus Center - 1st Floor - Fireplace Lounge":
            if reidPrinter == 1:
                printer_name += " #1"
                reidPrinter = 2
            elif reidPrinter == 2:
                printer_name += " #2"
                reidPrinter = 3

        status_td = printer.find_next_sibling("td").text.lower()

        if "down" or "error" in status_td:
            isPrinterDown = True
        else:
            isPrinterDown = False

        status_td = printer.find_next_siblings("td")

        printer_percentages = {'tonerBlack':4, 'tonerCian':status_td[3].text, 
                               'tonerMagenta':status_td[4].text, 'tonerYellow':status_td[5].text,
                               'drumBlack':status_td[6].text,'drumCian':status_td[7].text,'drumMagenta':status_td[8].text,
                               'drumYellow':status_td[9].text,'belt':status_td[10].text,'fuser':status_td[11].text}
        
        # Determine cabinet
        cabinet = next((c for c in CABINETS if c in printer_name), None)

        for supply, value in printer_percentages.items():
            if int(value) <= 5 and database.get_quantity_available(cabinet, supply) <= 0 and OPEN_HOUR <= now <= CLOSE_HOUR:
                send_slack_message(cabinet, supply, isPrinterDown)

            #TODO!!!
            # if int(value) == 100 and database.get_quantity_available(cabinet, supply) > 0:
            #     database.update_printer_supplies(cabinet, supply, -1)

def send_slack_message(cabinet, supply, isPrinterDown):
    """Sends a Slack message with Yes/No buttons."""

    time.sleep(30)
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": SLACK_CHANNEL_ID,
        "text": f"⚠️ Alert: Bring a `{supply}` to the cabinet on `{cabinet}`.\nMark \"Yes\" when this has been done. Mark \"No\" if there are no supplies available.",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"⚠️ Alert: Bring a `{supply}` to the cabinet on `{cabinet}`.\nMark \"Yes\" when this has been done. Mark \"No\" if there are no supplies available."}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Yes ✅"},
                        "style": "primary",
                        "value": f"yes|{cabinet}|{supply}",
                        "action_id": "yes_action"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "No ❌"},
                        "style": "danger",
                        "value":  f"no|{cabinet}|{supply}",
                        "action_id": "no_action",
                    }
                ]
            }
        ]
    }

    if server.response_received:
        requests.post(url, headers=headers, data=json.dumps(payload))
        server.response_received = False

while True: 
    scrape_printer_status()
    time.sleep(30)