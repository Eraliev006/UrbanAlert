from pydantic import BaseModel

class EmailNotificationSchema(BaseModel):
    to_user: str
    otp_code: str

