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

    plugins = ["nonebot_plugin_hoshino_sign"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| nai3_token | 是 | str | xxx | 请求头中必需的 token |

⚠️ token 的获取:

- 1.登录 https://novelai.net/login
- 2.F12 打开控制台并切换到控制台
- 3.输入 `console.log(JSON.parse(localStorage.session).auth_token)` 回车, 返回的字符串即为 token
- ![e3756ce75c6f6850efa633dbaa3a5ae6](https://github.com/zhulinyv/Semi-Auto-NovelAI-to-Pixiv/assets/66541860/502c9a49-6a73-446d-9401-e559628ad079)

## 🎉 使用

| 指令 | 参数 | 示例 | 结果 |
|:---:|:---:|:---:|:---:|
| nai3 | prompt | nai3 1girl, loli, cute | ![img](./img/8356736520_None_None.png) |

## 📖 待办

+ [x] 文生图
+ [ ] 图生图
+ [ ] 自定义参数
+ [ ] 队列功能
+ [ ] 冷却功能
+ [ ] 上限功能
+ [ ] 黑名单功能
+ [ ] ...

## 🤝 鸣谢

本项目逐步迁移自 [Semi-Auto-NovelAI-to-Pixiv](https://github.com/zhulinyv/Semi-Auto-NovelAI-to-Pixiv) 


<hr>
<img width="300px" src="https://count.getloli.com/get/@zhulinyv?theme=rule34"></img>