import datetime
from conf import SetupConfig, SetupAppConfig
from middlewares import DatetimeMiddleware
from services import CreateGoogleDriveService, CreateFolder, UploadFile, GetFileFromName, ReplaceFile, GetFiles, DeleteFile
import os


service = CreateGoogleDriveService()
setcfg, getcfg = SetupConfig()


def AddFilesOnce(path, parent=None):
    for name in os.listdir(path):
        if os.path.isdir(path+"\\"+name):
            folder = CreateFolder(folderName=name, parents=([parent] if parent is not None else []))
            AddFilesOnce(path + "\\" + name, folder["id"])
        else:
            UploadFile(path+"\\"+name, parent)

def ReplaceFiles(path, last_update_date, parent=None):
    for name in os.listdir(path):
        fileFromGdrive = GetFileFromName(name, parent)
        if os.path.isdir(path+"\\"+name) and fileFromGdrive is None:
            folder = CreateFolder(folderName=name, parents=[parent] if parent is not None else [])
            AddFilesOnce(path + "\\" + name, folder["id"])
        elif os.path.isdir(path+"\\"+name):
            ReplaceFiles(path+"\\"+name, last_update_date, fileFromGdrive["id"])
        else:
            if fileFromGdrive is None:
                UploadFile(path+"\\"+name, parent)
            else:
                last_change_time = datetime.datetime.fromtimestamp(os.path.getmtime(path + "\\" + name))
                if last_change_time > last_update_date:
                    ReplaceFile(path + "\\" + name, fileFromGdrive["id"])

def UpdateDeletedFiles(path, parent):
    for file in GetFiles(parent):
        if not os.path.exists(path+"\\"+file["name"]):
            DeleteFile(file["id"])
        elif os.path.isdir(path+"\\"+file["name"]):
            UpdateDeletedFiles(path+"\\"+file["name"], file["id"])


def UploadFiles():
    if getcfg("LastUpdate") is None:
        AddFilesOnce(".\\assets", getcfg("DriveFolderId"))
        setcfg("LastUpdate", datetime.datetime.now())
        return
    
    lastUpdateTime = getcfg("LastUpdate")
    ReplaceFiles(".\\assets", lastUpdateTime, getcfg("DriveFolderId"))
    print("Stopped Updating, Checking Deletions")
    UpdateDeletedFiles(".\\assets", getcfg("DriveFolderId"))
    setcfg("LastUpdate", datetime.datetime.now())

UploadFiles()