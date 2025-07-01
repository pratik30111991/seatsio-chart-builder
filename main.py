import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import Client

# Load Google credentials from environment
json_str = os.environ["GOOGLE_CREDENTIALS_JSON"]
json_data = json.loads(json_str)

# Authenticate Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)
gc = gspread.authorize(creds)

# Access Google Sheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# Authenticate Seats.io
client = Client(secret_key=os.environ["SEATSIO_SECRET_KEY"], region="eu")

# Create chart
chart = client.charts.create("Grand Theatre - Automated Chart")

# Create seats
for row in rows:
    label = str(row["Label"])
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]
    client.charts.add_seat_to_chart(chart.key, label=label, x=x, y=y, category=category)

print(f"✅ Chart created: {chart.key}")
