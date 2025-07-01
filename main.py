import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import Client, Region

# Read environment variables
SEATSIO_SECRET_KEY = os.environ["SEATSIO_SECRET_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]

# Convert escaped JSON string into dict
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

# Open the correct sheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
data = sheet.get_all_records()

# Create chart in NA region
client = Client(secret_key=SEATSIO_SECRET_KEY, region=Region.NORTH_AMERICA())
chart = client.charts.create("Grand Theatre - Automated Chart")

# Add all seats
for row in data:
    label = row["Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = int(row["Category"])
    client.charts.add_seat(chart.key, label=label, x=x, y=y, category=category)

print("✅ Seats imported successfully to chart:", chart.key)
