from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    nai3_token: str = "xxx"


nai3_config = Config.parse_obj(get_driver().config.dict())
