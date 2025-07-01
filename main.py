import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import Client, Region

# Load credentials from secret
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

# Setup Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# Open sheet and worksheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# Seats.io setup for North America
client = Client(secret_key=os.environ["SEATSIO_SECRET_KEY"], region=Region.NORTH_AMERICA())
chart = client.charts.create(name="Grand Theatre Chart")

# Place each seat
for row in rows:
    label = row["Seat Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]  # use text like "Stalls 1"
    client.charts.add_seat(chart.key, label=label, x=x, y=y, category=category)

print("✅ Chart created:", chart.key)
