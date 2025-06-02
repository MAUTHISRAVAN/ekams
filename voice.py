pip install flask
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# ----------------- Google Sheets Setup -------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
leads_sheet = client.open("InteriorLeads").worksheet("Leads")
calls_sheet = client.open("InteriorLeads").worksheet("CallRecords")

# ----------------- Helpers -------------------
def update_lead_status(mobile, status, summary):
    leads = leads_sheet.get_all_records()
    for i, lead in enumerate(leads):
        if str(lead["Mobile"]) == str(mobile):
            row = i + 2
            leads_sheet.update_cell(row, 6, status)      # Status
            leads_sheet.update_cell(row, 9, summary)     # Summary
            return True
    return False

def add_call_record(data):
    calls_sheet.append_row([
        data.get("id"),
        data.get("callproviderID", ""),
        data.get("phonenumberID", ""),
        data.get("customernumber", ""),
        data.get("type", ""),
        data.get("started"),
        data.get("ended"),
        data.get("milliseconds", ""),
        data.get("cost", ""),
        data.get("ended_reason", ""),
        data.get("transcript", "")
    ])

# ----------------- Webhook Endpoint -------------------
@app.route('/vapi-callback', methods=['POST'])
def receive_vapi_result():
    data = request.get_json()
    print("Received data:", data)

    mobile = data.get("customernumber")
    outcome = data.get("ended_reason", "Unknown")
    transcript = data.get("transcript", "")
    call_status = "Called" if outcome == "completed" else "Failed"

    # Update Leads
    updated = update_lead_status(mobile, call_status, outcome)

    # Add to CallRecords
    add_call_record(data)

    return jsonify({"success": True, "updated": updated}), 200

if __name__ == '__main__':
    app.run(port=5000)
