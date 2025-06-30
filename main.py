import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# === Config ===
SEATSIO_API_KEY = os.environ["SEATSIO_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"
BASE_URL = "https://api.seats.io"

# === Google Sheets ===
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
rows = sheet.get_all_records()

# === Create Draft ===
print("🧪 Creating draft version...")
res = requests.post(f"{BASE_URL}/charts/{CHART_KEY}/version/draft", auth=(SEATSIO_API_KEY, ""))
if res.status_code != 200:
    raise Exception(f"❌ Error creating draft: {res.text}")
print("✅ Draft version created.")

# === Add Seats ===
print("🎯 Adding seats to chart...")
add_url = f"{BASE_URL}/charts/{CHART_KEY}/version/draft/actions/add-seats"

for row in rows:
    seat = {
        "label": row["Seat Label"],
        "x": float(row["X"]),
        "y": float(row["Y"]),
        "category": row["Category"]
    }

    body = {"seats": [seat]}
    r = requests.post(add_url, auth=(SEATSIO_API_KEY, ""), json=body)

    if r.status_code == 200:
        print(f"✅ Seat {seat['label']} added.")
    else:
        print(f"❌ Failed to add seat {seat['label']}: {r.status_code} - {r.text}")

# === Publish Draft ===
print("🚀 Publishing draft...")
pub = requests.post(f"{BASE_URL}/charts/{CHART_KEY}/version/draft/publish", auth=(SEATSIO_API_KEY, ""))
if pub.status_code == 200:
    print("✅ Chart published successfully.")
else:
    raise Exception(f"❌ Failed to publish draft: {pub.text}")
