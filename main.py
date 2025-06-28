import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIG ==========
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"
SEATSIO_BASE_URL = "https://api.seats.io"
# ============================

if not SEATSIO_API_KEY:
    raise Exception("❌ SEATSIO_API_KEY secret not set.")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("❌ GOOGLE_CREDENTIALS_JSON secret not set.")

# ✅ Google Sheet Auth
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()

# ✅ Upload seats directly (no draft creation needed)
seats_url = f"{SEATSIO_BASE_URL}/charts/{CHART_KEY}/seats"

print("🪚 Uploading seats to chart...")

for row in data:
    try:
        label = str(row.get("Seat Label")).strip()
        x = float(row.get("X"))
        y = float(row.get("Y"))
        category = str(row.get("Category")).strip()

        seat_payload = {
            "seats": [{
                "label": label,
                "x": x,
                "y": y,
                "category": category
            }]
        }

        res = requests.post(seats_url, json=seat_payload, auth=(SEATSIO_API_KEY, ""))

        if res.status_code != 200:
            print(f"❌ Failed to create seat {label}: {res.status_code} - {res.text}")
        else:
            print(f"✅ Seat {label} created.")

    except Exception as e:
        print(f"❌ Error in row: {e}")

print("✅ All seats uploaded.")
