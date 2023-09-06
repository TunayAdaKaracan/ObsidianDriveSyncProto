import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import json

MIME_TYPES = {
    ".md": "text/plain"
}

# If modifying these scopes, delete the file token.json.
SERVICE = None
def CreateGoogleDriveService():
    global SERVICE
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = None
    if os.path.exists('./json/token.json'):
        creds = Credentials.from_authorized_user_file('./json/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './json/client-secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./json/token.json', 'w') as token:
            token.write(creds.to_json())
    SERVICE = build('drive', 'v3', credentials=creds)
    return SERVICE

def CreateFolder(folderName, **kwargs):
    metadata = {
        "name": folderName,
        "mimeType": "application/vnd.google-apps.folder",
        **kwargs
    }
    return SERVICE.files().create(body=metadata).execute()

def UploadFile(filePath, parent=None):
    media = MediaFileUpload(filePath, mimetype=MIME_TYPES.get(filePath.split(".")[-1], "text/plain"))
    SERVICE.files().create(
        body={
            "name": filePath.split("\\")[-1],
            "parents": [parent] if parent is not None else [],
        },
        media_body=media
    ).execute()

def ReplaceFile(filePath, fileId):
    media = MediaFileUpload(filePath, mimetype=MIME_TYPES.get(filePath.split(".")[-1], "text/plain"))
    SERVICE.files().update(
        fileId=fileId,
        body={
            "name": filePath.split("\\")[-1],
        },
        media_body=media
    ).execute()

def GetFile(fileId):
    try:
        file = SERVICE.files().get(fileId=fileId, fields="id, name, trashed").execute()
        return file
    except HttpError as e:
        if e.reason == "notFound":
            return None
        else:
            raise e
        
def GetFileFromName(name, parentId=None):
    query = f"parents='{parentId}'" if parentId else ""
    query += f"and name='{name}'" if parentId else f"name='{name}'"
    files = SERVICE.files().list(
        q=query,
        fields = "nextPageToken, files(id, name, mimeType)"
    ).execute().get("files", [])
    return None if len(files) == 0 else files[0]

def GetFiles(parentId):
    files = SERVICE.files().list(
        q=f"parents='{parentId}'",
        fields = "nextPageToken, files(id, name, mimeType)"
    ).execute().get("files", [])
    return files

def DeleteFile(fileID):
    SERVICE.files().delete(
        fileId=fileID
    ).execute()