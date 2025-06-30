import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Config ---
SEATSIO_API_KEY = os.environ["SEATSIO_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"
BASE_URL = "https://api.seats.io"

# --- Google Sheets ---
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(GOOGLE_CREDENTIALS_JSON),
    ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)
rows = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME).get_all_records()

# --- Create draft ---
draft_url = f"{BASE_URL}/charts/{CHART_KEY}/version/draft"
resp = requests.post(draft_url, auth=(SEATSIO_API_KEY, ""))
resp.raise_for_status()

# --- Add seats via REST endpoint ---
add_url = f"{BASE_URL}/charts/{CHART_KEY}/version/draft/actions/add-seats"
for row in rows:
    seat = {
        "label": row["Seat Label"],
        "x": float(row["X"]),
        "y": float(row["Y"]),
        "category": row["Category"]
    }
    body = {"seats": [seat]}
    r = requests.post(add_url, json=body, auth=(SEATSIO_API_KEY, ""))
    if r.status_code != 200:
        print("❌", seat, r.status_code, r.text)

# --- Publish draft ---
pub = f"{BASE_URL}/charts/{CHART_KEY}/version/draft/publish"
rp = requests.post(pub, auth=(SEATSIO_API_KEY, ""))
rp.raise_for_status()

print("✅ All seats uploaded and draft published.")
