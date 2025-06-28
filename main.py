import os
import json
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========================
# 🔧 CONFIG
# ========================
chart_key = "e38f6670-8b39-46b7-b22d-7de6187d0cde"
seatsio_api_key = os.environ.get("SEATSIO_API_KEY")
google_creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

domain = "api.us.seats.io"
base_url = f"https://{domain}"
headers = {
    "Authorization": f"{seatsio_api_key}",
    "Content-Type": "application/json"
}

# ========================
# 📄 Authorize Google Sheets
# ========================
creds_dict = json.loads(google_creds_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").sheet1
rows = sheet.get_all_records()

# ========================
# 🧹 Clear chart
# ========================
print("🧹 Clearing chart before adding new seats...")
try:
    r = requests.post(f"{base_url}/charts/{chart_key}/version/draft", headers=headers)
    if r.status_code != 201:
        raise Exception(f"❌ Failed to create draft version: {r.status_code} - {r.text}")
except Exception as e:
    print(f"❌ Error creating draft: {e}")
    exit(1)

# ========================
# 🪚 Upload seats
# ========================
print("🪚 Uploading seats to chart...")
for i, row in enumerate(rows):
    label = row.get("Label") or row.get("Seat") or f"Seat{i+1}"
    x = float(row.get("X", 0))
    y = float(row.get("Y", 0))
    category = row.get("Category", "1")

    seat_data = {
        "label": label,
        "left": x,
        "top": y,
        "category": category
    }

    for attempt in range(3):
        try:
            res = requests.post(
                f"{base_url}/charts/{chart_key}/drawing/seats",
                headers=headers,
                json=seat_data
            )
            res.raise_for_status()
            print(f"✅ Created seat {label}")
            break
        except Exception as e:
            print(f"❌ Failed to create seat {label} (Attempt {attempt+1}/3): {e}")
            time.sleep(5)
    else:
        print(f"⛔ Skipped seat {label} after 3 retries.")

print("🎉 All done.")
