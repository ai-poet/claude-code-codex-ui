# Claude Code UI

Use Claude Code to perform multiple tasks in parallel with a Claude Code-style UI.

A code agent task management system that provides parallel execution of Claude Code automation tasks. Users can run multiple Claude Code agents simultaneously through a web interface focused on Claude Code integration.

![async-code-ui](https://github.com/user-attachments/assets/e490c605-681a-4abb-a440-323e15f1a90d)


![async-code-review](https://github.com/user-attachments/assets/bbf71c82-636c-487b-bb51-6ad0b393c2ef)


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

