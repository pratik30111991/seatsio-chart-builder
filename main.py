import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# ========== ENV VARS ==========
SEATSIO_API_KEY = os.environ.get("SEATSIO_API_KEY")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
CHART_KEY = "49e1934d-4a13-e089-8344-8d01ace4e8db"
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

# ========== CHECK ==========
if not SEATSIO_API_KEY:
    raise Exception("SEATSIO_API_KEY not set")
if not GOOGLE_CREDENTIALS_JSON:
    raise Exception("GOOGLE_CREDENTIALS_JSON not set")

# ========== GOOGLE SHEET ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()

# ========== SEATS.IO ==========
client = SeatsioClient(Region.IN(), SEATSIO_API_KEY)

# ✅ Create draft version
print("🧪 Creating draft version...")
res = client.httpClient.post(f"/charts/{CHART_KEY}/version/draft", None)
if res.status_code != 200:
    raise Exception(f"❌ Error creating draft: {res.text}")
print("✅ Draft version created")

# ✅ Upload all seats
for row in data:
    try:
        label = row["Seat Label"]
        x = float(row["X"])
        y = float(row["Y"])
        category = row["Category"]

        payload = {
            "label": label,
            "x": x,
            "y": y,
            "category": category
        }

        response = client.httpClient.post(
            f"/charts/{CHART_KEY}/version/draft/actions/add-seat",
            payload
        )

        if response.status_code == 200:
            print(f"✅ Seat {label} added")
        else:
            print(f"❌ Failed to add seat {label}: {response.text}")
    except Exception as e:
        print(f"❌ Exception for seat {row.get('Seat Label')}: {e}")

# ✅ Publish
client.charts.publish_draft_version(CHART_KEY)
print("✅ Chart published successfully.")
