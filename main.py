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

# === Your Seats.io chart key ===
chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# === Read the spreadsheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).sheet1
data = sheet.get_all_records()

# === Prepare the chart drawing in Seats.io format ===
objects = []

for row in data:
    label = row["Seat Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]

    seat_object = {
        "type": "seat",
        "label": label,
        "x": x,
        "y": y,
        "category": category
    }
    objects.append(seat_object)

drawing_payload = {
    "objects": objects
}

# === Upload the chart drawing to Seats.io ===
base_url = "https://api.seats.io"
url = f"{base_url}/charts/{chart_key}/drawing"

response = requests.post(
    url,
    auth=(seatsio_api_key, ""),
    headers={"Content-Type": "application/json"},
    json=drawing_payload
)

if response.status_code == 200:
    print("✅ Chart drawing uploaded successfully.")
else:
    print(f"❌ Failed to upload drawing: {response.status_code} - {response.text}")
