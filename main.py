import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from seatsio import Client
from seatsio.region import Region

SEATSIO_SECRET_KEY = os.environ["SEATSIO_SECRET_KEY"]
CHART_KEY = os.environ["SEATSIO_CHART_KEY"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
gc = gspread.authorize(creds)

sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

client = Client(secret_key=SEATSIO_SECRET_KEY, region=Region.NA())

# ✅ REMOVE .update() — not available in old SDK

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
