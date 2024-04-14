import asyncio
import io
import os
import random
import time
import zipfile
from argparse import Namespace
from importlib.metadata import version

import ujson as json
from httpx import AsyncClient
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, Bot, GroupMessageEvent, Message, MessageEvent, MessageSegment, PrivateMessageEvent
from nonebot.log import logger
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_command, on_shell_command
from nonebot.rule import ArgumentParser

from .config import Config, nai3_config
from .utils import format_str, get_at, headers, json_for_t2i, list_to_str

ADMIN = SUPERUSER | GROUP_ADMIN | GROUP_OWNER

try:
    __version__ = version("nonebot_plugin_nai3")
except Exception:
    __version__ = "0.0.0"

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-nai3",
    description="通过 NovelAI 生成图片",
    usage="通过 NovelAI 生成图片",
    homepage="https://github.com/zhulinyv/nonebot_plugin_nai3",
    type="application",
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
    },
    config=Config,
    extra={
        "author": "zhulinyv",
        "version": __version__,
    },
)


nai3_parser = ArgumentParser()
nai3_parser.add_argument("prompt", nargs="*", help="提示词(支持你喜欢的画风串)", type=str)
nai3_parser.add_argument("-n", "--negative", nargs="*", help="负面提示词", type=str, dest="negative")
nai3_parser.add_argument("-r", "--resolution", help="画布形状/分辨率", type=str, dest="resolution")
nai3_parser.add_argument("-s", "--scale", help="提示词相关性", type=float, dest="scale")
nai3_parser.add_argument("-sm", help="sm", type=bool, dest="sm")
nai3_parser.add_argument("-smdyn", help="smdyn", type=bool, dest="smdyn")
nai3_parser.add_argument("--sampler", help="采样器", type=str, dest="sampler")
nai3_parser.add_argument("--schedule", help="噪声计划表", type=str, dest="schedule")


nai3 = on_shell_command("nai3", aliases={"nai"}, parser=nai3_parser, priority=30, block=True)
nai3_black = on_command("nai3黑名单", aliases={"nai3 黑名单", "nai黑名单", "nai 黑名单"}, priority=20, permission=ADMIN, block=True)

cd = {}


@nai3.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    if isinstance(event, PrivateMessageEvent):
        gid = uid = str(event.user_id)
    elif isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        uid = str(event.user_id)
    else:
        await nai3.send("不支持该聊天捏~请切换至群聊或私聊重试!", at_sender=True)

    try:
        with open("./data/nai3/black_data.json", "r") as f:
            black_data = json.load(f)
        if event.get_user_id() not in bot.config.superusers:
            if gid in black_data["group"]:
                await nai3.finish("当前群聊在画图黑名单中!", at_sender=True)
            if uid in black_data["user"]:
                await nai3.finish("你在画图黑名单中!", at_sender=True)
    except FileNotFoundError:
        pass

    now_time = time.time()
    try:
        cd[gid]["user"][uid]["limit"]
    except KeyError:
        cd[gid] = {"cool_time": now_time - nai3_config.nai3_cooltime_group, "user": {uid: {"limit": 999 if event.get_user_id() in bot.config.superusers else nai3_config.nai3_limit, "cool_time": now_time - nai3_config.nai3_cooltime_user}}}

    if event.get_user_id() not in bot.config.superusers:
        logger.debug(event.get_user_id())
        logger.debug(bot.config.superusers)
        if now_time - cd[gid]["cool_time"] < nai3_config.nai3_cooltime_group:
            await nai3.finish("群聊绘画冷却中, 剩余时间: {}...".format(round(nai3_config.nai3_cooltime_group - now_time + cd[gid]["cool_time"], 3)), at_sender=True)
        if now_time - cd[gid]["user"][uid]["cool_time"] < nai3_config.nai3_cooltime_user:
            await nai3.finish("个人绘画冷却中, 剩余时间: {}...".format(round(nai3_config.nai3_cooltime_user - now_time + cd[gid]["cool_time"], 3)), at_sender=True)
        if cd[gid]["user"][uid]["limit"] <= 0:
            await nai3.finish("今天已经没次数了哦~", at_send=True)

    await nai3.send("脑积水已收到绘画指令, 正在生成图片(剩余次数: {})...".format(cd[gid]["user"][uid]["limit"]), at_sender=True)

    json_for_t2i["input"] = format_str(list_to_str(args.prompt))
    resolution = args.resolution if args.resolution else "mb"
    if resolution == "mb":
        width = 832
        height = 1216
    elif resolution == "pc":
        width = 1216
        height = 832
    elif resolution == "sq":
        width = height = 1024
    else:
        await nai3.finish("输入的图片大小有误捏~", at_sender=True)
    json_for_t2i["parameters"]["width"] = width
    json_for_t2i["parameters"]["height"] = height
    json_for_t2i["parameters"]["scale"] = args.scale if args.scale else 5.0
    json_for_t2i["parameters"]["sampler"] = args.sampler if args.sampler else "k_euler"
    json_for_t2i["parameters"]["steps"] = 28
    json_for_t2i["parameters"]["sm"] = args.sm if args.sm else False
    json_for_t2i["parameters"]["sm_dyn"] = args.smdyn if args.smdyn else False
    json_for_t2i["parameters"]["noise_schedule"] = args.schedule if args.schedule else "native"
    seed = random.randint(1000000000, 9999999999)
    json_for_t2i["parameters"]["seed"] = seed
    json_for_t2i["parameters"]["negative_prompt"] = format_str(list_to_str(args.negative)) if args.negative else nai3_config.nai3_negative

    logger.debug(">>>>>")
    logger.debug(json_for_t2i)

    try:
        async with AsyncClient() as client:
            response = await client.post("https://image.novelai.net/ai/generate-image", json=json_for_t2i, headers=headers, timeout=300)
            while response.status_code == 429:
                await asyncio.sleep(random.randint(4, 8))
                response = await client.post("https://image.novelai.net/ai/generate-image", json=json_for_t2i, headers=headers, timeout=300)
                logger.debug(response.status_code)
            logger.debug("<<<<<")
            with zipfile.ZipFile(io.BytesIO(response.content), mode="r") as zip:
                with zip.open("image_0.png") as image:
                    now_time = time.time()
                    cd[gid]["cool_time"] = now_time
                    cd[gid]["user"][uid]["limit"] = 999 if event.get_user_id() in bot.config.superusers else cd[gid]["user"][uid]["limit"] - 1
                    cd[gid]["user"][uid]["cool_time"] = now_time
                    await nai3.send(f"种子: {seed}\n" + MessageSegment.image(image.read()), at_sender=True)
                    return
    except Exception as e:
        await nai3.finish(f"出现错误: {e}", at_sender=True)


@nai3_black.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    text_msg = msg.extract_plain_text().strip()
    id = await get_at(event)
    if id == -1:
        id = text_msg.replace("添加", "").replace("删除", "").replace("群聊", "").replace("用户", "")

    if not os.path.exists("./data/nai3"):
        os.makedirs("./data/nai3")
        black_data = {"user": [], "group": []}
        with open("./data/nai3/black_data.json", "w", encoding="utf-8") as f:
            json.dump(black_data, f, indent=4, ensure_ascii=False)

    with open("./data/nai3/black_data.json", "r") as f:
        black_data = json.load(f)
    if "添加" in text_msg:
        if "群聊" in text_msg:
            black_data["group"].append(str(id))
        elif "用户" in text_msg:
            black_data["user"].append(str(id))
        else:
            await nai3_black.finish("输入有误!", at_sender=True)
        action_msg = "添加成功!"
    if "删除" in text_msg:
        if "群聊" in text_msg:
            black_data["group"].remove(str(id))
        elif "用户" in text_msg:
            black_data["user"].remove(str(id))
        else:
            await nai3_black.finish("输入有误!", at_sender=True)
        action_msg = "删除成功!"
    with open("./data/nai3/black_data.json", "w", encoding="utf-8") as f:
        json.dump(black_data, f, indent=4, ensure_ascii=False)
    await nai3_black.finish(action_msg, at_sender=True)
