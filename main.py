import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# Load credentials
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# Open the sheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
data = sheet.get_all_records()

# Seats.io
client = SeatsioClient(Region.NORTH_AMERICA(), secret_key=os.environ["SEATSIO_SECRET_KEY"])

chart = client.charts.create(name="Grand Theatre Auto Chart")
for row in data:
    label = row["Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]
    client.charts.update(chart.key, name="Grand Theatre Auto Chart")
    client.seats.create(chart.key, category_label=category, label=label, x=x, y=y)

print(f"Chart created with key: {chart.key}")
