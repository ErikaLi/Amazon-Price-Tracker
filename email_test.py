# http://www.pythonforbeginners.com/code-snippets-source-code/using-python-to-send-email
# https://motherboard.vice.com/en_us/article/pgkbn9/how-to-send-an-email-from-a-python-script/
# import smtplib

# smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.

# Create a text/plain message
msg = MIMEText("Hi, I am a test message.")


# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'Test'
msg['From'] = "pricetrackerofficial@gmail.com"
msg['To'] = "yingyingli919@gmail.com"

# Send the message via our own SMTP server, but don't include the
# envelope header.
# https://stackoverflow.com/questions/20349170/socket-error-errno-111-connection-refused
s = smtplib.SMTP(host='smtp.gmail.com', port=587)
s.sendmail("pricetrackerofficial@gmail.com", ["yingyingli919@gmail.com"], msg.as_string())
s.quit()