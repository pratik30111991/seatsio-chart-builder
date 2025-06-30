import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import seatsio  # use seatsio.Client per SDK docs
from seatsio import Region

# Load secrets
SEATSIO_SECRET_KEY = os.environ["SEATSIO_SECRET_KEY"]
CHART_KEY = os.environ["SEATSIO_CHART_KEY"]

# Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
gc = gspread.authorize(creds)

sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# Seats.io client
client = seatsio.Client(Region.IN(), secret_key=SEATSIO_SECRET_KEY)

# Update chart name
client.charts.update(CHART_KEY, name="Grand Theatre - Auto Updated")

# Add seats
for row in rows:
    client.charts.create_object(
        chart_key=CHART_KEY,
        object_type="seat",
        label=row["Label"],
        category_key=str(int(row["Category"])),
        left=float(row["X"]),
        top=float(row["Y"])
    )

print("✅ All seats added successfully.")
