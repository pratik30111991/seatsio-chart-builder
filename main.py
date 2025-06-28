# main.py
import gspread
import json
import os
import requests
from oauth2client.service_account import ServiceAccountCredentials

# === Load Google Credentials from GitHub Secret ===
google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if not google_creds:
    raise Exception("❌ GOOGLE_CREDENTIALS_JSON secret not set.")
creds_dict = json.loads(google_creds)

# === Load Seats.io API Key from Secret ===
seatsio_api_key = os.environ.get("SEATSIO_API_KEY")
if not seatsio_api_key:
    raise Exception("❌ SEATSIO_API_KEY secret not set.")

# === Chart Key (V2 CHART ONLY) ===
chart_key = "e38f6670-8b39-46b7-b22d-7de6187d0cde"

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# === Open your sheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).worksheet("Grand Theatre Seating Plan")
data = sheet.get_all_records()

# === Seats.io Setup ===
base_url = "https://api.seats.io"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Secret {seatsio_api_key}"
}

print("🪚 Uploading seats to chart...")

for row in data:
    label = row["Seat Label"].strip()
    try:
        x = float(row["X"])
        y = float(row["Y"])
    except Exception:
        print(f"⚠️ Skipping seat {label} due to invalid X or Y.")
        continue
    category = row["Category"].strip()

    payload = {
        "label": label,
        "x": x,
        "y": y,
        "category": category
    }

    res = requests.post(
        f"{base_url}/charts/{chart_key}/drawing/seats",
        headers=headers,
        json=payload
    )

    if res.status_code == 201:
        print(f"✅ Seat {label} created.")
    else:
        print(f"❌ Failed to create seat {label}: {res.status_code} - {res.text}")

print("✅ All done uploading seats.")
