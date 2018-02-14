from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = ""
# Your Auth Token from twilio.com/console
auth_token  = ""

client = Client(account_sid, auth_token)

def send_text(phone, msg): 
    message = client.messages.create(
        to="+1" + phone, 
        from_="+14155238852",
        body=msg)

