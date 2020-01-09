import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


class emailSender(object):
    """This class interfaces with the necessary modules in order to facilitate the sending of an email to any other
    part of my code. It is written to send from a GMail address"""
    def __init__(self):
        # This constructor is used to set the details for the account used to send all emails from the software
        self.__username = "matthew.w.giles@gmail.com"
        self.__password = "XXXX"

    def sendEmail(self, subject, message, attachmentName, emails):
        """This function takes a subject string and message string along with the filename of an attachment and a list of
        email addresses that the email should be sent to"""
        # Create an instance of an email object
        msg = MIMEMultipart()
        msg['From'] = self.__username
        msg['Subject'] = subject
        msg['To'] = self.__username
        # Set the email's message to the plain text value of the message variable
        msg.attach(MIMEText(message, 'plain'))
        # If there is an attachment proceed to include it
        if attachmentName is not None:
            # Open the attachment and read append it to the email object
            attachment = open(attachmentName, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= " + attachmentName)
            msg.attach(part)
            # Delete the attachment from the local storage
            os.remove(attachmentName)
        # Making a connection with the gmail server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Signing into the gmail server using the details of the class private variables
        server.login(self.__username, self.__password)
        # Add the message (actual email)
        content = msg.as_string()
        # Add the address of the email is being sent from to the list of emails
        emails.append(self.__username)
        # Send the email back to the email it is sent from and then BCC all the other addresses
        server.sendmail(self.__username, emails, content)
        server.quit()
