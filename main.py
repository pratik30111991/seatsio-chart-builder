import os
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from seatsio import Client

# STEP 1: Decode JSON string from GitHub Secret and save it as a real JSON file
json_str = os.environ["GOOGLE_CREDENTIALS_JSON"]
json_data = json.loads(json_str)

with open("google_credentials.json", "w") as f:
    json.dump(json_data, f)

# STEP 2: Load credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
gc = gspread.authorize(creds)

# Now proceed with accessing your sheet and Seats.io logic...
# Read data from Google Sheet
sheet = gc.open_by_key("1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ").worksheet("Grand Theatre Seating Plan")
rows = sheet.get_all_records()

# Initialize Seats.io client (with working region)
client = Client(secret_key=SEATSIO_SECRET_KEY, region=Region.NA())

# Add seats to the chart
for row in rows:
    client.charts.create_object(
        chart_key=CHART_KEY,
        object_type="seat",
        label=row["Label"],
        category_key=str(int(row["Category"])),
        left=float(row["X"]),
        top=float(row["Y"])
    )

print("✅ All seats placed successfully.")
