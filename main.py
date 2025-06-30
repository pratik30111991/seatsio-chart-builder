import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# Env vars
SEATSIO_API_KEY = os.environ["SEATSIO_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

# Google Sheets access
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
sheets = gspread.authorize(creds)
rows = sheets.open_by_key(SHEET_ID).worksheet(SHEET_NAME).get_all_records()

# API base
BASE = "https://api-seatsio.seats.io"

# 1. Create chart
res_chart = requests.post(f"{BASE}/charts", auth=(SEATSIO_API_KEY, ""))
res_chart.raise_for_status()
chart_key = res_chart.json()["key"]
print("✅ Chart created:", chart_key)

# 2. Create draft
res_draft = requests.post(f"{BASE}/charts/{chart_key}/version/draft", auth=(SEATSIO_API_KEY, ""))
res_draft.raise_for_status()
print("🧪 Draft created")

# 3. Upload seats
for row in rows:
    payload = {
        "label": row["Seat Label"],
        "x": float(row["X"]),
        "y": float(row["Y"]),
        "category": row["Category"]
    }
    r = requests.post(
        f"{BASE}/charts/{chart_key}/version/draft/actions/add-seat",
        json=payload,
        auth=(SEATSIO_API_KEY, "")
    )
    if r.status_code != 200:
        print("❌ Seat add failed:", r.text)

print("🪚 Seats uploaded")

# 4. Publish draft
rp = requests.post(f"{BASE}/charts/{chart_key}/version/draft/publish", auth=(SEATSIO_API_KEY, ""))
rp.raise_for_status()
print("🎉 Draft published — chart ready!")
