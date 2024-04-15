import asyncio
import io
import os
import random
import time
import zipfile
from argparse import Namespace
from importlib.metadata import version
from pathlib import Path

import ujson as json
from httpx import AsyncClient
from nonebot import require
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    Event,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.log import logger
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_command, on_shell_command
from nonebot.rule import ArgumentParser
from nudenet import NudeDetector

from .config import Config, nai3_config
from .utils import format_str, get_at, headers, json_for_t2i, list_to_str, proxies

require("nonebot_plugin_smms")
from nonebot_plugin_smms import SMMS  # noqa: E402, F401

ADMIN = SUPERUSER | GROUP_ADMIN | GROUP_OWNER
nude_detector = NudeDetector()
smms = SMMS()

try:
    __version__ = version("nonebot_plugin_nai3")
except Exception:
    __version__ = "0.0.0"

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-nai3",
    description="通过 NovelAI 生成图片",
    usage="nai3/nai prompt args",
    homepage="https://github.com/zhulinyv/nonebot_plugin_nai3",
    type="application",
    supported_adapters={"~onebot.v11"},
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
nai3_black = on_command(
    "nai3黑名单", aliases={"nai3 黑名单", "nai黑名单", "nai 黑名单"}, priority=20, permission=ADMIN, block=True
)
nai3_help = on_command("nai3帮助", aliases={"nai3 帮助", "nai帮助", "nai 帮助"}, priority=25, block=True)

cd = {}


@nai3.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    # 获取群号和 QQ 号
    if isinstance(event, PrivateMessageEvent):
        gid = uid = str(event.user_id)
    elif isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        uid = str(event.user_id)
    else:
        await nai3.send("不支持该聊天捏~请切换至群聊或私聊重试!", at_sender=True)

    # 读取黑名单并判断
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

    # 更新冷却时间和次数
    now_time = time.time()
    try:
        cd[gid]["user"][uid]["limit"]
    except KeyError:
        cd[gid] = {
            "cool_time": now_time - nai3_config.nai3_cooltime_group,
            "user": {
                uid: {
                    "limit": 999 if event.get_user_id() in bot.config.superusers else nai3_config.nai3_limit,
                    "cool_time": now_time - nai3_config.nai3_cooltime_user,
                }
            },
        }

    # 判断冷却时间并阻断
    if event.get_user_id() not in bot.config.superusers:
        logger.debug(event.get_user_id())
        logger.debug(bot.config.superusers)
        if now_time - cd[gid]["cool_time"] < nai3_config.nai3_cooltime_group:
            await nai3.finish(
                "群聊绘画冷却中, 剩余时间: {}...".format(
                    round(nai3_config.nai3_cooltime_group - now_time + cd[gid]["cool_time"], 3)
                ),
                at_sender=True,
            )
        if now_time - cd[gid]["user"][uid]["cool_time"] < nai3_config.nai3_cooltime_user:
            await nai3.finish(
                "个人绘画冷却中, 剩余时间: {}...".format(
                    round(nai3_config.nai3_cooltime_user - now_time + cd[gid]["cool_time"], 3)
                ),
                at_sender=True,
            )
        if cd[gid]["user"][uid]["limit"] <= 0:
            await nai3.finish("今天已经没次数了哦~", at_send=True)

    # 组装 json 数据
    await nai3.send(
        "脑积水已收到绘画指令, 正在生成图片(剩余次数: {})...".format(cd[gid]["user"][uid]["limit"]), at_sender=True
    )

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
    json_for_t2i["parameters"]["negative_prompt"] = (
        format_str(list_to_str(args.negative)) if args.negative else nai3_config.nai3_negative
    )

    logger.debug(">>>>>")
    logger.debug(json_for_t2i)

    now_time = time.time()
    cd[gid]["cool_time"] = now_time
    cd[gid]["user"][uid]["cool_time"] = now_time

    try:
        # 生成图片
        async with AsyncClient(proxies=proxies if nai3_config.nai3_proxy else None) as client:
            response = await client.post(
                "https://image.novelai.net/ai/generate-image", json=json_for_t2i, headers=headers, timeout=500
            )
            while response.status_code in [429, 500]:
                await asyncio.sleep(random.randint(4, 8))
                response = await client.post(
                    "https://image.novelai.net/ai/generate-image", json=json_for_t2i, headers=headers, timeout=500
                )
                logger.debug(response.status_code)
            logger.debug("<<<<<")
            with zipfile.ZipFile(io.BytesIO(response.content), mode="r") as zip:
                with zip.open("image_0.png") as image:
                    with open("./data/nai3/temp.png", "wb") as f:
                        f.write(image.read())

            cd[gid]["user"][uid]["limit"] = (
                999 if event.get_user_id() in bot.config.superusers else cd[gid]["user"][uid]["limit"] - 1
            )

            # 检测 R18
            if not nai3_config.nai3_r18:
                body = nude_detector.detect("./data/nai3/temp.png")
                safe = "safe"
                for part in body:
                    if part["class"] in [
                        "BUTTOCKS_EXPOSED",
                        "FEMALE_BREAST_EXPOSED",
                        "FEMALE_GENITALIA_EXPOSED",
                        "ANUS_EXPOSED",
                        "MALE_GENITALIA_EXPOSED",
                    ]:
                        safe = "R18"
                if safe == "R18":
                    await nai3.send("检测到 R18 内容, 不可以涩涩!", at_sender=True)
                    if nai3_config.smms_token:
                        file = await smms.upload(Path("./data/nai3/temp.png"))
                        for superuser in bot.config.superusers:
                            await bot.call_api(
                                "send_msg",
                                **{
                                    "message": file.url,
                                    "user_id": superuser,
                                },
                            )
                            asyncio.sleep(3)
                    return
            await nai3.send(f"种子: {seed}\n" + MessageSegment.image("./data/nai3/temp.png"), at_sender=True)
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


@nai3_help.handle()
async def _(bot: Bot, event: Event):
    msgs = []
    message_list = []
    message_list.append(
        """指令: nai3/nai
参数:
prompt          提示词(支持你喜欢的画风串), 默认: None
-n/--negative   负面提示词, 默认: nsfw,...
-r/--resolution 画布形状/分辨率, ["mb", "pc", "sq"] 三选一, 默认: mb
-s/--scale      提示词相关性, 默认: 5.0
-sm             sm, 默认: False
-smdyn          smdyn, 默认: False
--sampler       采样器, 默认: k_euler
--schedule      噪声计划表, 默认: native
示例: nai3 1girl, loli, cute -r mb -s 5.0"""
    )
    message_list.append(MessageSegment.image("https://github.com/zhulinyv/nonebot_plugin_nai3/raw/main/img/1.png"))
    message_list.append(
        """指令: nai3黑名单/nai黑名单(需要超级用户, 群主或群管理员权限)
参数:
添加    添加黑名单
删除    删除黑名单
用户    指定添加类型
群聊    指定添加类型
群号/QQ号/@sb.
示例: nai3黑名单添加用户 @脑积水"""
    )
    message_list.append(MessageSegment.image("https://github.com/zhulinyv/nonebot_plugin_nai3/raw/main/img/2.png"))
    message_list.append("指令: nai3帮助\n返回: 展示以上帮助")
    if isinstance(event, GroupMessageEvent):
        for msg in message_list:
            msgs.append({"type": "node", "data": {"name": "脑积水", "uin": bot.self_id, "content": msg}})
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=msgs)
    else:
        for msg in message_list:
            await nai3_help.send(msg)
            await asyncio.sleep(0.5)
        return
