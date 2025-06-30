import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from seatsio import SeatsioClient, Region

SEATSIO_SECRET_KEY = os.environ["SEATSIO_SECRET_KEY"]
CHART_KEY = os.environ["SEATSIO_CHART_KEY"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

client = SeatsioClient(Region.IN, SEATSIO_SECRET_KEY)

client.charts.update(CHART_KEY, name="Grand Theatre - Auto Updated")

for row in rows:
    seat_id = row["Seat"]
    label = row["Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = int(row["Category"])

    client.charts.create_object(
        chart_key=CHART_KEY,
        object_type="seat",
        label=label,
        category_key=str(category),
        left=x,
        top=y
    )

print("✅ All seats added successfully.")
