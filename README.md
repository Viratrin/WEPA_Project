# Printer Supply Monitoring System

This project monitors printer supply levels across campus buildings and automates Slack alerts when supplies are low. It also handles Slack button responses to update inventory.

## Features

- Scrapes printer status from a public URL.
- Checks toner/drum levels and compares against inventory.
- Sends interactive Slack alerts when supply is needed.
- Updates a shared Excel sheet as the source of truth.
- Flask server to handle Slack button responses.

## Tech Stack

- Python (requests, BeautifulSoup, Flask, pandas)
- Slack API
- Excel (.xlsx) for persistent storage
- `.env` for API tokens and channel IDs

## Setup


1. Make sure `printer_supplies.xlsx` exists and follows the expected schema.

2. Run the Flask server:
   ```bash
   python server.py
   ```
3. Run ngrok
   ```bash
    ngrok http 5000
   ```
4. Start the monitoring script:
   ```bash
   python scraping.py
   ```

## Notes

- Script checks every 10 minutes.
- Alerts are sent only during working hours (8 AM–5 PM).
- Manual inventory is updated based on Slack responses.
