from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    nai3_token: str = "xxx"
    nai3_negative: str = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"
    nai3_limit: int = 10
    nai3_cooltime_group: int = 30
    nai3_cooltime_user: int = 300


nai3_config = Config.parse_obj(get_driver().config.dict())
