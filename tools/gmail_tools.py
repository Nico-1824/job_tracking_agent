import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import datetime
from bs4 import BeautifulSoup
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():

    """Gets the Gmail service for the authenticated user."""
    creds = None

    # token.json stores the user access and auth
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)


    # If the creds are not valid, user must log in to get new creds
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    





def get_unread_messages():
    """ Gets the unread messages from the users Gmail inbox. """

    service = get_gmail_service()

    try:
        week_ago = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime("%Y/%m/%d")

        query = f'"Thank you" OR "Application" OR "Interview" OR "Position" OR "Offer" OR "Developer" OR "La Salle" OR "LinkedIn" OR "Meeting" -:-unsubscribe after:{week_ago}'

        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], q=query, maxResults=20)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("No new mail.")
            return []
        
        return messages
    except HttpError as error:
        print(f"An error happened getting unread messages: {error}")
        return []


def clean_body(html_or_text):
    soup = BeautifulSoup(html_or_text, "html.parser")
    text = soup.get_text(separator="\n")
    text = re.sub(r'https?://\S+', '', text)  # strip all URLs
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
    

def get_message_body(payload):
    """Recursively extract the text/plain body from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return clean_body(base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace"))

    if "parts" in payload:
        for part in payload["parts"]:
            body = get_message_body(part)
            if body:
                return body

    # Fallback: no text/plain found, try HTML
    if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        return clean_body(base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace"))

    return None
    

def get_message_content():
    """Gets the content of the messages from the users messages and returns an array of the all the content."""
    message_content = []

    service = get_gmail_service()
    messages = get_unread_messages()

    for message in messages:
        message = service.users().messages().get(userId="me", id=message["id"]).execute()
        message_body_content = get_message_body(message["payload"])
        message_content.append({
            "id": message["id"],
            "body": message_body_content,
        })
    
    return message_content



def _get_schema():
    """Returns the schema for the Gmail tool, for gemini agent."""
    return {
        "type": "function",
        "name": "get_messages",
        "description": """Gets users emails, extracts the content of the messages from the users messages, 
        and cleans the message body to remove HTML tags to make as clean to raed as possible.""",
        "parameters": {}
    }