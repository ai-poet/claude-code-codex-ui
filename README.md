--- README.md
+++ README.md
# Claude Code UI

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


## License

See LICENSE file for details.

---
# Claude Code UI

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
        proxy_pass http://localhost:3000;
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
        proxy_pass http://localhost:5000/;
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
        proxy_pass http://localhost:5000;
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
   # Build frontend
   cd async-code-web && npm run build
   
   # Start production services
   docker-compose -f docker-compose.prod.yml up -d
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
   # Frontend: localhost:3000
   # Backend: localhost:5000
   ```

## License

See LICENSE file for details.