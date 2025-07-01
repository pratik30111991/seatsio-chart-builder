import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# Read Google credentials from secret
json_str = os.environ["GOOGLE_CREDENTIALS_JSON"]
google_creds = json.loads(json_str)

# Google Sheets auth
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
gc = gspread.authorize(creds)

# Open the spreadsheet and worksheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")

# Read seat data
data = sheet.get_all_records()

# Setup Seats.io client
client = SeatsioClient(secret_key=os.environ["SEATSIO_SECRET_KEY"], region=Region.IN)
chart_key = os.environ["SEATSIO_CHART_KEY"]

# Add seats to chart (example logic)
for row in data:
    label = row["Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]

    client.charts.create_seat(chart_key, label=label, x=x, y=y, category_key=category)
