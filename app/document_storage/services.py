from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from fastapi import HTTPException
from pathlib import Path
import logging
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
from app.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_FILE = Path(__file__).parent.parent.parent / 'token.json'
CREDENTIALS_FILE = Path(__file__).parent.parent.parent / 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
DOMAIN = Config.DOMAIN_NAME

class GoogleDriveService:
    def get_drive_service(self, credentials: Credentials):
        """Create a Google Drive service from credentials."""
        try:
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Error initializing Drive service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error initializing Drive service: {str(e)}")

    def load_credentials(self):
        """Load credentials from token.json and refresh if needed."""
        if TOKEN_FILE.exists():
            try:
                credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                # Refresh token if expired and refresh_token is available
                if credentials.expired and credentials.refresh_token:
                    logger.info("Access token expired, refreshing...")
                    credentials.refresh(Request())
                    self.save_credentials(credentials)
                return credentials
            except Exception as e:
                logger.error(f"Invalid credentials file: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid credentials file: {str(e)}")
        logger.warning("token.json not found, re-authentication required")
        return None

    def save_credentials(self, credentials: Credentials):
        """Save credentials to token.json."""
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(credentials.to_json())
            logger.info("Credentials saved to token.json")
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error saving credentials: {str(e)}")

    def authenticate(self):
        """Initialize OAuth flow and return authorization URL."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
                redirect_uri=f'{DOMAIN}/drive/auth/callback'
            )
            auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
            logger.info(f"Generated auth URL: {auth_url}")
            return auth_url, state
        except Exception as e:
            logger.error(f"Error initializing OAuth flow: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error initializing OAuth flow: {str(e)}")

    def handle_auth_callback(self, code: str):
        """Handle OAuth callback and save credentials."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
                redirect_uri=f'{DOMAIN}:8000/drive/auth/callback'
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials
            self.save_credentials(credentials)
            logger.info("OAuth authentication successful")
            return credentials
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

    def download_and_save(self, file_id: str, output_dir: str = "temp_files"):
        """Download a PDF from Google Drive by file_id and save file in local"""
        try:
            credentials = self.load_credentials()
            if not credentials or not credentials.valid:
                logger.warning("Invalid credentials, re-authentication required")
                raise HTTPException(
                    status_code=401,
                    detail="Could not validate credentials. Please authenticate via /drive/auth",
                )
            drive_service = self.get_drive_service(credentials)

            # Get file metadata
            file_metadata = (
                drive_service.files()
                .get(fileId=file_id, fields="name, mimeType")
                .execute()
            )
            file_name = file_metadata.get("name", "downloaded_file")
            mime_type = file_metadata.get("mimeType", "")

            # Verify file is a PDF
            if mime_type != "application/pdf":
                raise HTTPException(
                    status_code=400, detail=f"File is not a PDF: {mime_type}"
                )

            # Download file
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Save PDF to disk
            Path(output_dir).mkdir(exist_ok=True)
            temp_file_path = Path(output_dir) / file_name

            with open(temp_file_path, "wb") as f:
                f.write(fh.getvalue())

            if not temp_file_path.exists():
                raise HTTPException(
                    status_code=404, detail="File not found after download"
                )

            return {
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": mime_type,
                "path_file": temp_file_path,
            }

        except HttpError as e:
            status_code = e.resp.status
            if status_code == 404:
                logger.error(f"File not found: {file_id}")
                return {"error": f"File not found: {file_id}"}
            elif status_code == 403:
                logger.error(f"Access denied: {str(e)}")
                return {"error": f"Access denied: {str(e)}"}
            logger.error(f"Google API error: {str(e)}")
            return {"error": f"Google API error: {str(e)}"}
        except HTTPException as e:
            logger.error(f"HTTP error: {e.status_code} - {e.detail}")
            return {"error": f"HTTP error: {e.status_code} - {e.detail}"}
        except Exception as e:
            logger.error(f"Error: {str(e)}")