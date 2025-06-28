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

# === Your chart key ===
chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"
base_url = "https://api.seats.io"

# === Step 1: Create a new draft version (overwrite previous draft)
create_draft_url = f"{base_url}/charts/{chart_key}/version/draft"
r = requests.post(create_draft_url, auth=(seatsio_api_key, ""))
if r.status_code not in [200, 201]:
    raise Exception(f"❌ Failed to create draft version: {r.status_code} - {r.text}")
print("✅ Draft version created successfully.")

# === Step 2: Google Sheets setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").sheet1
rows = sheet.get_all_records()

# === Step 3: Prepare drawing objects
objects = []
for row in rows:
    objects.append({
        "type": "seat",
        "label": row["Seat Label"],
        "x": float(row["X"]),
        "y": float(row["Y"]),
        "category": row["Category"]
    })

drawing_payload = {
    "objects": objects
}

# === Step 4: Upload drawing to draft chart
upload_url = f"{base_url}/charts/{chart_key}/version/draft/drawing"
res = requests.put(
    upload_url,
    auth=(seatsio_api_key, ""),
    headers={"Content-Type": "application/json"},
    json=drawing_payload
)

if res.status_code == 200:
    print("✅ Seat layout uploaded successfully to draft.")
else:
    print(f"❌ Failed to upload drawing: {res.status_code} - {res.text}")
