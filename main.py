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

# === Chart key (static one)
chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"

# === Step 1: Create draft version
draft_url = f"https://api.seats.io/charts/{chart_key}/version/draft/actions/create"
r = requests.post(draft_url, auth=(seatsio_api_key, ""))
if r.status_code != 201:
    raise Exception(f"❌ Failed to create draft version: {r.status_code} - {r.text}")
print("✅ Draft version created.")

# === Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).sheet1
data = sheet.get_all_records()

# === Build drawing payload
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

# === Step 2: Upload drawing to draft
upload_url = f"https://api.seats.io/charts/{chart_key}/version/draft/drawing"
response = requests.post(
    upload_url,
    auth=(seatsio_api_key, ""),
    headers={"Content-Type": "application/json"},
    json=drawing_payload
)

if response.status_code == 200:
    print("✅ Seats added to draft chart.")
else:
    print(f"❌ Failed to upload drawing: {response.status_code} - {response.text}")
