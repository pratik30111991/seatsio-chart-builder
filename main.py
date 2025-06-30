import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# === Config ===
SEATSIO_API_KEY = os.environ["SEATSIO_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"

# === Google Sheets ===
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
sheet_client = gspread.authorize(creds)
sheet = sheet_client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
rows = sheet.get_all_records()

# === Seats.io Client ===
client = SeatsioClient(Region.IN, SEATSIO_API_KEY)

# === Create draft version
print("🧪 Creating draft version...")
client.charts.create_draft_version(CHART_KEY)
print("✅ Draft version created")

# === Add seats
print("🎯 Adding seats...")
for row in rows:
    label = row["Seat Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]

    try:
        client.charts.add_seat_to_draft_version(
            CHART_KEY,
            x=x,
            y=y,
            label=label,
            category_key=category
        )
        print(f"✅ Added seat {label}")
    except Exception as e:
        print(f"❌ Failed to add seat {label}: {e}")

# === Publish draft
print("🚀 Publishing chart...")
client.charts.publish_draft_version(CHART_KEY)
print("✅ Draft published")
