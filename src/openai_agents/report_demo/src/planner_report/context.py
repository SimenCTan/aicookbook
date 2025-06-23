from pydantic import BaseModel


class UserContext(BaseModel):
    user_name: str = "DemoUser"
