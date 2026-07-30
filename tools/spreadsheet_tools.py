from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import dotenv

dotenv.load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",]


TOKENS_DIR = os.getenv("TOKEN_DIR")

def get_spreadsheet_service():
    creds = None
    
    # token.json stores the user access and auth
    if os.path.exists(f"{TOKENS_DIR}token_sheets.json"):
        creds = Credentials.from_authorized_user_file(f"{TOKENS_DIR}token_sheets.json", SCOPES)


    # If the creds are not valid, user must log in to get new creds
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f"{TOKENS_DIR}credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(f"{TOKENS_DIR}token_sheets.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        return service
    except HttpError as error:
        print(error)




def get_companies() -> dict[str, int]:
    """This function will be eagerly called at the beginning of each interaction to populate the agents
    awareness of what companies weve seen before and need to compare statuses. It will only return the names 
    of companies inputed from the agent"""
    try:
        service = get_spreadsheet_service()

        results = (
            service
            .spreadsheets()
            .values()
            .get(spreadsheetId=os.getenv("SPREADSHEET_ID"), range="A2:A")
            .execute()
        )


        return {row[0]: i + 2 for i, row in enumerate(results.get("values", [])) if row}
    except HttpError as error:
        print(f"Error getting companies: {error}")






def check_if_company_seen(companies: dict[str, int], company_to_check: str) -> bool:
    """Returns whether a company is already in the spreadsheet"""
    return company_to_check in companies




def add_application(company: str, status: str, recruiter=None) -> bool:
    """Given the name of company, the status of the application, and the optionally the recruiters name, it
    will add it to the spreadsheet and return whether it successfully added it or not."""
    service = get_spreadsheet_service()

    values = [company, status, "" if recruiter == None else recruiter]
    body = {"values": [values]}

    try:
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=os.getenv("SPREADSHEET_ID"),
                range="A:C",
                valueInputOption='USER_ENTERED',
                body=body,
            )
            .execute()
        )

        return True

    except HttpError as error:
        print(f"Error adding company to spreadsheet: {error}")
        return False





def update_application(row: int, status: str):

    """This will update the corresponding application status to the given status in the input."""
    service = get_spreadsheet_service()

    try:

        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=os.getenv("SPREADSHEET_ID"),
                range=f"B{row}:B{row}",
                valueInputOption="USER_ENTERED",
                body={"values": [[status]]},
            )
            .execute()
        )

    except HttpError as error:
        print(error)





def _get_schema_spreadsheet():
    """Returns the list of function schemas for the spreadsheet tools, for the Gemini agent."""
    return [
        {
            "type": "function",
            "name": "add_application",
            "description": (
                "Adds a new company and its application status to the spreadsheet. "
                "Only call this for a company that has NOT been seen before -- check the "
                "list of already-tracked companies you were given before calling this."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company."
                    },
                    "status": {
                        "type": "string",
                        "description": "The current status of the application, e.g. 'Applied', 'Interview', 'Rejected', etc."
                    },
                    "recruiter": {
                        "type": "string",
                        "description": (
                            "The name of the recruiter or contact person, only if the email is "
                            "a personal message from a specific named individual (e.g. scheduling "
                            "an interview) -- not from an automated/no-reply system. Omit if unknown."
                        )
                    }
                },
                "required": ["company", "status"]
            }
        },
        {
            "type": "function",
            "name": "update_application",
            "description": (
                "Updates the status of an application for a company that has ALREADY been "
                "tracked before (e.g. moving from Applied to Interview or Rejected). "
                "Only call this for a company you already know is in the spreadsheet."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the already-tracked company to update."
                    },
                    "status": {
                        "type": "string",
                        "description": "The new status, e.g. 'Interview', 'Rejected', 'Offer'."
                    }
                },
                "required": ["company", "status"]
            }
        }
    ]
    


if __name__ == "__main__":
    # get_companies()
    add_application("Microsoft", "Applied")
    update_application(4, "Interview")