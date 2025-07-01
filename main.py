import os, json, gspread
from oauth2client.service_account import ServiceAccountCredentials
from seatsio import SeatsioClient, Region

creds = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

rows = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ") \
         .worksheet("Grand Theatre Seating Plan").get_all_records()

client = SeatsioClient(Region.NORTH_AMERICA(), secret_key=os.environ["SEATSIO_SECRET_KEY"])
chart = client.charts.create(name="Grand Theatre Chart")
print("✅ Chart created:", chart.key)

cats = {r["Category"] for r in rows}
cat_keys = {c: client.charts.create_category(chart.key, label=c, color="#009688").key for c in cats}

for r in rows:
    client.charts.add_seat(chart.key, label=r["Seat Label"], x=float(r["X"]), y=float(r["Y"]),
                           category_key=cat_keys[r["Category"]])

print("🎉 Seats added—check your Seats.io dashboard.")
