# ONES Ticket Skill for Claude Code

在 Claude Code 中直接管理 ONES 工单系统——创建需求、缺陷、任务，查询工单列表，管理迭代，添加评论和附件。

## 安装

### 方式一：一键安装脚本

```bash
bash install.sh
```

### 方式二：手动安装

将 `ones-ticket/` 和 `ones-init/` 目录复制到：

```
~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/
```

安装 Python 依赖（Token 刷新脚本需要）：

```bash
pip install playwright && playwright install chromium
```

## 首次配置

安装完成后，在 Claude Code 中执行：

```
/ones-init
```

按提示完成钉钉扫码登录，Token 自动保存到 `~/.ones_auth`。

## 使用方法

### 创建工单

直接用自然语言描述，触发词：**建工单**

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
| 缺陷 | 报错、异常、Bug | 标题、故障平台/账号、优先级 |
| 任务 | 任务、开发任务 | 标题、所属迭代、任务类别 |

## 完整能力列表

| 能力 | 状态 |
|------|------|
| 创建需求 | ✅ |
| 创建缺陷（含自动优先级判断） | ✅ |
| 创建任务（含迭代+类别） | ✅ |
| 查询工单列表 | ✅ |
| 按 UUID 查工单详情 | ✅ |
| 未关闭缺陷精确查询 | ✅ |
| 逾期工单统计 | ✅ |
| 工单状态流转 | ✅ |
| 添加评论 | ✅ |
| 附件/截图上传 | ✅ |
| 人员搜索 | ✅ |
| 查询迭代列表 | ✅ |
| 创建迭代（需 ManageSprints 权限） | ✅ |
| Token 一键刷新 | ✅ |

## Token 过期处理

认证失效时（HTTP 401），重新登录：

```bash
python3 ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/ones-ticket/scripts/refresh_token.py
source ~/.ones_auth
```

或在 Claude Code 中执行 `/ones-init`。

## 项目配置

本 Skill 预配置了以下固定值（如需适配其他项目请修改 `references/fields.md`）：

| 参数 | 值 |
|------|-----|
| 团队 | Q5w8GzTz |
| 项目 | 慧销（SaleSmart）|
| ONES 域名 | works.yxt.com |
