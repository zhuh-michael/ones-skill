# ONES 字段映射表

## 团队与项目配置（固定值）

| 参数 | 值 |
|------|----|
| team_uuid | `Q5w8GzTz` |
| project_uuid | `Gq9erDiKJ1trVL1V` |
| scope_uuid（需求） | `ThX6Rfd2` |
| scope_uuid（缺陷） | `D1DSpcGK` |

## Issue Type UUID

| 工单类型 | issue_type_uuid |
|---------|-----------------|
| 需求 | `CyqmgJVm` |
| 缺陷 | `H1pqkZQF` |

---

## 需求字段（ThX6Rfd2）

API 调用时只需传入以下字段，其余系统字段服务端自动处理：

| field_uuid | 字段名 | type | 必填 | 说明 |
|-----------|--------|------|------|------|
| `field001` | 标题 | 2 | ★ | 工单标题 |
| `field004` | 负责人 | 8 | ★ | 默认创建者（`$taskCreator` = ones-uid） |
| `7RjjyZkN` | 慧销业务模块 | 1 | ★ | 必须用户选择，见选项表 |
| `field012` | 优先级 | 1 | — | 默认 `NroP1UGJ`（Major B重要） |
| `field016` | 描述 | 20 | — | HTML 格式，见描述模板 |
| `field011` | 所属迭代 | sprint | — | 传 null |

### 慧销业务模块选项（`7RjjyZkN`）

| 模块名称 | option_uuid |
|---------|-------------|
| 销售端 | `1mJHearv` |
| 团队端 | `WCDHjATA` |
| 管理后台 | `DikSqKW3` |
| 即时赋能教练 | `NKLarW3b` |

### 需求优先级选项（`field012`）

| 优先级 | option_uuid | 备注 |
|--------|-------------|------|
| P0 | `UcuNeHU6` | |
| P1 | `GuRdLz3d` | |
| P2 | `NMJqMtZY` | |
| P3 | `UWx6vf67` | |
| Major（B重要） | `NroP1UGJ` | **系统默认值** |
| Minor（C次要） | `7s6QdQQi` | |

### 需求描述模板（`field016`，HTML）

```html
<p><span>【功能模块】{内容}</span></p>
<p><span>【当前结果】{内容}</span></p>
<p><span>【场景描述(why)】{内容}</span></p>
<p><span>【期望结果】{内容}</span></p>
<p><span>【截图】如有</span></p>
```

### 需求 field_values 完整结构

```python
[
    {"field_uuid": "field001", "type": 2,  "value": summary},
    {"field_uuid": "field004", "type": 8,  "value": ones_uid},         # 负责人=创建者
    {"field_uuid": "7RjjyZkN", "type": 1,  "value": module_uuid},      # 慧销业务模块★必填
    {"field_uuid": "field012", "type": 1,  "value": "NroP1UGJ"},       # 优先级默认 Major
    {"field_uuid": "field016", "type": 20, "value": description_html},
    {"field_uuid": "field011", "type": 7,  "value": None},
]
```

---

## 缺陷字段（D1DSpcGK）

| field_uuid | 字段名 | type | 必填 | 说明 |
|-----------|--------|------|------|------|
| `field001` | 标题 | 2 | ★ | 工单标题 |
| `field004` | 负责人 | 8 | ★ | 默认 `VgmUb3N1`（吴名先） |
| `field013` | 截止日期 | 5 | ★ | 需同时传 value（unix ts）和 date_value（YYYY-MM-DD） |
| `field016` | 描述 | 20 | ★ | HTML 格式，见描述模板 |
| `2KzQcUwN` | 缺陷优先级 | 1 | 建议填 | P0/P1/P2，见选项表 |
| `field011` | 所属迭代 | sprint | — | 传 null |

### 缺陷优先级选项（`2KzQcUwN`）

| 优先级 | option_uuid | 判断标准 | 截止日期（从今日起） |
|--------|-------------|---------|-----------------|
| **P0** | `FFbZ7ebB` | 影响产线用户使用，阻碍流程，或看板数据误导 | +0天（当天） |
| **P1** | `9R94zH1j` | 不影响核心流程，有临时方案，但有额外操作负担或视觉影响 | +3天 |
| **P2** | `ACKSasRN` | 不影响流程，仅交互/视觉问题，需教育用户 | +10天 |

### 缺陷描述模板（`field016`，HTML）

```html
<p><span style="color:#000000; font-size:medium">【故障平台】</span><em><span style="color:#c0c0c0"><span style="font-size:medium">{平台域名/机构名称}</span></span></em></p>
<p><span style="color:#000000; font-size:medium">【故障账号】</span><em><span style="color:#c0c0c0"><span style="font-size:medium">{账号名称}</span></span></em><br />
<span style="color:#000000; font-size:medium">【操作步骤】</span>{内容}<br />
<span style="color:#000000; font-size:medium">【相关链接】</span><em><span style="color:#c0c0c0"><span style="font-size:medium">{如有}</span></span></em><br />
<span style="color:#000000; font-size:medium">【当前结果】</span>{内容}<br />
<span style="color:#000000; font-size:medium">【期望结果】</span>{内容}<br />
<span style="color:#000000; font-size:medium">【截图/录屏】</span><em><span style="color:#c0c0c0"><span style="font-size:medium">请插入图片/上传录屏（如有）</span></span></em></p>
```

### 缺陷 field_values 完整结构

```python
# 截止日期按优先级计算
days_map = {"P0": 0, "P1": 3, "P2": 10}
deadline_dt  = datetime.now(timezone.utc) + timedelta(days=days_map[priority])
deadline_ts  = int(deadline_dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
deadline_str = deadline_dt.strftime("%Y-%m-%d")

priority_uuid = {"P0": "FFbZ7ebB", "P1": "9R94zH1j", "P2": "ACKSasRN"}[priority]

field_values = [
    {"field_uuid": "field001", "type": 2,  "value": summary},
    {"field_uuid": "field004", "type": 8,  "value": "VgmUb3N1"},       # 默认负责人：吴名先
    {"field_uuid": "field013", "type": 5,  "value": deadline_ts, "date_value": deadline_str},  # ★必填
    {"field_uuid": "2KzQcUwN", "type": 1,  "value": priority_uuid},    # 缺陷优先级
    {"field_uuid": "field016", "type": 20, "value": description_html}, # ★必填
    {"field_uuid": "field011", "type": 7,  "value": None},
]
```

---

## 任务字段（VBtGTYP2）

| field_uuid | 字段名 | type | 必填 | 说明 |
|-----------|--------|------|------|------|
| `field001` | 标题 | 2 | ★ | 工单标题 |
| `field004` | 负责人 | 8 | ★ | 传 user uuid |
| `field011` | 所属迭代 | 7 | ★ | 传 sprint uuid（见下方查询方式） |
| `RKaS6grg` | 任务类别 | 1 | ★ | 见选项表 |
| `field018` | 预估工时 | 4 | 建议填 | 数字，单位：小时 |
| `field013` | 截止日期 | 5 | — | 同缺陷，传 value（unix ts）+ date_value |
| `WiDjpKBA` | 任务难度 | 1 | — | 见选项表 |
| `field012` | 优先级 | 1 | — | 默认 `NroP1UGJ`（Major） |
| `field016` | 描述 | 20 | — | HTML 格式 |

### 任务类别选项（`RKaS6grg`）

| 类别 | option_uuid |
|------|-------------|
| 技术设计 | `XV7CdUh9` |
| API | `KrtxjEQ7` |
| 页面 | `BfmF8rLZ` |
| 文档编写 | `Cx5RucXy` |
| 手工测试 | `8shjQJBY` |
| 自动化测试 | `QmcMVVaY` |

### 任务难度选项（`WiDjpKBA`）

| 难度 | option_uuid |
|------|-------------|
| 低 | `JP1wMp29` |
| 中 | `7pyW2weo` |
| 高 | `GBo1BVNh` |

### 查询当前项目迭代（Sprint）

```python
payload = {
    "query": "{ sprints(filter: {project_in: [\"Gq9erDiKJ1trVL1V\"], status_in: [\"to_do\", \"in_progress\"]}) { uuid name startTime endTime status } }",
    "variables": {}
}
# POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/items/graphql?t=sprints
# 返回 sprints[].uuid / sprints[].name
```

### 任务 field_values 完整结构

```python
from datetime import datetime, timezone, timedelta

field_values = [
    {"field_uuid": "field001", "type": 2,  "value": summary},
    {"field_uuid": "field004", "type": 8,  "value": assignee_uuid},
    {"field_uuid": "field011", "type": 7,  "value": sprint_uuid},       # ★所属迭代
    {"field_uuid": "RKaS6grg", "type": 1,  "value": category_uuid},    # ★任务类别
    {"field_uuid": "field018", "type": 4,  "value": estimated_hours},   # 预估工时（小时）
    {"field_uuid": "field012", "type": 1,  "value": "NroP1UGJ"},       # 优先级默认 Major
    {"field_uuid": "field016", "type": 20, "value": description_html},
]
```

---

## 成员 UUID

| 姓名 | uuid | 说明 |
|------|------|------|
| 朱浩 | `Sn3hdCc9` | 当前用户（ones-uid），需求默认负责人 |
| 吴名先 | `VgmUb3N1` | 缺陷默认负责人（layout 系统默认值） |

## Task UUID 生成规则

```python
import random, string
task_uuid = ones_uid + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
```

---

## 图片上传流程（三步）

工单描述中嵌入图片需依次调用三个接口。

### Step 1：注册附件 → 获取 token + resource_uuid

```python
payload = {
    "type": "attachment", "name": "文件名.jpg",
    "ref_id": task_uuid, "ref_type": "task",
    "description": "", "source": "edit",
    "image_width": w, "image_height": h, "ctype": "image/jpeg"
}
# POST /res/attachments/upload
# 返回：token, resource_uuid
```

图片尺寸获取（macOS）：
```bash
sips -g pixelWidth -g pixelHeight {path}
```

### Step 2：上传文件

```bash
curl -F "token={token}" -F "file=@{path};type=image/jpeg" \
  https://works.yxt.com/api/project/files/upload
```

### Step 3：更新描述嵌入图片

用 `resource_uuid` 构造 img 标签，更新 `desc_rich` + `descriptionText` 字段：

```python
img_html = (
    f'<figure class="ones-image-figure" data-size="medium">'
    f'<div class="image-wrapper">'
    f'<img data-mime="image/jpeg" data-orientation="1" '
    f'data-ref-id="{task_uuid}" data-ref-type="task" '
    f'data-size="medium" data-uuid="{resource_uuid}" '
    f'src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" />'
    f'</div><figcaption></figcaption></figure>'
)
# 通过 tasks/update3 更新 desc_rich 和 descriptionText
```
