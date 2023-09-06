import os
import json
from middlewares import DatetimeMiddleware
from services import CreateFolder, GetFile

def SetupAppConfig(middlewares=[]):
    config_contens = {}
    isCreated = False
    
    if not os.path.exists("./db/config.json"):
        with open("./db/config.json", "w") as f:
            isCreated = True
            f.write("{}")
    else:
        with open("./db/config.json", "r") as f:
            config_contens = json.loads(f.read())
    
    def set_config(key, val):
        namespace = config_contens
        key = key.split(".")
        if len(key) > 1:
            for name in key.split(".")[:-1]:
                if namespace.get(name, None) is None:
                    namespace[name] = {}
                namespace = namespace[name]
        
        use_middleware = None
        if not isinstance(val, (str, dict, tuple, list, int, float)) and val is not None:
            for middleware in middlewares:
                if middleware.accepts(val):
                    use_middleware = middleware
                    break
            if use_middleware is None:
                raise Exception("No middleware is been assigned to type of "+str(type(val)))
        namespace[key[-1]] = val if not use_middleware else use_middleware.set(key[-1], val)

        with open("./db/config.json", "w") as f:
            f.write(json.dumps(config_contens))
    
    def get_config(key=None):
        if key is None: return config_contens

        key = key.split(".")
        namespace = config_contens
        
        if len(key) > 1:
            for name in key[:-1]:
                if namespace.get(name, None) is None:
                    namespace[name] = {}
                namespace = namespace[name]
        
        raw_val = namespace.get(key[-1], None)
        if raw_val is None: return None
        
        use_middleware = None
        for middleware in middlewares:
            if middleware.isinform(raw_val):
                use_middleware = middleware
                break
        return raw_val if not use_middleware else use_middleware.get(key[-1], raw_val)

    return (set_config, get_config, isCreated)

def SetupConfig():
    setcfg, getcfg, isCreated = SetupAppConfig([DatetimeMiddleware()])

    if isCreated:
        setcfg("VaultName", os.path.dirname(__file__).split("\\")[-1]+"-Tests")
        setcfg("DriveFolderId", CreateFolder(getcfg("VaultName"))["id"])
    else:
        folder = GetFile(getcfg("DriveFolderId"))
        if folder is None or folder.get("trashed"):
            setcfg("DriveFolderId", CreateFolder(getcfg("VaultName"))["id"])
            setcfg("LastUpdate", None)

    
    return (setcfg, getcfg)