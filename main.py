import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# Load credentials from GitHub secret
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

# Google Sheets authorization
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# Open sheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# Connect to Seats.io
client = SeatsioClient(region=Region.NORTH_AMERICA(), secret_key=os.environ["SEATSIO_SECRET_KEY"])
chart = client.charts.create(name="Grand Theatre Chart")
print("✅ Chart created:", chart.key)

# Collect unique categories
categories = list(set(row["Category"] for row in rows))
category_map = {}
for cat in categories:
    created = client.charts.create_category(chart.key, label=cat, color="#009688")
    category_map[cat] = created.key

# Add seats
for row in rows:
    label = row["Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category_label = row["Category"]
    category_key = category_map[category_label]
    client.charts.add_seat(chart.key, label=label, x=x, y=y, category_key=category_key)

print("🎉 All seats added successfully!")
