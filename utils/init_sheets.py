from services.google_sheets import GoogleSheetsManager

def initialize_google_sheets():
    sheets_manager = GoogleSheetsManager()

    sheets_manager.get_worksheet("Users")
    sheets_manager.get_worksheet("Groups")
    sheets_manager.get_worksheet("Assignments")
    sheets_manager.get_worksheet("Attendance")

    print("Google Sheets initialized")

if __name__ == "__main__":
    initialize_google_sheets()