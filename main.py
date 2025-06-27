import gspread
import csv
from oauth2client.service_account import ServiceAccountCredentials

# === Setup your Google Service Account Credentials ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(creds)

# === Open your sheet ===
spreadsheet_id = "1Y0HEFyBeIYTUaJvBwRw3zw-cjjULujnU5EfguohoGvQ"
sheet = client.open_by_key(spreadsheet_id).sheet1
data = sheet.get_all_records()

# === Process data and create CSV ===
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

        # Count seat number in each row
        if row_label not in row_seat_counter:
            row_seat_counter[row_label] = 1
        else:
            row_seat_counter[row_label] += 1
        seat_number = row_seat_counter[row_label]

        writer.writerow([seat_label, row_label, seat_number, x, y, category])

print("✅ seatsio_ready.csv created.")
