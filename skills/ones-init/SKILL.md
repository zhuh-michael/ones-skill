---
name: ones-init
description: ONES 工单系统登录初始化。触发词：/ones-init。检查认证状态，引导用户完成钉钉扫码登录，验证 Token 是否有效。
---

# ONES 登录初始化

## 触发场景

用户执行 `/ones-init` 时运行此流程。

## 执行步骤

### Step 1：检查当前认证状态

运行以下 Python 脚本检查环境变量和 Token 有效性：

```python
import subprocess, json, os

ones_uid = os.environ.get("ONES_UID", "")
ones_lt  = os.environ.get("ONES_LT", "")
csrf     = os.environ.get("ONES_CSRF_TOKEN", "")

if not all([ones_uid, ones_lt, csrf]):
    print("NOT_SET")
else:
    # 用一个轻量接口验证 token 是否有效
    r = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "https://works.yxt.com/project/api/project/team/Q5w8GzTz/members",
        "-H", f"x-csrf-token: {csrf}",
        "-b", f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
    ], capture_output=True, text=True)
    print(r.stdout.strip())
```

**判断逻辑：**
- 输出 `NOT_SET` → 环境变量未配置，执行 Step 2
- 输出 `200` → Token 有效，直接告知用户已就绪
- 输出 `401` / 其他 → Token 失效，执行 Step 2

### Step 2：引导登录

Token 未设置或已失效时，告知用户执行：

```
⚠️  ONES 认证未配置或已失效，需要重新登录。

请在终端执行以下命令（首次需要先安装依赖）：

# 首次安装（仅需一次）
pip install playwright && playwright install chromium

# 启动登录流程
python3 ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/ones-ticket/scripts/refresh_token.py
```

流程说明：
1. 脚本自动打开浏览器，跳转钉钉授权页
2. 用钉钉 App 扫码确认（唯一的人工步骤）
3. Token 自动保存到 `~/.ones_auth`，并写入 `~/.zshrc`

完成后执行：
```bash
source ~/.ones_auth
```

然后重新运行 `/ones-init` 验证是否成功。

### Step 3：验证并展示结果

Token 有效时展示：

```
✅ ONES 认证就绪！

用户 ID：{ONES_UID}
Token：已配置（有效）

现在可以使用以下能力：
• 建工单 — 创建需求/缺陷/任务
• 查工单 — 查询工单列表/详情
• 查迭代 — 查看当前迭代信息
```
