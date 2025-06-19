# Claude Code UI

**Languages:** [English](#english) | [中文](#中文)

---

## English

Use Claude Code to perform multiple tasks in parallel with a modern UI.

A code agent task management system that provides parallel execution of Claude Code automation tasks. Users can run multiple Claude Code agents simultaneously through a web interface focused on Claude Code integration.

> This project is based on [@ObservedObserver/async-code](https://github.com/ObservedObserver/async-code), modified and optimized for Claude Code integration.

![code-review](https://github.com/user-attachments/assets/bbf71c82-636c-487b-bb51-6ad0b393c2ef)


## Key Features

- 🤖 **Claude Code Integration**: Run Claude Code automation tasks in parallel
- 🔄 **Parallel Task Management**: Execute multiple coding tasks simultaneously  
- 🌐 **Clean Web UI**: Modern interface for managing Claude Code tasks
- 🐳 **Containerized Execution**: Secure sandboxed environment for each task
- 🔗 **Git Integration**: Automatic repository cloning, commits, and PR creation
- **Selfhost**: Deploy your own parallel code agent platform.

## Architecture

- **Frontend**: Next.js with TypeScript and TailwindCSS
- **Backend**: Python Flask API with Docker orchestration
- **Agent**: Claude Code (Anthropic)
- **Task Management**: Parallel execution system based on container

## Quick Start

1. **Setup**
   ```bash
   git clone <this-repo>
   cd async-code
   ./build.sh
   ```

2. **Configure Environment**
   - Add your Anthropic API key to `server/.env`
   - Copy `async-code-web/.env.example` to `async-code-web/.env.local` and configure frontend variables
   - Get a GitHub Personal Access Token with repo permissions
   - **Setup Supabase database** (required - see Database Setup section)

3. **Run**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Database Setup (Required)

The application requires a Supabase database for data storage and full functionality:

1. **Create a Supabase project** at https://supabase.com
2. **Initialize the database** by running the SQL script in your Supabase dashboard:
   ```sql
   -- Copy and run the contents of db/init_supabase.sql in Supabase SQL Editor
   ```
3. **Configure backend environment variables** in `server/.env`:
   ```bash
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```
4. **Configure frontend environment variables** in `async-code-web/.env.local`:
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

See `db/README.md` for detailed database setup instructions.

## Usage

1. **Setup GitHub Token**: Enter your GitHub token in the web interface
2. **Configure Repository**: Specify target repository and branch
3. **Submit Tasks**: Start multiple Claude Code tasks in parallel
4. **Review Results**: Review outputs from Claude Code automation
5. **Create PRs**: Generate pull requests from successful tasks

## Environment Variables

### Backend (server/.env)
```bash
# Required: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Flask Configuration
FLASK_ENV=production

# Required: Supabase Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

### Frontend (async-code-web/.env.local)
```bash
# Required: Supabase Configuration for frontend
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```


## Development

```bash
# Run all services
docker-compose up

# Development mode
cd async-code-web && npm run dev  # Frontend
cd server && python main.py      # Backend
```

## Production Deployment

### Nginx Configuration

For production deployment, use nginx as a reverse proxy to serve the application:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (Next.js)
    location / {
        proxy_pass http://ip:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://ip:5000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle CORS for API requests
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }

    # WebSocket support for real-time updates
    location /ws {
        proxy_pass http://ip:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase max body size for file uploads
    client_max_body_size 50M;
    
    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
}

# SSL Configuration (recommended)
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/your/certificate.pem;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Same location blocks as above
    # ... (copy all location blocks from HTTP configuration)
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Production Setup Steps

1. **Build for production**:
   ```bash
   ./build.sh
   ```

2. **Install and configure nginx**:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install nginx
   
   # Copy configuration
   sudo cp nginx.conf /etc/nginx/sites-available/claude-code-ui
   sudo ln -s /etc/nginx/sites-available/claude-code-ui /etc/nginx/sites-enabled/
   
   # Test and reload
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **SSL Certificate (recommended)**:
   ```bash
   # Using Let's Encrypt with Certbot
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

4. **Start services**:
   ```bash
   # Ensure services are running on the correct ports
   # Frontend: ip:3000
   # Backend: ip:5000
   ```

---

## 中文

使用现代 UI 通过 Claude Code 并行执行多个任务。

这是一个代码代理任务管理系统，提供 Claude Code 自动化任务的并行执行。用户可以通过专注于 Claude Code 集成的 Web 界面同时运行多个 Claude Code 代理。

> 本项目基于 [@ObservedObserver/async-code](https://github.com/ObservedObserver/async-code)，针对 Claude Code 集成进行了修改和优化。

![code-review](https://github.com/user-attachments/assets/bbf71c82-636c-487b-bb51-6ad0b393c2ef)

### 核心功能

- 🤖 **Claude Code 集成**：并行运行 Claude Code 自动化任务
- 🔄 **并行任务管理**：同时执行多个编码任务
- 🌐 **简洁的 Web UI**：用于管理 Claude Code 任务的现代界面
- 🐳 **容器化执行**：为每个任务提供安全的沙盒环境
- 🔗 **Git 集成**：自动仓库克隆、提交和 PR 创建
- **自托管**：部署您自己的并行代码代理平台

### 架构

- **前端**：Next.js + TypeScript + TailwindCSS
- **后端**：Python Flask API + Docker 编排
- **代理**：Claude Code (Anthropic)
- **任务管理**：基于容器的并行执行系统

### 快速开始

1. **安装**
   ```bash
   git clone <this-repo>
   cd async-code
   ./build.sh
   ```

2. **配置环境**
   - 将您的 Anthropic API 密钥添加到 `server/.env`
   - 复制 `async-code-web/.env.example` 到 `async-code-web/.env.local` 并配置前端变量
   - 获取具有仓库权限的 GitHub 个人访问令牌
   - **设置 Supabase 数据库**（必需 - 请参阅数据库设置部分）

3. **运行**
   - 前端：http://localhost:3000
   - 后端 API：http://localhost:5000

### 数据库设置（必需）

应用程序需要 Supabase 数据库来存储数据并实现完整功能：

1. **在 https://supabase.com 创建 Supabase 项目**
2. **通过在 Supabase 控制台中运行 SQL 脚本来初始化数据库**：
   ```sql
   -- 在 Supabase SQL 编辑器中复制并运行 db/init_supabase.sql 文件的内容
   ```
3. **在 `server/.env` 中配置后端环境变量**：
   ```bash
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```
4. **在 `async-code-web/.env.local` 中配置前端环境变量**：
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

详细的数据库设置说明请参见 `db/README.md`。

### 使用方法

1. **设置 GitHub 令牌**：在 Web 界面中输入您的 GitHub 令牌
2. **配置仓库**：指定目标仓库和分支
3. **提交任务**：并行启动多个 Claude Code 任务
4. **查看结果**：查看 Claude Code 自动化的输出
5. **创建 PR**：从成功的任务生成拉取请求

### 环境变量

#### 后端 (server/.env)
```bash
# 必需：Anthropic API 密钥
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Flask 配置
FLASK_ENV=production

# 必需：Supabase 数据库配置
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

#### 前端 (async-code-web/.env.local)
```bash
# 必需：前端 Supabase 配置
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 开发

```bash
# 运行所有服务
docker-compose up

# 开发模式
cd async-code-web && npm run dev  # 前端
cd server && python main.py      # 后端
```

### 生产部署

#### Nginx 配置

生产部署时，使用 nginx 作为反向代理服务应用程序：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端 (Next.js)
    location / {
        proxy_pass http://ip:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://ip:5000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 处理 API 请求的 CORS
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        
        # 处理预检请求
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }

    # WebSocket 支持实时更新
    location /ws {
        proxy_pass http://ip:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 增加文件上传的最大文件大小
    client_max_body_size 50M;
    
    # 启用 gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
}
```

#### 生产环境设置步骤

1. **构建生产版本**：
   ```bash
   ./build.sh
   ```

2. **安装和配置 nginx**：
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install nginx
   
   # 复制配置
   sudo cp nginx.conf /etc/nginx/sites-available/claude-code-ui
   sudo ln -s /etc/nginx/sites-available/claude-code-ui /etc/nginx/sites-enabled/
   
   # 测试并重新加载
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **SSL 证书（推荐）**：
   ```bash
   # 使用 Let's Encrypt 和 Certbot
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

4. **Start services**:
   ```bash
   # Ensure services are running on the correct ports
   # Frontend: ip:3000
   # Backend: ip:5000
   ```

详见 LICENSE 文件。

---

## Production Deployment

### Nginx Configuration