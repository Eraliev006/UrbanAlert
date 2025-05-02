from pydantic import BaseModel

class EmailNotification(BaseModel):
    to_user: str
    otp_code: str

