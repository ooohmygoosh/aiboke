# 详细部署教程（Docker Compose）

## 1. 服务器准备

- 系统：Ubuntu 22.04+
- 建议配置：2C4G（测试）/4C8G（生产起步）
- 域名（生产）：
  - `api.example.com`
  - `admin.example.com`
  - `app.example.com`

## 2. 安装 Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## 3. 拉取项目并配置变量

```bash
git clone <your-repo-url> ai-music-app
cd ai-music-app
cp .env.example .env
```

编辑 `.env`，至少填好：

- `TIANPULE_API_BASE`
- `TIANPULE_API_KEY`

## 4. 启动服务

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

## 5. 验证服务

```bash
curl http://127.0.0.1/healthz
curl -X POST http://127.0.0.1/api/v1/users/init-tags \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","tags":["治愈","电子"]}'
curl -X POST http://127.0.0.1/api/v1/tracks/generate \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u1","duration":30}'
```

## 6. 配置 HTTPS（生产）

建议把 `deploy/nginx.conf` 按域名拆分为多个 server，并结合 Certbot 签发证书。

示例命令：

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com -d admin.example.com -d app.example.com
```

## 7. 生产化建议

- 加入 PostgreSQL、Redis、Celery。
- 增加日志采集与告警（Sentry / Prometheus + Grafana）。
- 增加数据库自动备份与恢复演练。
