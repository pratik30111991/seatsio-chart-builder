import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import Client, Region

# ✅ Load credentials from environment
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

# ✅ Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# ✅ Open Google Sheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# ✅ Seats.io client with correct region
client = Client(secret_key=os.environ["SEATSIO_SECRET_KEY"], region=Region.NORTH_AMERICA())

# ✅ Create chart
chart = client.charts.create(name="Grand Theatre Chart")

# ✅ Add seats
for row in rows:
    label = row["Seat Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = row["Category"]
    client.charts.add_seat(chart.key, label=label, x=x, y=y, category=category)

print("✅ Chart created successfully:", chart.key)
