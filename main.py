import gspread
import csv
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# === Load JSON from GitHub Secret (in environment variable) ===
google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")

if not google_creds:
    raise Exception("❌ Missing GOOGLE_CREDENTIALS_JSON secret.")

# Authorize with Google Sheets API
creds_dict = json.loads(google_creds)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# === Open the Google Sheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).sheet1
data = sheet.get_all_records()

# === Write to Seats.io-compatible CSV ===
with open("seatsio_ready.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["seatLabel", "row", "column", "x", "y", "category"])

    row_seat_counter = {}

    for row in data:
        seat_label = row["Seat"]
        row_label = row["Label"]
        x = row["X"]
        y = row["Y"]
        category = row["Category"]

        # Auto-generate seat number (column) for each row
        if row_label not in row_seat_counter:
            row_seat_counter[row_label] = 1
        else:
            row_seat_counter[row_label] += 1
        seat_number = row_seat_counter[row_label]

        writer.writerow([seat_label, row_label, seat_number, x, y, category])

print("✅ Done: seatsio_ready.csv generated successfully.")
