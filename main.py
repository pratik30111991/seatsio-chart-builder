import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio.seatsio_client import SeatsioClient
from seatsio.region import Region

# Load secrets
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

if not SEATSIO_API_KEY:
    raise Exception("❌ SEATSIO_API_KEY not set.")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("❌ GOOGLE_CREDENTIALS_JSON not set.")

# Authorize Google Sheets
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
sheets_client = gspread.authorize(creds)
worksheet = sheets_client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = worksheet.get_all_records()

# Connect to Seats.io
client = SeatsioClient(Region.IN, SEATSIO_API_KEY)

# Create chart
chart = client.charts.create("Grand Theatre Chart (Auto)")
print(f"✅ Created chart: {chart.key}")

# Create draft
client.charts.create_draft_version(chart.key)
print("🧪 Draft version created...")

# Add seats
for row in data:
    try:
        label = row["Seat Label"]
        x = float(row["X"])
        y = float(row["Y"])
        category = row["Category"]
        client.charts.add_seat_to_draft_version(chart.key, x, y, label, category)
        print(f"✅ Seat added: {label}")
    except Exception as e:
        print(f"❌ Failed to add seat {row.get('Seat Label')}: {e}")

# Publish chart
client.charts.publish_draft_version(chart.key)
print("🎉 Chart published!")
