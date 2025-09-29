from twilio.rest import Client
import phonenumbers

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
MESSAGING_SERVICE_SID = os.getenv("MESSAGING_SERVICE_SID")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def format_phone(raw_number, region="CA"):
    try:
        parsed = phonenumbers.parse(raw_number, region)  # e.g. "4155551234" with region US
        if phonenumbers.is_valid_number(parsed):
            # Return in international format (+14155551234)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None
    return None

def send_message(number, message):
    client.messages.create(
            messaging_service_sid=MESSAGING_SERVICE_SID,
            body=message,
            to=number
        )