# 工单查询 API

## 0. 更新工单字段 / 状态流转

### 字段更新（标题、描述、截止日期、负责人等）

```
PUT https://works.yxt.com/project/api/project/team/Q5w8GzTz/tasks/{task_uuid}
Content-Type: application/json;charset=UTF-8
```

传需要修改的字段即可，结构与创建时相同（`field_values` 数组）。

### 状态流转（两步）

**Step 1：查可用流转**
```
GET https://works.yxt.com/project/api/project/team/Q5w8GzTz/task/{task_uuid}/transitions
```
返回 `transitions[]`，每条含 `uuid`（流转ID）、`name`（流转名称）、`end_status_uuid`。

**Step 2：执行流转**
```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/task/{task_uuid}/transit
Content-Type: application/json;charset=UTF-8

{"transition_uuid": "xxx"}
```

```python
# Python 调用示例
payload = {"transition_uuid": transition_uuid}
subprocess.run(["curl","-s",
    f"https://works.yxt.com/project/api/project/team/Q5w8GzTz/task/{task_uuid}/transit",
    "-H","content-type: application/json;charset=UTF-8",
    "-H",f"x-csrf-token: {csrf}",
    "-b",f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
    "--data-raw", json.dumps(payload)], capture_output=True, text=True)
```

---

## 1. 按 UUID 查询工单详情

```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/tasks/info
Content-Type: application/json;charset=UTF-8

{"ids": ["uuid1", "uuid2"]}
```

## 2. 查询工单列表（GraphQL）

```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/items/graphql?t=group-task-data
Content-Type: application/json;charset=UTF-8
```

**请求体结构：**

```json
{
  "query": "{ buckets (...) { tasks (...) { uuid name number status { uuid name category } deadline issueType { uuid } } pageInfo { totalCount hasNextPage } } }",
  "variables": {
    "orderBy": {"position": "ASC", "createTime": "ASC"},
    "filterGroup": [<filter>],
    "pagination": {"limit": 50, "preciseCount": false}
  }
}
```

### 常用 filter 组合

| 场景 | filterGroup |
|------|-------------|
| 我的缺陷 | `[{"project_in":["Gq9erDiKJ1trVL1V"],"issueType_in":["H1pqkZQF"],"owner_in":["$currentUser"]}]` |
| 我的需求 | `[{"project_in":["Gq9erDiKJ1trVL1V"],"issueType_in":["CyqmgJVm"],"owner_in":["$currentUser"]}]` |
| 全部工单 | `[{"project_in":["Gq9erDiKJ1trVL1V"],"issueType_in":["CyqmgJVm","H1pqkZQF"]}]` |
| **未关闭缺陷**（精确定义） | `[{"project_in":["Gq9erDiKJ1trVL1V"],"issueType_in":["H1pqkZQF"],"status_notIn":["UXQxFHse","CFbsohNY","DFF3639N","1VFWcEV1","KtFfwnsV","TeH9xcmt"]}]` |

### "未关闭"状态定义

**不要**用 `statusCategory_in: ["to_do","in_progress"]`，应使用 `status_notIn` 排除以下已关闭状态：

| status_uuid | 状态名称 | 备注 |
|-------------|---------|------|
| `UXQxFHse` | 已关闭 | |
| `CFbsohNY` | 非缺陷关闭 | |
| `DFF3639N` | 无法复现 | |
| `1VFWcEV1` | 问题重复 | 视为关闭 |
| `KtFfwnsV` | 暂缓处理 | 视为关闭 |
| `TeH9xcmt` | 非缺陷 | |

```python
CLOSED_STATUS_UUIDS = ["UXQxFHse", "CFbsohNY", "DFF3639N", "1VFWcEV1", "KtFfwnsV", "TeH9xcmt"]
# 用法：
"filterGroup": [{"project_in": ["Gq9erDiKJ1trVL1V"], "issueType_in": ["H1pqkZQF"], "status_notIn": CLOSED_STATUS_UUIDS}]
```

**说明：**
- `$currentUser`：ONES 内置变量，自动替换为当前登录用户
- `issueType_in`：需求 `CyqmgJVm`，缺陷 `H1pqkZQF`，可传数组同时查两种

### 返回字段说明

| 字段 | 说明 |
|------|------|
| `uuid` | 工单 UUID |
| `name` | 标题 |
| `number` | 工单编号（#xxx） |
| `status.name` | 状态名称（中文） |
| `status.category` | 状态分类：`to_do` / `in_progress` / `done` |
| `deadline` | 截止日期（ONESDATE 格式） |
| `issueType.uuid` | 类型 UUID |

## Python 调用模板

```python
import subprocess, json, os

ones_uid = os.environ["ONES_UID"]
ones_lt  = os.environ["ONES_LT"]
csrf     = os.environ["ONES_CSRF_TOKEN"]

GRAPHQL_QUERY = """
{
    buckets (
      groupBy: $groupBy
      orderBy: $groupOrderBy
      pagination: $pagination
      filter: $groupFilter
    ) {
      key
      tasks (
        filterGroup: $filterGroup
        orderBy: $orderBy
        limit: 10000
      ) {
        uuid name number
        status { uuid name category }
        deadline(unit: ONESDATE)
        issueType { uuid }
      }
      pageInfo { count totalCount hasNextPage }
    }
    __extensions
}
"""

payload = {
    "query": GRAPHQL_QUERY,
    "variables": {
        "groupBy": {"tasks": {}},
        "groupOrderBy": None,
        "orderBy": {"position": "ASC", "createTime": "ASC"},
        "filterGroup": [
            {
                "project_in": ["Gq9erDiKJ1trVL1V"],
                "issueType_in": ["CyqmgJVm", "H1pqkZQF"],
                "owner_in": ["$currentUser"]
            }
        ],
        "pagination": {"limit": 50, "preciseCount": False}
    }
}

result = subprocess.run([
    "curl", "-s",
    "https://works.yxt.com/project/api/project/team/Q5w8GzTz/items/graphql?t=group-task-data",
    "-H", "accept: application/json, text/plain, */*",
    "-H", "content-type: application/json;charset=UTF-8",
    "-H", f"x-csrf-token: {csrf}",
    "-b", f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
    "--data-raw", json.dumps(payload)
], capture_output=True, text=True)

data   = json.loads(result.stdout)
tasks  = data["data"]["buckets"][0]["tasks"]
total  = data["data"]["buckets"][0]["pageInfo"]["totalCount"]
```

## 3. 人员搜索

用于查找用户 UUID（指定负责人、关注者时使用）。

```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/users/search
Content-Type: application/json
```

**请求体：**
```json
{
  "keyword": "姓名关键词",
  "status": [1],
  "team_member_status": [1],
  "need_user_list_filter": true,
  "project_uuid": "Gq9erDiKJ1trVL1V",
  "permission_list": [{
    "context_type": "issue_type",
    "context_param": {
      "project_uuid": "Gq9erDiKJ1trVL1V",
      "issue_type_uuid": "H1pqkZQF"
    },
    "permission": "be_assigned"
  }],
  "types": [1, 10]
}
```

`issue_type_uuid` 按场景传：需求 `CyqmgJVm`，缺陷 `H1pqkZQF`。

**Python 调用：**
```python
payload = {
    "keyword": name_keyword,
    "status": [1],
    "team_member_status": [1],
    "need_user_list_filter": True,
    "project_uuid": "Gq9erDiKJ1trVL1V",
    "permission_list": [{"context_type": "issue_type", "context_param": {"project_uuid": "Gq9erDiKJ1trVL1V", "issue_type_uuid": issue_type_uuid}, "permission": "be_assigned"}],
    "types": [1, 10]
}
# 返回 users[].uuid / users[].name
```

## 工单链接格式

```
https://works.yxt.com/project/#/team/Q5w8GzTz/task/{uuid}
```

## 4. 创建迭代

> ⚠️ 需要 **ManageSprints** 权限（项目管理员），普通成员无法调用。

```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/project/Gq9erDiKJ1trVL1V/sprints/add
Content-Type: application/json;charset=UTF-8
```

```json
{
  "sprints": [{
    "title": "迭代名称",
    "assign": "{owner_uuid}",
    "start_date": "2026-04-14",
    "end_date": "2026-04-30",
    "period": "custom",
    "fields": [],
    "statuses": []
  }]
}
```

注意：日期用 `YYYY-MM-DD` 字符串，不是时间戳。

---

## 5. 添加评论

```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/task/{task_uuid}/send_message
Content-Type: application/json
```

```json
{
  "uuid": "随机8位字符串",
  "content_type": 1,
  "text": "<p>评论内容（支持 HTML）</p>"
}
```

```python
import random, string
msg_uuid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
payload  = {"uuid": msg_uuid, "content_type": 1, "text": "<p>评论内容</p>"}
# POST 到上方地址，返回 {"code":200,"errcode":"OK"}
```

---

## 5. 附件上传（截图）

三步流程：注册 → 上传文件 → （可选）验证。

### Step 1：注册附件，获取 token

```
POST https://works.yxt.com/project/api/project/team/Q5w8GzTz/res/attachments/upload
Content-Type: application/json;charset=UTF-8
```

```json
{
  "type": "attachment",
  "name": "filename.png",
  "ref_id": "{task_uuid}",
  "ref_type": "task",
  "description": "",
  "image_width": 1685,
  "image_height": 465,
  "ctype": "image/png"
}
```

返回：`token`、`upload_url`、`resource_uuid`

### Step 2：上传文件

```
POST https://works.yxt.com/api/project/files/upload
Content-Type: multipart/form-data
```

字段：`token`（Step 1 返回）、`file`（文件二进制）

### Python 调用模板

```python
import subprocess, json, os, struct

def upload_attachment(image_path, task_uuid, ones_uid, ones_lt, csrf):
    filename = os.path.basename(image_path)
    # 获取 PNG 尺寸
    with open(image_path, "rb") as f:
        f.seek(16)
        w = struct.unpack(">I", f.read(4))[0]
        h = struct.unpack(">I", f.read(4))[0]

    # Step 1: 注册
    reg = {"type":"attachment","name":filename,"ref_id":task_uuid,"ref_type":"task",
           "description":"","image_width":w,"image_height":h,"ctype":"image/png"}
    r1 = subprocess.run(["curl","-s",
        "https://works.yxt.com/project/api/project/team/Q5w8GzTz/res/attachments/upload",
        "-H","content-type: application/json;charset=UTF-8",
        "-H",f"x-csrf-token: {csrf}",
        "-b",f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
        "--data-raw", json.dumps(reg)], capture_output=True, text=True)
    d1 = json.loads(r1.stdout)
    token, upload_url = d1["token"], d1["upload_url"]

    # Step 2: 上传
    r2 = subprocess.run(["curl","-s",upload_url,
        "-H",f"x-csrf-token: {csrf}",
        "-b",f"ones-uid={ones_uid}; ones-lt={ones_lt}; ct={csrf}; language=zh; timezone=Asia/Shanghai",
        "-F",f"token={token}",
        "-F",f"file=@{image_path};type=image/png"], capture_output=True, text=True)
    return json.loads(r2.stdout)  # 返回 hash、url、name、size
```

### Step 3（可选）：验证附件

```
GET https://works.yxt.com/project/api/project/team/Q5w8GzTz/task/{task_uuid}/attachments?since=0
```

返回 `attachments[]`，含 uuid、name、image_width、image_height。
