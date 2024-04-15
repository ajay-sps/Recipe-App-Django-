import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='You have successfully signed in!!!',
         from_='',
         to='+9815430168'
     )
print(message.sid)