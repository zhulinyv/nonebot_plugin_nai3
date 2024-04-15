from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .config import nai3_config

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6",
    "Authorization": f"Bearer {nai3_config.nai3_token}",
    "Referer": "https://novelai.net",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    "Sec-Ch-Ua-mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",  # noqa: E501
}


json_for_t2i = {
    "input": str,
    "model": "nai-diffusion-3",
    "action": "generate",
    "parameters": {
        "params_version": 1,
        "width": int,
        "height": int,
        "scale": float,
        "sampler": str,
        "steps": int,
        "n_samples": 1,
        "ucPreset": 0,
        "qualityToggle": True,
        "sm": bool,
        "sm_dyn": bool,
        "dynamic_thresholding": False,
        "controlnet_strength": 1,
        "legacy": False,
        "add_original_image": False,
        "uncond_scale": 1,
        "cfg_rescale": 0,
        "noise_schedule": str,
        "legacy_v3_extend": False,
        "seed": int,
        "negative_prompt": str,
        "reference_image_multiple": [],
        "reference_information_extracted_multiple": [],
        "reference_strength_multiple": [],
    },
}

try:
    proxies = {
        "http://": "http://" + nai3_config.nai3_proxy,
        "https://": "http://" + nai3_config.nai3_proxy,
    }
except Exception:
    proxies = None


def list_to_str(str_list: list):
    empty_str = ""
    for i in str_list:
        if i[-1] == ",":
            empty_str += f"{i}"
        else:
            empty_str += f"{i},"
    return empty_str


def format_str(str_: str):
    str_ = str_.replace(", ", ",")
    str_ = str_.replace(",", ", ")
    str_ = str_[:-2] if str_[-2:] == ", " else str_
    return str_


async def get_at(event: GroupMessageEvent) -> int:
    msg = event.get_message()
    for msg_seg in msg:
        if msg_seg.type == "at":
            return -1 if msg_seg.data["qq"] == "all" else int(msg_seg.data["qq"])
    return -1
