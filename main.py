import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# === Load Google Credentials ===
google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if not google_creds:
    raise Exception("❌ GOOGLE_CREDENTIALS_JSON secret not set.")

creds_dict = json.loads(google_creds)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# === Open Google Sheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet_name = "Grand Theatre Seating Plan"
sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
rows = sheet.get_all_records()

# === Seats.io setup ===
api_key = os.environ.get("SEATSIO_API_KEY")
if not api_key:
    raise Exception("❌ SEATSIO_API_KEY secret not set.")

headers = {
    "Authorization": f"Secret {api_key}",
    "Content-Type": "application/json"
}

chart_key = "49e1934d-4a13-e089-8344-8d01ace4e8db"
base_url = "https://api.seats.io"

# === Clear the chart first ===
print("🧹 Clearing chart before adding new seats...")
requests.post(f"{base_url}/charts/{chart_key}/actions/clear", headers=headers)

# === Add each seat ===
for row in rows:
    label = row["Seat Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]

    payload = {
        "label": label,
        "coordinates": {"x": x, "y": y},
        "category": category
    }

    r = requests.post(
        f"{base_url}/charts/{chart_key}/drawing/seats",
        headers=headers,
        json=payload
    )

    if r.status_code == 201:
        print(f"✅ Seat {label} created.")
    else:
        print(f"❌ Failed to create seat {label}: {r.status_code} - {r.text}")
