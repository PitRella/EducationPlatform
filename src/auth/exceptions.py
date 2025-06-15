from fastapi import HTTPException

class WrongCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail = "User with this "
                                                   "credentials can not be "
                                                   "found")
class AccessTokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail = "Access token expired")