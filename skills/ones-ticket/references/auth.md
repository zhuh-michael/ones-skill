# ONES 认证配置

## 认证方式

ONES 使用钉钉 OAuth 登录，session 凭证存储在 Cookie 中，会定期失效。

使用 `scripts/refresh_token.py` 可一键刷新，**用户只需扫一次码**，其余流程全自动完成。

## 一键刷新 Token

```bash
# 首次安装依赖（仅需一次）
pip install playwright && playwright install chromium

# 刷新 token（session 失效时运行）
python3 ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/ones-ticket/scripts/refresh_token.py
```

脚本会：
1. 自动打开浏览器，跳转钉钉授权页
2. 你用钉钉 App 扫码确认（唯一的人工步骤）
3. 自动捕获 ones-lt、ones-uid、ct 并保存到 `~/.ones_auth`
4. 自动写入 `~/.zshrc`，新终端自动加载

## 所需环境变量

| 变量名 | Cookie 来源 | 说明 |
|--------|------------|------|
| `ONES_UID` | `ones-uid` | 用户 ID，稳定不变 |
| `ONES_LT` | `ones-lt` | 登录 Token，会过期 |
| `ONES_CSRF_TOKEN` | `ct` | CSRF Token，与 ones-lt 同步 |

## OAuth 链路说明

```
钉钉扫码 → authCode
  → POST /tianhe/oauth/dingdingScan   换取 SSO token
  → GET  /tianhe/oauth/authorize      换取 ONES code (oc-xxx)
  → GET  /works.yxt.com/tianhe/login  换取 ones-lt + ct cookie
```

## 当前已知配置

| 参数 | 值 |
|------|----|
| 钉钉 client_id | `dingfebp4qduibguwbdz` |
| ONES client_id | `ones` |
| 中间层域名 | `api-info.yunxuetang.cn` |
| ONES 域名 | `works.yxt.com` |

## 错误处理

- **HTTP 401**：运行 refresh_token.py 刷新 token
- **脚本超时（5分钟）**：检查是否在钉钉 App 完成了授权确认
- **playwright 报错**：确认已执行 `playwright install chromium`
