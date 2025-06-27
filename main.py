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

# === Define your Seats.io chart key ===
chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# === Open your sheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).sheet1
data = sheet.get_all_records()

# === Prepare data to push to Seats.io ===
base_url = "https://api.seats.io"
headers = {
    "Content-Type": "application/json",
}

for row in data:
    seat_label = row["Seat Label"]  # 👈 using your exact column
    x = row["X"]
    y = row["Y"]
    category = row["Category"]

    payload = {
        "label": seat_label,
        "categoryKey": category,
        "x": float(x),
        "y": float(y)
    }

    # === API call to create seat
    response = requests.post(
        f"{base_url}/charts/{chart_key}/seats",
        auth=(seatsio_api_key, ""),
        headers=headers,
        json=payload
    )

    if response.status_code == 201:
        print(f"✅ Seat {seat_label} created.")
    else:
        print(f"❌ Failed to create seat {seat_label}: {response.status_code} - {response.text}")
