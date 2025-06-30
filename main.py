import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio.seatsio_client import SeatsioClient
from seatsio.region import Region

# ========== Setup ==========
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

if not SEATSIO_API_KEY:
    raise Exception("SEATSIO_API_KEY not set")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("GOOGLE_CREDENTIALS_JSON not set")

# ========== Connect Google Sheet ==========
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
rows = sheet.get_all_records()

# ========== Seats.io Client ==========
client = SeatsioClient(Region.IN, SEATSIO_API_KEY)

# Use your existing chart
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"

# Create draft version
client.charts.create_draft_version(CHART_KEY)

# Collect seat objects
seats = []
for row in rows:
    try:
        seat = {
            "label": row["Seat Label"],
            "x": float(row["X"]),
            "y": float(row["Y"]),
            "category": row["Category"]
        }
        seats.append(seat)
    except Exception as e:
        print(f"❌ Invalid row: {row} => {e}")

# Update chart draft with seat drawing objects
drawing_objects = [
    {
        "type": "seat",
        "label": s["label"],
        "x": s["x"],
        "y": s["y"],
        "category": s["category"]
    }
    for s in seats
]

client.charts.update_chart(
    CHART_KEY,
    {"objects": drawing_objects}
)

# Publish the draft
client.charts.publish_draft_version(CHART_KEY)
print("✅ All seats added & draft published successfully.")
