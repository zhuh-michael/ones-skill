# ones-skill — ONES 工单系统 Claude Code Skill

在 Claude Code 中直接管理 ONES 工单系统——创建需求、缺陷、任务，查询工单列表，管理迭代，添加评论和附件。

## 安装

```bash
claude plugin add git@github.com:zhuh-michael/ones-skill.git
```

Claude Code 会自动下载并注册 `ones-ticket` 和 `ones-init` 两个 skill。

## 更新

```bash
claude plugin update ones-skill
```

## 首次配置

安装完成后，在 Claude Code 中执行登录初始化：

```
/ones-init
```

流程：
1. 执行 `/ones-init`，检测认证状态
2. 若未配置，按提示在终端运行扫码脚本：
   ```bash
   pip install playwright && playwright install chromium   # 首次需要
   python3 ~/.claude/plugins/marketplaces/ones-skill/skills/ones-ticket/scripts/refresh_token.py
   ```
3. 用钉钉 App 扫码授权（唯一手动步骤）
4. Token 自动保存到 `~/.ones_auth` 并写入 `~/.zshrc`
5. 再次执行 `/ones-init` 验证是否就绪

## 使用方法

### 创建工单

触发词：**建工单**

```
建工单 客户反馈登录页面白屏，Safari 浏览器必现
建工单 希望在报表页面增加数据导出为 Excel 的功能
```

Skill 会自动：
1. 识别工单类型（需求 / 缺陷 / 任务）
2. 提取关键字段，缺失时主动询问
3. 展示确认卡片，等待确认后创建

### 查询工单

```
查一下我的未关闭缺陷
统计逾期超过3个月的工单
本期迭代有哪些任务
```

### 其他操作

- 更新状态：`把工单 xxx 改为需求设计中`
- 添加评论：`在工单 xxx 添加评论：已确认可以复现`
- 上传截图：`更新截图 [附图]`
- 查询迭代：`当前有哪些进行中的迭代`
- 创建迭代：`创建一个新迭代，名称 2026V7，4月14日到4月30日`

## 支持的工单类型

| 类型 | 触发信号 | 关键必填字段 |
|------|---------|------------|
| 需求 | 新增功能、优化体验 | 标题、慧销业务模块 |
| 缺陷 | 报错、异常、Bug | 标题前缀【R/tf-xxx】、故障平台/账号、优先级 |
| 任务 | 任务、开发任务 | 标题、所属迭代、任务类别 |

## 完整能力列表

| 能力 | 状态 |
|------|------|
| 创建需求 | ✅ |
| 创建缺陷（含自动优先级判断 + 标题前缀规则） | ✅ |
| 创建任务（含迭代 + 类别） | ✅ |
| 查询工单列表 | ✅ |
| 按 UUID 查工单详情 | ✅ |
| 未关闭缺陷精确查询 | ✅ |
| 逾期工单统计 | ✅ |
| 工单状态流转 | ✅ |
| 添加评论 | ✅ |
| 附件 / 截图上传 | ✅ |
| 人员搜索 | ✅ |
| 查询迭代列表 | ✅ |
| 创建迭代（需 ManageSprints 权限） | ✅ |
| Token 一键刷新 | ✅ |

## Token 过期处理

认证失效时（HTTP 401），在 Claude Code 中执行：

```
/ones-init
```

或直接在终端运行：

```bash
python3 ~/.claude/plugins/marketplaces/ones-skill/skills/ones-ticket/scripts/refresh_token.py
source ~/.ones_auth
```

## 项目配置

本 Skill 预配置了以下固定值（如需适配其他项目请修改 `skills/ones-ticket/references/fields.md`）：

| 参数 | 值 |
|------|-----|
| 团队 | Q5w8GzTz |
| 项目 | 慧销（SaleSmart）|
| ONES 域名 | works.yxt.com |
