import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio.seatsio_client import SeatsioClient
from seatsio.region import Region

# ====== Setup ======
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"

if not SEATSIO_API_KEY:
    raise Exception("SEATSIO_API_KEY not set")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("GOOGLE_CREDENTIALS_JSON not set")

# ====== Google Sheets ======
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()

# ====== Seats.io Client ======
client = SeatsioClient(Region.IN(), SEATSIO_API_KEY)

# ✅ Create draft version for existing chart
print("🧪 Creating draft version...")
draft = client.charts.create_draft_version(CHART_KEY)

# ✅ Add seats
print("🪚 Uploading seats to chart...")
for row in data:
    try:
        label = row["Seat Label"]
        x = float(row["X"])
        y = float(row["Y"])
        category = row["Category"]

        client.charts.add_seat_to_draft_version(CHART_KEY, x, y, label, category)
        print(f"✅ Added seat {label}")
    except Exception as e:
        print(f"❌ Error adding seat {row.get('Seat Label')}: {e}")

# ✅ Publish draft
client.charts.publish_draft_version(CHART_KEY)
print("✅ Draft published. All seats uploaded.")
