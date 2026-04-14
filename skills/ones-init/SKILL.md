---
name: ones-init
description: ONES 工单系统登录初始化。触发词：/ones-init。全自动完成依赖安装和认证配置，用户只需钉钉扫码一次。
---

# ONES 登录初始化

## 执行原则

**AI 负责一切，用户只做一件事：用钉钉 App 扫码。**

所有依赖安装、脚本执行、Token 验证均由 AI 自动完成，不得提示用户手动执行任何命令。

---

## Step 1：检查 Token 是否有效

```python
import subprocess, os

ones_uid = os.environ.get("ONES_UID", "")
ones_lt  = os.environ.get("ONES_LT", "")
csrf     = os.environ.get("ONES_CSRF_TOKEN", "")

if not all([ones_uid, ones_lt, csrf]):
    print("NOT_SET")
else:
    r = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "https://works.yxt.com/project/api/project/team/Q5w8GzTz/members",
        "-H", f"x-csrf-token: {csrf}",
        "-b", f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
    ], capture_output=True, text=True)
    print(r.stdout.strip())
```

- 输出 `200` → Token 有效，跳到 Step 5 展示就绪状态
- 其他 → 继续 Step 2

---

## Step 2：自动安装依赖

直接执行，不询问用户：

```python
import subprocess, sys

def run(cmd, check=True):
    return subprocess.run(cmd, capture_output=True, text=True, check=check)

# 检查并安装 playwright Python 包
try:
    import playwright
except ImportError:
    print("📦 正在安装 playwright...")
    run([sys.executable, "-m", "pip", "install", "playwright", "--quiet"])

# 检查并安装 Chromium
r = run([sys.executable, "-m", "playwright", "install", "--dry-run"], check=False)
if "chromium" not in r.stdout.lower() or r.returncode != 0:
    print("📦 正在安装 Chromium（约 100MB，请稍候）...")
    run([sys.executable, "-m", "playwright", "install", "chromium"])

print("✅ 依赖就绪")
```

---

## Step 3：启动登录流程

**直接运行**刷新脚本，不提示用户手动执行：

```python
import subprocess, sys, os

script = os.path.expanduser(
    "~/.claude/plugins/marketplaces/ones-skill/skills/ones-ticket/scripts/refresh_token.py"
)

# 备用路径（直接安装场景）
if not os.path.exists(script):
    script = os.path.expanduser(
        "~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/ones-ticket/scripts/refresh_token.py"
    )

print("🌐 正在打开浏览器，请准备好钉钉 App...")
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  ⬇️  唯一需要你做的事：")
print("  📱 用钉钉 App 扫描弹出的二维码")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

subprocess.run([sys.executable, script])
```

脚本会自动完成：浏览器跳转 → 捕获 Cookie → 保存 `~/.ones_auth` → 写入 `~/.zshrc`

---

## Step 4：加载 Token 到当前环境

脚本完成后，自动 source 并验证：

```python
import subprocess, os, re

auth_file = os.path.expanduser("~/.ones_auth")

if not os.path.exists(auth_file):
    print("❌ 登录未成功，未找到 ~/.ones_auth，请重新执行 /ones-init")
else:
    # 读取并设置环境变量
    with open(auth_file) as f:
        for line in f:
            m = re.match(r'export (\w+)="(.+)"', line.strip())
            if m:
                os.environ[m.group(1)] = m.group(2)

    # 验证
    ones_uid = os.environ.get("ONES_UID", "")
    ones_lt  = os.environ.get("ONES_LT", "")
    csrf     = os.environ.get("ONES_CSRF_TOKEN", "")

    r = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "https://works.yxt.com/project/api/project/team/Q5w8GzTz/members",
        "-H", f"x-csrf-token: {csrf}",
        "-b", f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
    ], capture_output=True, text=True)

    if r.stdout.strip() == "200":
        print("LOGIN_OK")
    else:
        print(f"LOGIN_FAIL:{r.stdout.strip()}")
```

- `LOGIN_OK` → 继续 Step 5
- `LOGIN_FAIL` → 告知用户登录未成功，建议重新执行 `/ones-init`

---

## Step 5：展示就绪状态

```
✅ ONES 认证就绪！

用户 ID：{ONES_UID}
Token：已配置（验证通过）

现在可以使用：
• 建工单  — 创建需求 / 缺陷 / 任务
• 查工单  — 查询列表 / 详情 / 逾期统计
• 查迭代  — 查看 / 创建迭代
```

---

## 注意事项

- 新终端中 `ONES_UID` 等变量需要 `source ~/.ones_auth` 才生效，但 AI 执行 API 时会通过脚本内部读取，不受此影响
- Token 有效期约数天到数周，失效后重新执行 `/ones-init` 即可
