from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from urllib.error import HTTPError
import base64
import mimetypes
import os
from django.conf import settings



def initialise_gmail():
    SCOPES = 'https://www.googleapis.com/auth/gmail.compose'

    store_path = os.path.join(settings.BASE_DIR,'token.json')
    store = file.Storage(store_path)
    creds = store.get()
    if not creds or creds.invalid:
        cred_path = os.path.join(settings.BASE_DIR,'credentials.json')
        flow = client.flow_from_clientsecrets(cred_path, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    return service



def create_message(to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = 'operations@textbook.ventures'
  message['subject'] = subject
  b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
  b64_string = b64_bytes.decode()
  return {'raw': b64_string}


def create_message_with_attachment(
    recipients, subject, message_text, files):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
  # deal with the message body
  message = MIMEMultipart()
  message['to'] = ','.join(recipients)
  message['from'] = 'operations@textbook.ventures'
  message['subject'] = subject

  msg = MIMEText(message_text)
  message.attach(msg)

  # deal with the attachment/files
  for file in files:
    filename = file.name
    content_type = file.content_type
    encoding = file.charset
    if content_type is None or encoding is not None:
      content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    msg = MIMEBase(main_type, sub_type)
    msg.set_payload(file.read())

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

  b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
  b64_string = b64_bytes.decode()
  return {'raw': b64_string}




def send_message(message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  service = initialise_gmail()
  try:
    message = (service.users().messages().send(userId='me', body=message)
               .execute())
    print( 'Message Id: %s' % message['id'])
    return message
  except HTTPError as e:
    print( 'An error occurred: %s' % e)
    print( e.read() )
  return

def send_confirmation_email(recipient):
  service = initialise_gmail() 


  confirmation_message_path = os.path.join(settings.BASE_DIR,'templates/confirmation_email.html')
  try: 
    fp = open (confirmation_message_path, 'rb')
    message = MIMEText(fp.read(),'html')
    fp.close()
  except:
    message = MIMEText('Thank you for your submission')

  message['to'] = recipient
  message['from'] = 'operations@textbook.ventures'
  message['subject'] = 'SSF Cup Submission Confirmation'

  b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
  b64_string = b64_bytes.decode()
  send_message ({'raw':b64_string})

  return 







