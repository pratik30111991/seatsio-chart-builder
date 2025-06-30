import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# Load environment variables
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

if not SEATSIO_API_KEY:
    raise Exception("❌ SEATSIO_API_KEY is not set.")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("❌ GOOGLE_CREDENTIALS_JSON is not set.")

# Setup Google Sheets access
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
sheets_client = gspread.authorize(creds)
sheet = sheets_client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()

# Initialize Seats.io client
client = SeatsioClient(Region.IN, SEATSIO_API_KEY)

# Create new chart
chart = client.charts.create("Grand Theatre Chart (Auto)")
print(f"✅ Created chart: {chart.key}")

# Create draft version
client.charts.create_draft_version(chart.key)
print("🧪 Draft version created.")

# Add seats from Google Sheet
for row in data:
    try:
        label = row["Seat Label"]
        x = float(row["X"])
        y = float(row["Y"])
        category = row["Category"]

        client.charts.add_seat_to_draft_version(chart.key, x, y, label, category)
        print(f"✅ Seat added: {label}")
    except Exception as e:
        print(f"❌ Error adding seat {row.get('Seat Label')}: {e}")

# Publish chart
client.charts.publish_draft_version(chart.key)
print("🎉 Draft published successfully!")
