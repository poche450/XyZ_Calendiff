from __future__ import print_function
import datetime
import os.path

from requests.models import HTTPError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


now = datetime.datetime.utcnow().isoformat() + 'Z'
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class calendar():
  def __init__(self):
    self.creds = None
    self.authenticated=self.is_authenticated()
  def is_authenticated(self):
    if not os.path.exists('token.json'):
      authenticated=False
    if os.path.exists('token.json'):
      self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
      if self.creds.valid and not self.creds.expired:
        authenticated=True
      if not self.creds.valid or self.creds.expired:
        authenticated=False
    return authenticated

  def authorize(self):
      """Shows basic usage of the Google Calendar API.
      Prints the start and name of the next 10 events on the user's calendar.
      """

      # The file token.json stores the user's access and refresh tokens, and is
      # created automatically when the authorization flow completes for the first
      # time.
      if os.path.exists('token.json'):
          self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
      # If there are no (valid) credentials available, let the user log in.
      if not self.creds or not self.creds.valid:
          if self.creds and self.creds.expired and self.creds.refresh_token:
              self.creds.refresh(Request())
          else:
            try:
              flow = InstalledAppFlow.from_client_secrets_file(
                  'credentials.json', SCOPES)
              self.creds = flow.run_local_server(port=0)
            except:pass
          # Save the credentials for the next run
          with open('token.json', 'w') as token:
              token.write(self.creds.to_json())

