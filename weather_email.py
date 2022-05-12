import os, os.path, requests
from base64 import urlsafe_b64encode
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from typing import Any, TypedDict


load_dotenv()


class Forecast(TypedDict):
    """Represents the minimum weather info to be displayed in email"""
    min_temp: float
    max_temp: float
    total_precip: float
    condition: str  # Such as Partly Cloudy or Sunny
    icon_filename: str


def get_forecast_json(zip_code: str) -> dict[str, Any]:
    """Returns the forecast data for the specified zip code
    
    Currently, there are no checks to determine whether the zip code
    is valid or if the API can be accessed"""
    api_key = os.getenv('WEATHER_API_KEY')
    params = {'key': api_key, 'q': zip_code, 'days': 1,
          'aqi': 'no', 'alerts': 'no'}
    link = 'http://api.weatherapi.com/v1/forecast.json'
    response = requests.get(link, params=params)
    return response.json()


def extract_relevant_forecast_data(forecast_json: dict[str, Any]) -> Forecast:
    """Extracts only the information that will be used in email"""
    day = forecast_json['forecast']['forecastday'][0]['day']
    forecast = {'min_temp': day['mintemp_f'], 'max_temp': day['maxtemp_f'],
                'total_precip': day['totalprecip_in']}
    forecast['condition'] = day['condition']['text']
    forecast['icon_filename'] = day['condition']['icon'].split('/')[-1]
    return forecast


def construct_email(forecast: Forecast) -> MIMEBase:
    """Constructs the email using a Forecast and pre-formatted HTML"""
    message = MIMEMultipart('related')
    message['to'] = os.getenv('EMAIL_RECEIVER')
    message['from'] = os.getenv('EMAIL_SENDER')
    message['subject'] = "Today's Forecast"
    
    with open('email_format.html') as f:
        email_format = f.read().format(
            high = forecast['max_temp'],
            low = forecast['min_temp'],
            total_precip = forecast['total_precip'],
            condition = forecast['condition']
        )
    message.attach(MIMEText(email_format, 'html'))

    icon_filepath = os.path.join('weather_icons', '64x64',
                                 'day', forecast['icon_filename'])
    with open(icon_filepath, 'rb') as f:
        img_data = f.read()
    img = MIMEImage(img_data, 'png')
    img.add_header('Content-Id', '<cond_icon>')
    img.add_header('Content-Disposition', 'inline', filename=forecast['icon_filename'].split('.')[0])
    message.attach(img)
    return message

def get_credentials() -> Credentials | None:
    scopes = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def send_email(message: MIMEBase, creds: Credentials) -> bool:
    body = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        service = build('gmail', 'v1', credentials=creds)
        service.users().messages().send(userId='me', body=body).execute()
    except HttpError:
        return False
    else:
        return True
    finally:
        service.close()


def main() -> None:
    creds = get_credentials()
    forecast_json = get_forecast_json(os.getenv('ZIP_CODE'))
    forecast = extract_relevant_forecast_data(forecast_json)
    message = construct_email(forecast)
    has_sent_email = send_email(message, creds)
    if has_sent_email:
        print('Email successfully sent!')
    else:
        print('Email failed to send')


if __name__ == '__main__':
    main()
