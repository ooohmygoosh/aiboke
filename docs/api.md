# API 与推荐逻辑说明

## 一、核心业务流程

1. 用户首次选择标签，调用 `POST /api/v1/users/init-tags` 初始化标签池。
2. 用户请求生成音乐，调用 `POST /api/v1/tracks/generate`。
3. 用户对音乐行为反馈：
   - 收藏：`POST /api/v1/tracks/{track_id}/favorite`
   - 跳过：`POST /api/v1/tracks/{track_id}/skip`
4. 后端根据行为更新标签权重，下一次生成更贴近用户偏好。

## 二、标签权重规则（默认）

- 初始化：每个已选标签 `weight = 1.0`
- 收藏：`+0.8`
- 跳过：`-0.6`
- 播放完成（预留）：`+0.1`
- 权重范围：`[-5, 10]`

实现位置：`backend/app/tag_engine.py`。

## 三、天谱乐 API 接入

后端在生成接口中会调用 `_submit_tianpule_task`：

- 环境变量：
  - `TIANPULE_API_BASE`
  - `TIANPULE_API_KEY`
- 请求地址（示例）：`{TIANPULE_API_BASE}/v1/music/generate`
- 请求体（示例）：

```json
{
  "task_id": "uuid",
  "tags": ["治愈", "电子", "钢琴"],
  "duration": 30
}
```

> 如果未配置天谱乐环境变量，MVP 模式下会跳过真实 API 请求，方便本地联调。

## 四、下一步建议

- 将 `user_profiles` 从内存改为 PostgreSQL 持久化。
- 增加 `generation_tasks` 表并接入异步任务队列（Celery + Redis）。
- 增加管理员权限（RBAC）和任务监控页面。
