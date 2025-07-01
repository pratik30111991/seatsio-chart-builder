import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

# Load Google credentials from GitHub Secret
creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

client = SeatsioClient(Region.NORTH_AMERICA(), secret_key=os.environ["SEATSIO_SECRET_KEY"])
chart = client.charts.create(name="Grand Theatre Auto Chart")
print("✅ Created chart:", chart.key)

categories = list({r["Category"] for r in rows})
category_map = {}
for cat in categories:
    cat_obj = client.charts.create_category(chart.key, label=cat, color="#8860D0")
    category_map[cat] = cat_obj.key

for r in rows:
    client.charts.add_seat(chart.key,
                           label=r["Seat Label"],
                           x=float(r["X"]),
                           y=float(r["Y"]),
                           category_key=category_map[r["Category"]])

print("🎉 All seats added — check your chart in Seats.io!")
