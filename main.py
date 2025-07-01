import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import Client, Region

# === Step 1: Load Google Credentials from GitHub Secrets ===
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# === Step 2: Open Google Sheet ===
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
data = sheet.get_all_records()

# === Step 3: Connect to Seats.io ===
client = Client(secret_key=os.environ["SEATSIO_SECRET_KEY"], region=Region.NORTH_AMERICA())
chart = client.charts.create(name="Grand Theatre Chart")

# === Step 4: Map category names to category keys ===
category_map = {}
categories = set(row["Category"] for row in data)
for idx, name in enumerate(categories, start=1):
    category_map[name] = client.charts.create_category(chart.key, key=idx, label=name)

# === Step 5: Place each seat ===
for row in data:
    label = str(row["Seat Label"])
    x = float(row["X"])
    y = float(row["Y"])
    category = category_map[row["Category"]].key

    client.charts.add_seat(chart.key, label=label, x=x, y=y, category=category)

print(f"✅ Chart '{chart.key}' created successfully with {len(data)} seats.")
