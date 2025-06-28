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

# === CHART KEY (replace with your actual key) ===
chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# === Open the specific worksheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).worksheet("Grand Theatre Seating Plan")
data = sheet.get_all_records()

# === Seats.io Setup ===
base_url = "https://api.seats.io"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Secret {seatsio_api_key}"
}

# === Clear and create draft version ===
r = requests.post(f"{base_url}/charts/{chart_key}/version/draft/actions/create", headers=headers)
if r.status_code != 200:
    raise Exception(f"❌ Failed to create draft version: {r.status_code} - {r.text}")

# === Add each seat ===
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
        f"{base_url}/charts/{chart_key}/version/draft/seats", headers=headers, json=payload
    )

    if res.status_code == 201:
        print(f"✅ Seat {label} created.")
    else:
        print(f"❌ Failed to create seat {label}: {res.status_code} - {res.text}")

# === Publish the draft ===
publish = requests.post(f"{base_url}/charts/{chart_key}/version/publish", headers=headers)
if publish.status_code == 204:
    print("✅ Chart published successfully.")
else:
    print(f"❌ Failed to publish chart: {publish.status_code} - {publish.text}")
