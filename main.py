import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# ENV
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

if not SEATSIO_API_KEY or not GOOGLE_CREDENTIALS_JSON:
    raise Exception("❌ Missing credentials")

# Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)
worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
rows = worksheet.get_all_records()

# Seats.io client
client = SeatsioClient(Region.IN, SEATSIO_API_KEY)

# Create chart
chart = client.charts.create("🎭 Grand Theatre Chart (Auto)")
client.charts.create_draft_version(chart.key)
print(f"✅ Created chart: {chart.key}")

# Add seats
for row in rows:
    try:
        label = row["Seat"]
        x = float(row["X"])
        y = float(row["Y"])
        category = row["Category"]
        client.charts.add_seat_to_draft_version(chart.key, x, y, label, category)
        print(f"➕ Added: {label} at ({x},{y}) [Category: {category}]")
    except Exception as e:
        print(f"⚠️ Seat error: {e}")

# Publish
client.charts.publish_draft_version(chart.key)
print("🎉 Chart published!")
