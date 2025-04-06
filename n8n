import gspread
import time
import requests
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- Config ----------------
VAPI_API_KEY = "YOUR_VAPI_API_KEY"
SHEET_NAME = "InteriorLeads"
MAX_ATTEMPTS = 2

# ------------- Google Sheets Auth -------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet("Leads")

# ------------- Fetch TBC Leads -----------------
def get_tbc_leads():
    leads = sheet.get_all_records()
    tbc_leads = []
    for i, lead in enumerate(leads):
        if lead["Status"] == "TBC" and lead["Attempt"] < MAX_ATTEMPTS:
            lead["row"] = i + 2  # account for header
            tbc_leads.append(lead)
    return tbc_leads

# ------------- Initiate Vapi Call -----------------
def start_call(lead):
    payload = {
        "phoneNumber": lead["Mobile"],
        "metadata": {
            "first_name": lead["First Name"],
            "last_name": lead["Last Name"],
            "email": lead["Email"]
        }
    }
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post("https://api.vapi.ai/v1/calls", json=payload, headers=headers)
    return response.json()

# ------------- Update Lead Status -----------------
def update_lead_status(row, status, attempt, summary=""):
    sheet.update_cell(row, 6, status)  # Status
    sheet.update_cell(row, 7, attempt)  # Attempt
    if summary:
        sheet.update_cell(row, 9, summary)  # Summary

# ------------- Main Logic -----------------
def run():
    leads = get_tbc_leads()
    for lead in leads:
        print(f"Calling {lead['First Name']} at {lead['Mobile']}")
        response = start_call(lead)

        # Simulate waiting for response or callback
        time.sleep(1)

        if "call_id" in response:
            update_lead_status(lead["row"], "In-Progress", lead["Attempt"] + 1)
        else:
            # Retry logic if failed
            update_lead_status(lead["row"], "Failed", lead["Attempt"] + 1, "API Call Failed")

if __name__ == "__main__":
    run()
