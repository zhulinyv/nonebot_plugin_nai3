from nonebot.plugin import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    nai3_token: str = "xxx"
    nai3_negative: str = (
        "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"  # noqa: E501
    )
    nai3_limit: int = 10
    nai3_cooltime_group: int = 30
    nai3_cooltime_user: int = 300
    nai3_proxy: str = None
    nai3_r18: bool = False
    smms_api_url: str = "https://sm.ms/api/v2"
    smms_token: str = None


nai3_config = get_plugin_config(Config)
