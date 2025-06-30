import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

SEATSIO_API_KEY = os.environ["SEATSIO_API_KEY"]
GOOGLE_CREDS = os.environ["GOOGLE_CREDENTIALS_JSON"]
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

creds_dict = json.loads(GOOGLE_CREDS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
gc = gspread.authorize(creds)
rows = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME).get_all_records()

BASE = "https://api.seatsio.com"  # or api-in.seatsio.com if that's your region

# 1) Create chart
r = requests.post(f"{BASE}/charts", auth=(SEATSIO_API_KEY, ""))
r.raise_for_status()
chart_key = r.json()["key"]
print("✅ Chart key:", chart_key)

# 2) Draft
requests.post(f"{BASE}/charts/{chart_key}/version/draft", auth=(SEATSIO_API_KEY, ""))

# 3) Add seats
for row in rows:
    data = {
        "label": row["Seat Label"],
        "x": float(row["X"]),
        "y": float(row["Y"]),
        "category": row["Category"]
    }
    resp = requests.post(
        f"{BASE}/charts/{chart_key}/version/draft/actions/add-seat",
        json=data,
        auth=(SEATSIO_API_KEY, "")
    )
    if resp.status_code != 200:
        print("❌ seat error:", resp.text)

# 4) Publish
requests.post(f"{BASE}/charts/{chart_key}/version/draft/publish", auth=(SEATSIO_API_KEY, ""))

print("🎉 Chart created and published! Key:", chart_key)
