#!/usr/bin/env python3
"""
ONES Token Refresher
自动完成钉钉 OAuth → ONES 登录流程，用户只需扫一次码。

依赖：pip install playwright && playwright install chromium
用法：python3 refresh_token.py
"""

import asyncio
import os
import sys

DINGTALK_OAUTH_URL = (
    "https://login.dingtalk.com/oauth2/challenge.htm"
    "?redirect_uri=https%3A%2F%2Ftianhe.yxt.com%2F%23%2Flogin-with-dingtalk-qr"
    "&response_type=code"
    "&client_id=dingfebp4qduibguwbdz"
    "&scope=openid"
    "&state=https%3A%2F%2Ftianhe.yxt.com%2Fsso%2F%3Fclient_id%3Dones"
    "%26redirect_uri%3Dhttps%253A%252F%252Fworks.yxt.com%252Fplugin%252F8mGqKxYT"
    "%252FQ5w8GzTz%252FoLK5mqk3%252F1.1.6%252Fmodules%252Fabout-blank-N14c%252Findex.html"
    "%26state%3Dhttps%253A%252F%252Fworks.yxt.com%252Fproject%252F%253FbindedOrgUUID"
    "%253D8mGqKxYT%2526ones_from%253Dhttps%25253A%25252F%25252Fworks.yxt.com%25252F"
    "project%25252F%252523%25252Fworkspace%2526redirect_path%253D%2525252Fauth%2525252F"
    "third_login%2526type%253D106885706%2526instanceId%253D709ca485"
    "&prompt=consent"
)

ENV_FILE = os.path.expanduser("~/.ones_auth")
TIMEOUT_SECONDS = 300


async def refresh():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ 缺少依赖，请先执行：")
        print("   pip install playwright && playwright install chromium")
        sys.exit(1)

    result = {"ones_uid": None, "ones_lt": None, "csrf_token": None}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        async def try_capture_cookies():
            """从 works.yxt.com 捕获 ONES session cookies"""
            cookies = await context.cookies("https://works.yxt.com")
            for c in cookies:
                if c["name"] == "ones-lt" and c["value"]:
                    result["ones_lt"] = c["value"]
                elif c["name"] == "ones-uid" and c["value"]:
                    result["ones_uid"] = c["value"]
                elif c["name"] == "ct" and c["value"]:
                    result["csrf_token"] = c["value"]

        async def on_response(response):
            url = response.url
            # 覆盖多种可能触发 cookie 写入的关键请求
            if any(kw in url for kw in [
                "tianhe/login",
                "auth/token_info",
                "third_login",
                "works.yxt.com/project/api",
            ]):
                await try_capture_cookies()

        async def on_url_change(url):
            # 落地到 works.yxt.com 即视为登录完成
            if "works.yxt.com/project" in url:
                await asyncio.sleep(1)  # 等待 cookie 写入
                await try_capture_cookies()

        page.on("response", on_response)
        page.on("framenavigated", lambda frame: asyncio.ensure_future(
            on_url_change(frame.url)
        ))

        print("🌐 正在打开钉钉授权页面...")
        await page.goto(DINGTALK_OAUTH_URL)
        print("📱 请用钉钉 App 扫码授权（等待中，最长 5 分钟）...")
        print()

        for i in range(TIMEOUT_SECONDS):
            if all(result.values()):
                break
            await asyncio.sleep(1)
            # 每隔 5 秒主动尝试一次捕获（兜底）
            if i > 0 and i % 5 == 0:
                await try_capture_cookies()
            if i > 0 and i % 30 == 0:
                print(f"   仍在等待... ({i}s)")

        await browser.close()

    if all(result.values()):
        _save_tokens(result["ones_uid"], result["ones_lt"], result["csrf_token"])
        return True
    else:
        print("❌ 超时未获取到 token，请重试")
        return False


def _save_tokens(ones_uid, ones_lt, csrf_token):
    content = (
        f'export ONES_UID="{ones_uid}"\n'
        f'export ONES_LT="{ones_lt}"\n'
        f'export ONES_CSRF_TOKEN="{csrf_token}"\n'
    )
    with open(ENV_FILE, "w") as f:
        f.write(content)
    os.chmod(ENV_FILE, 0o600)

    print("✅ 登录成功，Token 已保存！")
    print()
    print(f"   ONES_UID:  {ones_uid}")
    print(f"   ONES_LT:   {ones_lt[:20]}...")
    print(f"   CSRF_TOKEN:{csrf_token[:20]}...")
    print()
    print("执行以下命令使其在当前终端生效：")
    print(f"   source {ENV_FILE}")
    print()

    zshrc = os.path.expanduser("~/.zshrc")
    source_line = f'[ -f {ENV_FILE} ] && source {ENV_FILE}'
    if os.path.exists(zshrc):
        with open(zshrc, "r") as f:
            existing = f.read()
        if ENV_FILE not in existing:
            with open(zshrc, "a") as f:
                f.write(f"\n# ONES Auth Token\n{source_line}\n")
            print(f"✅ 已自动写入 ~/.zshrc，新终端将自动加载")


if __name__ == "__main__":
    success = asyncio.run(refresh())
    sys.exit(0 if success else 1)
