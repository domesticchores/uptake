import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import CLIENT_ADDRESS

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def main():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
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


  service = build("gmail", "v1", credentials=creds)
  get_messages(service, CLIENT_ADDRESS)

def get_messages(service, user_id):
  try:
    results = service.users().messages().list(userId='me').execute() 
    for mail in results['messages']:
      print(get_message(service, 'me', mail['id']))
  except Exception as error:
    print('An error occurred: %s' % error)

def get_message(service, user_id, msg_id):
  try:
    data = service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
    return data['snippet']
  except Exception as error:
    print('An error occurred: %s' % error)

if __name__ == "__main__":
  main()