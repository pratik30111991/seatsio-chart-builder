import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from seatsio import SeatsioClient, Region

# Google Sheet setup
SHEET_ID = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
SHEET_NAME = "Grand Theatre Seating Plan"

# Seats.io credentials from GitHub Secrets
SEATSIO_SECRET_KEY = os.environ["SEATSIO_SECRET_KEY"]
SEATSIO_WORKSPACE_KEY = os.environ["SEATSIO_WORKSPACE_KEY"]
SEATSIO_CHART_KEY = os.environ["SEATSIO_CHART_KEY"]

# Load Google credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
rows = sheet.get_all_records()

client = SeatsioClient(Region.IN, SEATSIO_SECRET_KEY)

# Create new chart
chart = client.charts.update(SEATSIO_CHART_KEY, name="Updated Grand Theatre Chart")

# Clear existing seats
client.charts.remove_custom_objects(SEATSIO_CHART_KEY)

# Add new seats
for row in rows:
    seat_id = row["Seat"]
    label = row["Label"]
    x = float(row["X"])
    y = float(row["Y"])
    category = int(row["Category"])

    client.charts.create_object(
        chart_key=SEATSIO_CHART_KEY,
        object_type="seat",
        label=label,
        category_key=str(category),
        left=x,
        top=y
    )

print("✅ Seats chart updated successfully.")
