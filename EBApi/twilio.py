# Standard library import
import logging
import os
# Third-party imports
from twilio.rest import Client
#from dotenv import load_dotenv
#load_dotenv()
import boto3
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "EBIKESAPI_DATABASE_SECRET"
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']


client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sending message logic through Twilio Messaging API
def send_message_to_client(to_number, body_text):
    print(f"envs: {os.getenv('TWILIO_ACCOUNT_SID')}, {os.getenv('TWILIO_AUTH_TOKEN')}")
    try:
        message = client.messages.create(
            from_=f"whatsapp:+254794837755",
            body=body_text,
            to=f"{to_number}"
            )
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")


# Sending message logic to riders via Twilio Messaging API
def send_message_to_rider(to_number, body_text):
    print(f"envs: {os.getenv('TWILIO_ACCOUNT_SID')}, {os.getenv('TWILIO_AUTH_TOKEN')}")
    try:
        message = client.messages.create(
            from_=f"whatsapp:+254794837755",
            body=body_text,
            to=f"{to_number}"
        )
        logger.info(f"Message sent to rider: {to_number}")
    except Exception as e:
        logger.error(f"Error sending message to rider {to_number}: {e}")