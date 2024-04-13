import io
import random
import zipfile

from httpx import AsyncClient
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .utils import headers, json_for_t2i

__version__ = "0.0.2"

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-nai3",
    description="通过 NovelAI 生成图片",
    usage="通过 NovelAI 生成图片",
    homepage="https://github.com/zhulinyv/nonebot_plugin_nai3",
    type="library",
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
    },
    extra={
        "author": "zhulinyv",
        "version": __version__,
    },
)


nai3 = on_command("nai3", aliases={"nai"}, priority=30, block=True)


@nai3.handle()
async def _(msg: Message = CommandArg()):
    prompt = msg.extract_plain_text().strip()

    json_for_t2i["input"] = prompt
    json_for_t2i["parameters"]["width"] = 832
    json_for_t2i["parameters"]["height"] = 1216
    json_for_t2i["parameters"]["scale"] = 5.0
    json_for_t2i["parameters"]["sampler"] = "k_euler"
    json_for_t2i["parameters"]["steps"] = 28
    json_for_t2i["parameters"]["sm"] = False
    json_for_t2i["parameters"]["sm_dyn"] = False
    json_for_t2i["parameters"]["noise_schedule"] = "native"
    json_for_t2i["parameters"]["seed"] = random.randint(1000000000, 9999999999)
    json_for_t2i["parameters"]["negative_prompt"] = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"

    async with AsyncClient() as client:
        response = await client.post("https://image.novelai.net/ai/generate-image", json=json_for_t2i, headers=headers, timeout=300)
        logger.debug(">>>>>")
        logger.debug(response.status_code)
        logger.debug("<<<<<")
        with zipfile.ZipFile(io.BytesIO(response.content), mode="r") as zip:
            with zip.open("image_0.png") as image:
                await nai3.finish(MessageSegment.image(image.read()))
