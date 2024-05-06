<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/raw/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/raw/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<h1 align="center">nonebot_plugin_nai3</h1>
<h4 align="center">✨通过 NovelAI 生成图片✨</h4>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.9+-blue">
    <a href="https://github.com/zhulinyv/nonebot_plugin_nai3/raw/main/LICENSE"><img src="https://img.shields.io/github/license/zhulinyv/nonebot_plugin_nai3" alt="license"></a>
    <img src="https://img.shields.io/github/issues/zhulinyv/nonebot_plugin_nai3">
    <img src="https://img.shields.io/github/stars/zhulinyv/nonebot_plugin_nai3">
    <img src="https://img.shields.io/github/forks/zhulinyv/nonebot_plugin_nai3">
</p>

## 💬 介绍

通过 Post 请求 NovelAI 官网生成图片, **因此你需要购买 NovelAI 会员才可以使用本插件**

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-nai3

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-nai3
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-nai3
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-nai3
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-nai3
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_nai3"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| nai3_token | 是 | str | "xxx" | 请求头中必需的 token |
| nai3_negative | 否 | str | "nsfw,..." | 负面提示词 |
| nai3_limit | 否 | int | 10 | 每人最多生成次数 |
| nai3_cooltime_group | 否 | int | 30 | 群聊画图冷却时间(单位: 秒) |
| nai3_cooltime_user | 否 | int | 300 | 个人画图冷却时间(单位: 秒) |
| nai3_proxy | 否 | str | None | post 请求生成图片使用的代理 |
| nai3_r18 | 否 | bool | False | 是否允许 R18 图片(False 将会把图片链接发给超级用户) |
| nai3_send_to_group | 否 | bool | True | 是否允许将图片链接发送到群 |
| nai3_save | 否 | bool | False | 是否将用户生成的图片保存 |
| nai3_save_path | 否 | str | "./data/nai3/img" | 图片保存位置 |
| SMMS_API_URL | 否 | str | "https://sm.ms/api/v2" | SMMS 图床 API 地址 |
| SMMS_TOKEN | 是 | str | "xxx" | 不配置将损失一张 R18 图片(bushi) |

⚠️ token 的获取:

- 1.登录 https://novelai.net/login
- 2.F12 打开控制台并切换到控制台
- 3.输入 `console.log(JSON.parse(localStorage.session).auth_token)` 回车, 返回的字符串即为 token
- ![e3756ce75c6f6850efa633dbaa3a5ae6](https://github.com/zhulinyv/Semi-Auto-NovelAI-to-Pixiv/assets/66541860/502c9a49-6a73-446d-9401-e559628ad079)

⚠️ SMMS token 的获取:

- 登录SM.MS"
- 点击"Sign Up"注册一个账号"
- 输入账号邮箱和密码"
- 点击"User" > "Dashboard""
- 点击"API Token", 就可以看到Token, 复制即可使用"

## 🎉 使用

```
指令: nai3/nai
参数:
    prompt          提示词(支持你喜欢的画风串), 默认: None
    -n/--negative   负面提示词, 默认: nsfw,...
    -r/--resolution 画布形状/分辨率, ["mb", "pc", "sq"] 三选一, 默认: mb
    -s/--scale      提示词相关性, 默认: 5.0
    -sm             sm, 默认: False
    -smdyn          smdyn, 默认: False
    --sampler       采样器, 默认: k_euler
    --schedule      噪声计划表, 默认: native
示例: nai3 1girl, loli, cute -r mb -s 5.0
返回: 
```

![img](./img/1.png)

```
指令: nai3黑名单/nai黑名单(需要超级用户, 群主或群管理员权限)
参数:
    添加    添加黑名单
    删除    删除黑名单
    用户    指定添加类型
    群聊    指定添加类型
    群号/QQ号/@sb.
示例: nai3黑名单添加用户 @脑积水
返回: 
```

![img](./img/2.png)

```
指令: nai3帮助/nai帮助
返回: 展示以上帮助
```

## 📖 待办

+ [x] 文生图
+ [ ] 图生图
+ [x] 自定义参数
+ [ ] ~~队列功能~~
+ [x] 冷却功能
+ [x] 上限功能
+ [x] 黑名单功能
+ [x] 代理
+ [x] R18 检测
+ [ ] 翻译
+ [x] 帮助指令
+ [x] 检测到 R18 图片生成链接并上报超级用户
+ [x] 图片保存
+ [ ] 分群配置
+ [ ] 每日人设
+ [ ] 提示词反推
+ [ ] 法术解析
+ [ ] ...

## 🤝 鸣谢

本项目逐步迁移自 [Semi-Auto-NovelAI-to-Pixiv](https://github.com/zhulinyv/Semi-Auto-NovelAI-to-Pixiv)

本项目使用 [nonebot-plugin-smms](https://github.com/mobyw/nonebot-plugin-smms) 上传图片


<hr>
<img width="300px" src="https://count.getloli.com/get/@zhulinyv?theme=rule34"></img>
