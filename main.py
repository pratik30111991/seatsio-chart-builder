import gspread
import json
import os
import requests
from oauth2client.service_account import ServiceAccountCredentials

# === Load Google Credentials from file (set via GitHub Actions) ===
google_creds_path = os.environ.get("GOOGLE_CREDENTIALS_FILE")
if not google_creds_path:
    raise Exception("❌ GOOGLE_CREDENTIALS_FILE env variable not set.")

with open(google_creds_path, 'r') as f:
    creds_dict = json.load(f)

# === Load Seats.io API Key ===
seatsio_api_key = os.environ.get("SEATSIO_API_KEY")
if not seatsio_api_key:
    raise Exception("❌ SEATSIO_API_KEY secret not set.")

# === Chart Key ===
chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"  # ✅ your actual chart key

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# === Open your sheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet_name = "Grand Theatre Seating Plan"
sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
data = sheet.get_all_records()

# === Seats.io API Setup ===
base_url = "https://api.seats.io"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Secret {seatsio_api_key}"
}

# === Clear any existing draft ===
r = requests.post(f"{base_url}/charts/{chart_key}/version/draft", headers=headers)
if r.status_code != 200:
    raise Exception(f"❌ Failed to create draft version: {r.status_code} - {r.text}")

# === Upload each seat ===
for row in data:
    label = row["Seat Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]

    payload = {
        "label": label,
        "x": x,
        "y": y,
        "category": category
    }

    res = requests.post(
        f"{base_url}/charts/{chart_key}/version/draft/seats",
        headers=headers,
        json=payload
    )

    if res.status_code == 201:
        print(f"✅ Seat {label} created.")
    else:
        print(f"❌ Failed to create seat {label}: {res.status_code} - {res.text}")

# === Publish the draft ===
pub_res = requests.post(f"{base_url}/charts/{chart_key}/version/publish", headers=headers)
if pub_res.status_code == 204:
    print("✅ Chart published successfully.")
else:
    print(f"❌ Failed to publish chart: {pub_res.status_code} - {pub_res.text}")
