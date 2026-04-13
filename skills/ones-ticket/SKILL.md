---
name: ones-ticket
description: 解析用户提供的文案内容，自动识别工单类型（需求/缺陷/查询），展示结构化表单二次确认，然后调用 ONES 工单系统 API 创建工单或查询工单列表。主要触发词：「建工单」。其他触发场景：提工单、创建工单、新建需求、报缺陷、查询工单、工单列表等。
---

# ONES 工单助手

## 工作流程

### 第一步：内容分析与类型识别

分析用户输入，判断意图：

| 类型 | 识别信号 | issue_type_uuid |
|------|---------|-----------------|
| **需求** | 希望增加功能、优化体验、新增能力 | `CyqmgJVm` |
| **缺陷** | 出现错误、功能异常、Bug、报错、客户反馈异常 | `H1pqkZQF` |
| **查询** | 查看工单列表、进度查询、状态查询 | 无需创建，执行查询 |

若无法确定类型，直接问用户："这个问题是**需求**（新功能）、**缺陷**（功能异常）还是要**查询**现有工单？"

### 第二步：信息提取与缺失补全

从用户文案中提取字段，**对缺失的必填项主动逐一提问，不得留空创建**。

#### 需求必填项

| 字段 | 说明 | 缺失时提问示例 |
|------|------|--------------|
| 标题 | 一句话概括，≤50字 | 自动生成，可让用户确认 |
| 慧销业务模块 | 销售端/团队端/管理后台/即时赋能教练（必填） | "这个需求属于哪个业务模块？销售端、团队端、管理后台还是即时赋能教练？" |
| 功能模块 | 涉及哪个具体功能区域（描述字段） | "涉及哪个功能模块？" |
| 场景描述(why) | 为什么需要/业务背景 | "能描述一下使用场景或背景吗？" |
| 期望结果 | 希望达成的效果 | "期望的效果是什么？" |

#### 缺陷必填项

| 字段 | 说明 | 缺失时提问示例 |
|------|------|--------------|
| **标题前缀** | `【环境-标识】`格式，见下方规则 | "是产线（R）还是测试环境（tf）的问题？客户/功能是？" |
| 标题 | 前缀 + 一句话概括，≤50字 | 自动生成，可让用户确认 |
| 故障平台 | 平台域名/机构名称 | "是哪个平台或客户机构出现的问题？" |
| 故障账号 | 出问题的账号 | "是哪个账号遇到的问题？" |
| 操作步骤 | 如何复现 | "能描述一下触发步骤吗？" |
| 当前结果 | 实际发生了什么 | 通常可从用户描述提取 |
| 期望结果 | 应该是什么效果 | "期望的正确表现是什么？" |
| 优先级 | P0/P1/P2（见判断标准） | 根据描述自动判断并在表单中标注，用户可修改 |

#### 缺陷标题前缀规则（必须遵守）

格式：`【{环境}-{标识}】{标题内容}`

| 环境 | 标识规则 | 示例 |
|------|---------|------|
| `R`（产线） | 客户名称 或 技术问题分类（如"性能"） | `【R-wuxx-demo】录制处理超时` |
| `tf`（测试） | 功能名称（tf下无客户） | `【tf-ASR标注】识别结果不准确` |

**提取逻辑：**
- 用户描述中有"产线/客户/线上"关键词 → 环境 = `R`，从描述中提取客户名
- 用户描述中有"测试/tf/test"关键词 → 环境 = `tf`，提取功能名
- 无法判断 → 直接问："这个问题是**产线（R）**还是**测试环境（tf）**？"
- 客户名/功能名无法从描述提取 → 追问一次

最终标题 = `【环境-标识】` + 一句话概括（确保总长度 ≤ 50 字）

**提问原则：** 一次最多问 2 个问题，避免让用户填写"表格"。信息凑齐后再展示确认卡片。

### 第三步：缺陷优先级判断

根据用户描述自动判断优先级，在确认卡片中展示供用户调整：

| 优先级 | field_uuid值 | 判断标准 | 截止要求 |
|--------|-------------|---------|---------|
| **P0** | `FFbZ7ebB` | 影响产线用户使用，阻碍流程执行，或看板数据错误有误导 | 当天上线解决 |
| **P1** | `9R94zH1j` | 不影响核心流程，有临时方案，但有额外操作负担或视觉影响 | 3天内解决 |
| **P2** | `ACKSasRN` | 不影响流程，仅交互/视觉体验问题，需教育用户 | 10天内解决 |

优先级对应截止日期（从今日起算）：P0=当日，P1=+3天，P2=+10天。

### 第四步：结构化确认卡片

**需求确认卡片：**
```
📋 工单信息确认（需求）
─────────────────────────────
标题：    [标题]
功能模块：[模块]

【功能模块】[内容]
【场景描述(why)】[内容]
【期望结果】[内容]
【截图】如有

─────────────────────────────
确认创建？（是 / 需要修改：xxx）
```

**缺陷确认卡片：**
```
📋 工单信息确认（缺陷）
─────────────────────────────
标题：    [标题]
优先级：  P0🔴 / P1🟠 / P2🟡  [判断依据一句话说明]
截止日期：[根据优先级自动计算]

【故障平台】[内容]
【故障账号】[内容]
【操作步骤】[内容]
【相关链接】[如有]
【当前结果】[内容]
【期望结果】[内容]
【截图/录屏】如有

─────────────────────────────
确认创建？（是 / 需要修改：xxx）
```

**收到用户确认后才执行 API**，有修改则更新后重新展示卡片。

### 第五步：执行 API 操作

读取认证环境变量（详见 references/auth.md）。始终使用 **Python inline 脚本**调用 API（避免 shell 转义问题）。字段映射详见 references/fields.md。

**创建工单端点**：`POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/tasks/add3`（注意是 `add3`，不是 `tasks`）

#### 创建需求

```python
payload = {
    "tasks": [{
        "uuid": task_uuid,           # ONES_UID + 8位随机大写字母数字
        "assign": ones_uid,
        "summary": summary,
        "parent_uuid": "",
        "issue_type_uuid": "CyqmgJVm",
        "project_uuid": "Gq9erDiKJ1trVL1V",
        "watchers": [ones_uid],
        "field_values": [
            {"field_uuid": "field001", "type": 2, "value": summary},
            {"field_uuid": "field004", "type": 8, "value": ones_uid},
            {"field_uuid": "field016", "type": 20, "value": description_html},
            {"field_uuid": "7RjjyZkN", "type": 1, "value": module_uuid},    # 慧销业务模块（必填，见fields.md）
            {"field_uuid": "field012", "type": 1, "value": "NroP1UGJ"},   # 优先级默认 Major
            {"field_uuid": "field011", "type": 7, "value": None}
        ],
        "add_manhours": [{"hours": None, "mode": "simple", "type": "estimated"}]
    }]
}
```

需求描述 HTML 模板（field016）：
```html
<p><span>【功能模块】{内容}</span></p>
<p><span>【场景描述(why)】{内容}</span></p>
<p><span>【期望结果】{内容}</span></p>
<p><span>【截图】如有</span></p>
```

#### 创建缺陷

```python
# 截止日期按优先级计算
deadline_days = {"P0": 0, "P1": 3, "P2": 10}[priority]
deadline_dt = datetime.now(timezone.utc) + timedelta(days=deadline_days)
deadline_ts  = int(deadline_dt.replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
deadline_str = deadline_dt.strftime("%Y-%m-%d")

priority_uuid = {"P0": "FFbZ7ebB", "P1": "9R94zH1j", "P2": "ACKSasRN"}[priority]
priority_field_uuid = "待确认"   # 需要补充优先级的 field_uuid

payload = {
    "tasks": [{
        "uuid": task_uuid,
        "assign": ones_uid,
        "summary": summary,
        "parent_uuid": "",
        "issue_type_uuid": "H1pqkZQF",
        "project_uuid": "Gq9erDiKJ1trVL1V",
        "watchers": [ones_uid],
        "field_values": [
            {"field_uuid": "field001", "type": 2, "value": summary},
            {"field_uuid": "field004", "type": 8, "value": "VgmUb3N1"},       # 缺陷默认负责人：吴名先
            {"field_uuid": "field013", "type": 5, "value": deadline_ts, "date_value": deadline_str},  # ★必填
            {"field_uuid": "2KzQcUwN", "type": 1, "value": priority_uuid},    # 缺陷优先级 P0/P1/P2
            {"field_uuid": "field016", "type": 20, "value": description_html}, # ★必填
            {"field_uuid": "field011", "type": 7, "value": None}
        ],
        "add_manhours": [{"hours": None, "mode": "simple", "type": "estimated"}]
    }]
}
```

缺陷描述 HTML 模板（field016）：
```html
<p><span style="color:#000000; font-size:medium">【故障平台】</span><em><span style="color:#c0c0c0">{平台域名/机构名称}</span></em></p>
<p><span style="color:#000000; font-size:medium">【故障账号】</span><em><span style="color:#c0c0c0">{账号名称}</span></em><br />
<span style="color:#000000; font-size:medium">【操作步骤】</span>{内容}<br />
<span style="color:#000000; font-size:medium">【相关链接】</span><em><span style="color:#c0c0c0">{如有}</span></em><br />
<span style="color:#000000; font-size:medium">【当前结果】</span>{内容}<br />
<span style="color:#000000; font-size:medium">【期望结果】</span>{内容}<br />
<span style="color:#000000; font-size:medium">【截图/录屏】</span><em><span style="color:#c0c0c0">请插入图片/上传录屏（如有）</span></em></p>
```

创建成功后展示：
```
✅ 工单创建成功！
标题：[标题]
优先级：[P0/P1/P2]  截止：[日期]
链接：https://works.yxt.com/project/#/team/Q5w8GzTz/task/[uuid]
```

### 错误处理

- **HTTP 401**：认证失效，提示运行 `python3 scripts/refresh_token.py` 扫码刷新
- **MissingParameter**：检查必填字段，重新展示表单
- **网络错误**：检查是否在公司网络/VPN 环境

## 参考文档

- **认证配置**：[references/auth.md](references/auth.md)
- **字段映射**：[references/fields.md](references/fields.md) — 含所有 UUID 对照表
- **查询 API**：[references/query-api.md](references/query-api.md)
