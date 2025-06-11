from fastapi import HTTPException, status


class UserNotFoundByIdException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404,
                            detail=f"Active user by this id not "
                                   f"found.")

class ForgottenParametersException(HTTPException):
    def __init__(self):
        super().__init__(status_code=422,
                         detail=f"Not all parameters was filled")