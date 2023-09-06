import datetime
from abc import ABC


class Middleware(ABC):
    def accepts(self, val) -> bool:
        pass
    
    def isinform(self, val) -> bool:
        pass

    def get(self, key, val) -> object:
        pass

    def set(self, key, val) -> str:
        pass


class DatetimeMiddleware(Middleware):
    def accepts(self, val):
        return isinstance(val, datetime.datetime)
    
    def isinform(self, val):
        try:
            datetime.datetime.strptime(val, "%d/%m/%Y %H:%M:%S")
            return True
        except ValueError:
            return False

    def set(self, key, val):
        return datetime.datetime.strftime(val, "%d/%m/%Y %H:%M:%S")
    
    def get(self, key, val):
        return datetime.datetime.strptime(val, "%d/%m/%Y %H:%M:%S")