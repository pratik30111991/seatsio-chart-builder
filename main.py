import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIG ==========
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
CHART_KEY = "e38f6670-8b39-46b7-b22d-7de6187d0cde"
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Sheet1"
SEATSIO_BASE_URL = "https://api.seats.io"  # Fixed to global endpoint
# ==============================

if not SEATSIO_API_KEY:
    raise Exception("❌ SEATSIO_API_KEY secret not set.")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("❌ GOOGLE_CREDENTIALS_JSON secret not set.")

creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()

print("🧹 Clearing chart before adding new seats...")

# Create draft version of chart
draft_url = f"{SEATSIO_BASE_URL}/charts/{CHART_KEY}/version/draft"
draft_res = requests.post(draft_url, auth=(SEATSIO_API_KEY, ""))
if draft_res.status_code != 200:
    raise Exception(f"❌ Error creating draft: {draft_res.text}")

drawing_url = f"{SEATSIO_BASE_URL}/charts/{CHART_KEY}/drawing/seats"

print("🪚 Uploading seats to chart...")

for row in data:
    try:
        seat = row.get("Seat")
        label = row.get("Label")
        x = float(row.get("X"))
        y = float(row.get("Y"))
        category = int(row.get("Category"))

        seat_data = {
            "label": label,
            "x": x,
            "y": y,
            "category": category,
            "leftNeighbour": None,
            "rightNeighbour": None,
            "accessible": False
        }

        res = requests.post(
            drawing_url,
            json=seat_data,
            auth=(SEATSIO_API_KEY, "")
        )

        if res.status_code != 200:
            print(f"❌ Failed to create seat {seat}: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"❌ Error processing seat {row.get('Seat')}: {e}")

print("✅ Done uploading all seats.")
