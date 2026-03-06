# 详细部署教程（Docker Compose）

## 1. 服务器准备

- 系统：Ubuntu 22.04+
- 建议配置：2C4G（测试）/4C8G（生产起步）
- 域名（生产）：
  - `api.example.com`
  - `admin.example.com`
  - `app.example.com`

## 2. Docker 最简安装（推荐）

你说得对，下面这套是最省事的。

### 2.1 一键安装（3 条命令）

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

然后**重新登录终端**（或执行 `newgrp docker`），再验证：

```bash
docker --version
docker compose version
docker run --rm hello-world
```

> 如果你只想“快点跑起来”，到这里就够了。

### 2.2 如果仍报错，按这个顺序排查

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker --no-pager
docker ps
```

常见报错：

- `docker: command not found`：通常是安装失败或 shell 未重载，重新执行 2.1 并重新登录。
- `permission denied while trying to connect to the Docker daemon socket`：说明用户组未生效，执行 `newgrp docker` 或重新登录。
- `Cannot connect to the Docker daemon`：Docker 服务未启动，执行 `sudo systemctl start docker`。

### 2.3 手动安装（仅在一键安装失败时使用）

如果你的网络/镜像源限制导致一键脚本失败，再使用手动安装：

```bash
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
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
