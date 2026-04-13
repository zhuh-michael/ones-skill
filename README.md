# ones-skill — ONES 工单系统 Claude Code Skill

在 Claude Code 中直接管理 ONES 工单系统。

## 安装

```bash
claude plugin add git@github.com:zhuh-michael/ones-skill.git
```

## 首次登录

安装完成后，在 Claude Code 中执行：

```
/ones-init
```

按提示完成钉钉扫码登录，Token 自动保存。

## 使用

触发词：**建工单**

```
建工单 客户反馈登录页面白屏，Safari 必现
建工单 希望报表页面支持导出 Excel
```

## 能力

| 能力 | 状态 |
|------|------|
| 创建需求 / 缺陷 / 任务 | ✅ |
| 查询工单列表 / 详情 | ✅ |
| 状态流转 | ✅ |
| 添加评论 | ✅ |
| 附件 / 截图上传 | ✅ |
| 迭代查询 / 创建 | ✅ |
| Token 一键刷新 | ✅ |

## 更新

```bash
claude plugin update ones-skill
```
