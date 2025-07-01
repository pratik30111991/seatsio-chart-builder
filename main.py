import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import Client

# Load Google Service Account credentials from GitHub Secrets
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# Open the sheet and read data
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# Seats.io setup
client = Client(secret_key=os.environ["SEATSIO_SECRET_KEY"])
chart = client.charts.create(name="Grand Theatre Chart")

# Add seats from Google Sheet
for row in rows:
    label = str(row["Seat"])
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]
    
    client.charts.create_seat(chart.key, label=label, x=x, y=y, category=category)

print("✅ Chart created successfully:", chart.key)
