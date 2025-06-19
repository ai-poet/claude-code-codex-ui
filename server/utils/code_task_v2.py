import json
import os
import logging
import docker
import docker.types
import uuid
import time
import random
from datetime import datetime
from database import DatabaseOperations
import fcntl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Docker client
docker_client = docker.from_env()

def cleanup_orphaned_containers():
    """Clean up orphaned AI code task containers aggressively"""
    try:
        # Get all containers with our naming pattern
        containers = docker_client.containers.list(all=True, filters={'name': 'ai-code-task-'})
        orphaned_count = 0
        current_time = time.time()
        
        for container in containers:
            try:
                # Get container creation time
                created_at = container.attrs['Created']
                # Parse ISO format timestamp and convert to epoch time
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                age_hours = (current_time - created_time) / 3600
                
                # Remove containers that are:
                # 1. Not running (exited, dead, created)
                # 2. OR older than 2 hours (stuck containers)
                # 3. OR in error state
                should_remove = (
                    container.status in ['exited', 'dead', 'created'] or
                    age_hours > 2 or
                    container.status == 'restarting'
                )
                
                if should_remove:
                    logger.info(f"🧹 Removing orphaned container {container.id[:12]} (status: {container.status}, age: {age_hours:.1f}h)")
                    container.remove(force=True)
                    orphaned_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to cleanup container {container.id[:12]}: {e}")
                # If we can't inspect it, try to force remove it anyway
                try:
                    container.remove(force=True)
                    orphaned_count += 1
                    logger.info(f"🧹 Force removed problematic container: {container.id[:12]}")
                except Exception as force_error:
                    logger.warning(f"⚠️  Could not force remove container {container.id[:12]}: {force_error}")
        
        if orphaned_count > 0:
            logger.info(f"🧹 Cleaned up {orphaned_count} orphaned containers")
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to cleanup orphaned containers: {e}")

def run_ai_code_task_v2(task_id: int, user_id: str, github_token: str):
    """Run Claude Code automation in a container - Supabase version"""
    try:
        # Get task from database to check the model type
        task = DatabaseOperations.get_task_by_id(task_id, user_id)
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return
        
        model_cli = task.get('agent', 'claude')
        
        # Only Claude is supported
        if model_cli != 'claude':
            logger.error(f"Unsupported model: {model_cli}. Only Claude is supported.")
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'failed',
                'error': f'Unsupported model: {model_cli}. Only Claude is supported.'
            })
            return
        
        logger.info(f"🚀 Running Claude Code task {task_id}")
        return _run_ai_code_task_v2_internal(task_id, user_id, github_token)
            
    except Exception as e:
        logger.error(f"💥 Exception in run_ai_code_task_v2: {str(e)}")
        try:
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'failed',
                'error': str(e)
            })
        except:
            logger.error(f"Failed to update task {task_id} status after exception")

def _run_ai_code_task_v2_internal(task_id: int, user_id: str, github_token: str):
    """Internal implementation of Claude Code automation"""
    try:
        # Clean up any orphaned containers before starting new task
        cleanup_orphaned_containers()
        
        # Get task from database (v2 function)
        task = DatabaseOperations.get_task_by_id(task_id, user_id)
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return
        
        # Update task status to running
        DatabaseOperations.update_task(task_id, user_id, {'status': 'running'})
        
        model_name = task.get('agent', 'claude').upper()
        logger.info(f"🚀 Starting {model_name} Code task {task_id}")
        
        # Get prompt from chat messages
        prompt = ""
        if task.get('chat_messages'):
            for msg in task['chat_messages']:
                if msg.get('role') == 'user':
                    prompt = msg.get('content', '')
                    break
        
        if not prompt:
            error_msg = "No user prompt found in chat messages"
            logger.error(error_msg)
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'failed',
                'error': error_msg
            })
            return
        
        logger.info(f"📋 Task details: prompt='{prompt[:50]}...', repo={task['repo_url']}, branch={task['target_branch']}, model={model_name}")
        logger.info(f"Starting {model_name} task {task_id}")
        
        # Escape special characters in prompt for shell safety
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        # Create container environment variables
        env_vars = {
            'CI': 'true',  # Indicate we're in CI/non-interactive environment
            'TERM': 'dumb',  # Use dumb terminal to avoid interactive features
            'NO_COLOR': '1',  # Disable colors for cleaner output
            'FORCE_COLOR': '0',  # Disable colors for cleaner output
            'NONINTERACTIVE': '1',  # Common flag for non-interactive mode
            'DEBIAN_FRONTEND': 'noninteractive',  # Non-interactive package installs
        }
        
        # Add Claude-specific API keys and environment variables
        model_cli = task.get('agent', 'claude')
        
        # Get user preferences for custom environment variables
        user = DatabaseOperations.get_user_by_id(user_id)
        user_preferences = user.get('preferences', {}) if user else {}
        
        if user_preferences:
            logger.info(f"🔧 Found user preferences for Claude: {list(user_preferences.keys())}")
        
        # Start with default Claude environment
        claude_env = {
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'ANTHROPIC_NONINTERACTIVE': '1'  # Custom flag for Anthropic tools
        }
        # Merge with user's custom Claude environment variables
        claude_config = user_preferences.get('claudeCode', {})
        if claude_config and claude_config.get('env'):
            claude_env.update(claude_config['env'])
        env_vars.update(claude_env)
        print(env_vars)
        # Use Claude Code container image
        container_image = 'claude-code-automation:latest'
        
        
        # Load Claude credentials from user preferences in Supabase
        credentials_content = ""
        escaped_credentials = ""
        logger.info(f"🔍 Looking for Claude credentials in user preferences for task {task_id}")
        
        # Check if user has Claude credentials in their preferences
        claude_config = user_preferences.get('claudeCode', {})
        credentials_json = claude_config.get('credentials') if claude_config else None
        
        # Check if credentials is meaningful (not empty object, null, undefined, or empty string)
        has_meaningful_credentials = (
            credentials_json is not None and 
            credentials_json != {} and 
            credentials_json != "" and
            (isinstance(credentials_json, dict) and len(credentials_json) > 0)
        )
        
        if has_meaningful_credentials:
            try:
                # Convert JSON object to string for writing to container
                credentials_content = json.dumps(credentials_json)
                logger.info(f"📋 Successfully loaded Claude credentials from user preferences and stringified ({len(credentials_content)} characters) for task {task_id}")
                # Escape credentials content for shell
                escaped_credentials = credentials_content.replace("'", "'\"'\"'").replace('\n', '\\n')
                logger.info(f"📋 Credentials content escaped for shell injection")
            except Exception as e:
                logger.error(f"❌ Failed to process Claude credentials from user preferences: {e}")
                credentials_content = ""
                escaped_credentials = ""
        else:
            logger.info(f"ℹ️  No meaningful Claude credentials found in user preferences for task {task_id} - skipping credentials setup (credentials: {credentials_json})")
        
        # 打印 Claude 相关环境变量（只显示 key 是否存在和长度，不打印具体 key）
        safe_env_vars = {k: (v[:5] + '...' if v and len(v) > 8 else v) if 'KEY' in k or 'TOKEN' in k else v for k, v in env_vars.items()}
        logger.info(f"[调试] Claude 相关 env_vars: {safe_env_vars}")
        logger.info(f"[调试] Claude prompt: {prompt}")
        
        # Create the command to run in container (v2 function)
        repo_url = task['repo_url']
        if github_token:
            # 替换 https://github.com/owner/repo.git 为 https://<token>@github.com/owner/repo.git
            repo_url = repo_url.replace('https://github.com/', f'https://{github_token}@github.com/')
        
        container_command = f'''
echo "===== [调试] 容器启动，打印全部环境变量 ====="
env
echo "===== [调试] 当前目录内容 ====="
ls -alh
echo "===== [调试] ANTHROPIC_API_KEY 长度: $(echo -n $ANTHROPIC_API_KEY | wc -c) ====="
echo "===== [调试] ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL ====="
echo "===== [调试] ANTHROPIC_BASE_URL 长度: $(echo -n $ANTHROPIC_BASE_URL | wc -c) ====="
set -e
echo "Setting up repository..."

# Clone repository
git clone -b {task['target_branch']} {repo_url} /workspace/repo
cd /workspace/repo

# Configure git
git config user.email "claude-code@automation.com"
git config user.name "Claude Code Automation"

# We'll extract the patch instead of pushing directly
echo "📋 Will extract changes as patch for later PR creation..."

echo "Starting Claude Code with prompt..."

# Create a temporary file with the prompt using heredoc for proper handling
cat << 'PROMPT_EOF' > /tmp/prompt.txt
{prompt}
PROMPT_EOF

# Setup Claude credentials
echo "Setting up Claude credentials..."

# Create ~/.claude directory if it doesn't exist
mkdir -p ~/.claude

# Write credentials content directly to file
if [ ! -z '{escaped_credentials}' ]; then
    echo "📋 Writing credentials to ~/.claude/.credentials.json"
    cat << 'CREDENTIALS_EOF' > ~/.claude/.credentials.json
{credentials_content}
CREDENTIALS_EOF
    echo "✅ Claude credentials configured"
else
    echo "⚠️  No credentials content available"
fi

echo "Using Claude CLI..."

# Try different ways to invoke claude
echo "Checking claude installation..."

if [ -f /usr/local/bin/claude ]; then
    echo "Found claude at /usr/local/bin/claude"
    echo "File type:"
    file /usr/local/bin/claude || echo "file command not available"
    echo "First few lines:"
    head -5 /usr/local/bin/claude || echo "head command failed"
    
    # Check if it's a shell script
    if head -1 /usr/local/bin/claude | grep -q "#!/bin/sh\|#!/bin/bash\|#!/usr/bin/env bash"; then
        echo "Detected shell script, running with sh..."
        sh /usr/local/bin/claude < /tmp/prompt.txt
    # Check if it's a Node.js script (including env -S node pattern)
    elif head -1 /usr/local/bin/claude | grep -q "#!/usr/bin/env.*node\|#!/usr/bin/node"; then
        echo "Detected Node.js script..."
        if command -v node >/dev/null 2>&1; then
            echo "Running with node..."
            # Try different approaches for Claude CLI
            
            # First try with --help to see available options
            echo "Checking claude options..."
            node /usr/local/bin/claude --help 2>/dev/null || echo "Help not available"
            
            # Try non-interactive approaches
            echo "Attempting non-interactive execution..."
            
            # Method 1: Use the official --print flag for non-interactive mode
            echo "Using --print flag for non-interactive mode..."
            cat /tmp/prompt.txt | node /usr/local/bin/claude --print --allowedTools "Edit,Bash" --debug 2>&1
            CLAUDE_EXIT_CODE=$?
            echo "Claude Code finished with exit code: $CLAUDE_EXIT_CODE"
            
            if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
                echo "ERROR: Claude Code failed with exit code $CLAUDE_EXIT_CODE"
                exit $CLAUDE_EXIT_CODE
            fi
            
            echo "===== [调试] Claude CLI 执行后 ====="
            echo "✅ Claude Code completed successfully"
        else
            echo "Node.js not found, trying direct execution..."
            /usr/local/bin/claude < /tmp/prompt.txt
            CLAUDE_EXIT_CODE=$?
            echo "Claude Code finished with exit code: $CLAUDE_EXIT_CODE"
            if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
                echo "ERROR: Claude Code failed with exit code $CLAUDE_EXIT_CODE"
                exit $CLAUDE_EXIT_CODE
            fi
            echo "✅ Claude Code completed successfully"
        fi
    # Check if it's a Python script
    elif head -1 /usr/local/bin/claude | grep -q "#!/usr/bin/env python\|#!/usr/bin/python"; then
        echo "Detected Python script..."
        if command -v python3 >/dev/null 2>&1; then
            echo "Running with python3..."
            python3 /usr/local/bin/claude < /tmp/prompt.txt
            CLAUDE_EXIT_CODE=$?
        elif command -v python >/dev/null 2>&1; then
            echo "Running with python..."
            python /usr/local/bin/claude < /tmp/prompt.txt
            CLAUDE_EXIT_CODE=$?
        else
            echo "Python not found, trying direct execution..."
            /usr/local/bin/claude < /tmp/prompt.txt
            CLAUDE_EXIT_CODE=$?
        fi
        echo "Claude Code finished with exit code: $CLAUDE_EXIT_CODE"
        if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
            echo "ERROR: Claude Code failed with exit code $CLAUDE_EXIT_CODE"
            exit $CLAUDE_EXIT_CODE
        fi
        echo "✅ Claude Code completed successfully"
    else
        echo "Unknown script type, trying direct execution..."
        /usr/local/bin/claude < /tmp/prompt.txt
        CLAUDE_EXIT_CODE=$?
        echo "Claude Code finished with exit code: $CLAUDE_EXIT_CODE"
        if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
            echo "ERROR: Claude Code failed with exit code $CLAUDE_EXIT_CODE"
            exit $CLAUDE_EXIT_CODE
        fi
        echo "✅ Claude Code completed successfully"
    fi
elif command -v claude >/dev/null 2>&1; then
    echo "Using claude from PATH..."
    CLAUDE_PATH=$(which claude)
    echo "Claude found at: $CLAUDE_PATH"
    claude < /tmp/prompt.txt
    CLAUDE_EXIT_CODE=$?
    echo "Claude Code finished with exit code: $CLAUDE_EXIT_CODE"
    if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Claude Code failed with exit code $CLAUDE_EXIT_CODE"
        exit $CLAUDE_EXIT_CODE
    fi
    echo "✅ Claude Code completed successfully"
else
    echo "ERROR: claude command not found anywhere"
    echo "Checking available interpreters:"
    which python3 2>/dev/null && echo "python3: available" || echo "python3: not found"
    which python 2>/dev/null && echo "python: available" || echo "python: not found"
    which node 2>/dev/null && echo "node: available" || echo "node: not found"
    which sh 2>/dev/null && echo "sh: available" || echo "sh: not found"
    exit 1
fi  # End of Claude CLI setup

# Check if there are changes
if git diff --quiet; then
    echo "ℹ️  No changes made by Claude - this is a valid outcome"
    echo "The AI tool ran successfully but decided not to make changes"
    
    # Create empty patch and diff for consistency
    echo "=== PATCH START ==="
    echo "No changes were made"
    echo "=== PATCH END ==="
    
    echo "=== GIT DIFF START ==="
    echo "No changes were made"
    echo "=== GIT DIFF END ==="
    
    echo "=== CHANGED FILES START ==="
    echo "No files were changed"
    echo "=== CHANGED FILES END ==="
    
    echo "=== FILE CHANGES START ==="
    echo "No file changes to display"
    echo "=== FILE CHANGES END ==="
    
    # Set empty commit hash
    echo "COMMIT_HASH="
else
    # Commit changes locally
    git add .
    git commit -m "Claude: {escaped_prompt[:100]}"

    # Get commit info
    COMMIT_HASH=$(git rev-parse HEAD)
    echo "COMMIT_HASH=$COMMIT_HASH"

    # Generate patch file for later application
    echo "📦 Generating patch file..."
    git format-patch HEAD~1 --stdout > /tmp/changes.patch
    echo "=== PATCH START ==="
    cat /tmp/changes.patch
    echo "=== PATCH END ==="

    # Also get the diff for display
    echo "=== GIT DIFF START ==="
    git diff HEAD~1 HEAD
    echo "=== GIT DIFF END ==="

    # List changed files for reference
    echo "=== CHANGED FILES START ==="
    git diff --name-only HEAD~1 HEAD
    echo "=== CHANGED FILES END ==="

    # Get before/after content for merge view
    echo "=== FILE CHANGES START ==="
    for file in $(git diff --name-only HEAD~1 HEAD); do
        echo "FILE: $file"
        echo "=== BEFORE START ==="
        git show HEAD~1:"$file" 2>/dev/null || echo "FILE_NOT_EXISTS"
        echo "=== BEFORE END ==="
        echo "=== AFTER START ==="
        cat "$file" 2>/dev/null || echo "FILE_DELETED"
        echo "=== AFTER END ==="
        echo "=== FILE END ==="
    done
    echo "=== FILE CHANGES END ==="
fi

# Explicitly exit with success code
echo "Container work completed successfully"
exit 0
'''
        
        # Run container with unified AI Code tools (supports both Claude and Codex)
        logger.info(f"🐳 Creating Docker container for task {task_id} using {container_image} (model: {model_name})")
        
        # Configure Docker security options
        container_kwargs = {
            'image': container_image,
            'command': ['bash', '-c', container_command],
            'environment': env_vars,
            'detach': True,
            'remove': False,  # Don't auto-remove so we can get logs
            'working_dir': '/workspace',
            'network_mode': 'bridge',  # Ensure proper networking
            'tty': False,  # Don't allocate TTY - may prevent clean exit
            'stdin_open': False,  # Don't keep stdin open - may prevent clean exit
            'name': f'claude-code-task-{task_id}-{int(time.time())}-{uuid.uuid4().hex[:8]}',  # Highly unique container name with UUID
            'mem_limit': '2g',  # Limit memory usage to prevent resource conflicts
            'cpu_shares': 1024,  # Standard CPU allocation
            'ulimits': [docker.types.Ulimit(name='nofile', soft=1024, hard=2048)]  # File descriptor limits
        }
        
        
        # Retry container creation with enhanced conflict handling
        container = None
        max_retries = 5  # Increased retries for better reliability
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Container creation attempt {attempt + 1}/{max_retries}")
                container = docker_client.containers.run(**container_kwargs)
                logger.info(f"✅ Container created successfully: {container.id[:12]} (name: {container_kwargs['name']})")
                break
            except docker.errors.APIError as e:
                error_msg = str(e)
                if "Conflict" in error_msg and "already in use" in error_msg:
                    # Handle container name conflicts by generating a new unique name
                    logger.warning(f"🔄 Container name conflict on attempt {attempt + 1}, generating new name...")
                    new_name = f'claude-code-task-{task_id}-{int(time.time())}-{uuid.uuid4().hex[:8]}'
                    container_kwargs['name'] = new_name
                    logger.info(f"🆔 New container name: {new_name}")
                    # Try to clean up any conflicting containers
                    cleanup_orphaned_containers()
                else:
                    logger.warning(f"⚠️  Docker API error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise Exception(f"Failed to create container after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"❌ Unexpected error creating container on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # Update task with container ID (v2 function)
        DatabaseOperations.update_task(task_id, user_id, {'container_id': container.id})
        
        logger.info(f"⏳ Waiting for container to complete (timeout: 300s)...")
        
        # Wait for container to finish - should exit naturally when script completes
        try:
            logger.info(f"🔄 Waiting for container script to complete naturally...")
            
            # Check initial container state
            container.reload()
            logger.info(f"🔍 Container initial state: {container.status}")
            
            # Use standard wait - container should exit when bash script finishes
            logger.info(f"🔄 Calling container.wait() - container should exit when script completes...")
            result = container.wait(timeout=1800)  # 30 minute timeout
            logger.info(f"🎯 Container exited naturally! Exit code: {result['StatusCode']}")
            
            # Verify final container state
            container.reload()
            logger.info(f"🔍 Final container state: {container.status}")
            
            # Get logs before any cleanup operations
            logger.info(f"📜 Retrieving container logs...")
            try:
                logs = container.logs().decode('utf-8')
                logger.info(f"📝 Retrieved {len(logs)} characters of logs")
                logger.info(f"🔍 First 200 chars of logs: {logs[:200]}...")
            except Exception as log_error:
                logger.warning(f"❌ Failed to get container logs: {log_error}")
                logs = f"Failed to retrieve logs: {log_error}"
            
            # Clean up container after getting logs
            try:
                container.reload()  # Refresh container state
                container.remove()
                logger.info(f"🧹 Successfully removed container {container.id[:12]}")
            except docker.errors.NotFound:
                logger.info(f"🧹 Container {container.id[:12]} already removed")
            except Exception as cleanup_error:
                logger.warning(f"⚠️  Failed to remove container {container.id[:12]}: {cleanup_error}")
                # Try force removal as fallback
                try:
                    container.remove(force=True)
                    logger.info(f"🧹 Force removed container {container.id[:12]}")
                except docker.errors.NotFound:
                    logger.info(f"🧹 Container {container.id[:12]} already removed")
                except Exception as force_cleanup_error:
                    logger.error(f"❌ Failed to force remove container {container.id[:12]}: {force_cleanup_error}")
                
        except Exception as e:
            logger.error(f"⏰ Container timeout or error: {str(e)}")
            logger.error(f"🔄 Updating task status to FAILED due to timeout/error...")
            
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'failed',
                'error': f"Container execution timeout or error: {str(e)}"
            })
            
            # Try to get logs even on error
            try:
                logs = container.logs().decode('utf-8')
            except Exception as log_error:
                logs = f"Container failed and logs unavailable: {log_error}"
            
            # Try to clean up container on error
            try:
                container.reload()  # Refresh container state
                container.remove(force=True)
                logger.info(f"Cleaned up failed container {container.id}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to remove failed container {container.id}: {cleanup_error}")
            return
        
        if result['StatusCode'] == 0:
            logger.info(f"✅ Container exited successfully (code 0) - parsing results...")
            # Parse output to extract commit hash, diff, and patch
            lines = logs.split('\n')
            commit_hash = None
            git_diff = []
            git_patch = []
            changed_files = []
            file_changes = []
            capturing_diff = False
            capturing_patch = False
            capturing_files = False
            capturing_file_changes = False
            capturing_before = False
            capturing_after = False
            current_file = None
            current_before = []
            current_after = []
            
            for line in lines:
                if line.startswith('COMMIT_HASH='):
                    commit_hash = line.split('=', 1)[1]
                    logger.info(f"🔑 Found commit hash: {commit_hash}")
                elif line == '=== PATCH START ===':
                    capturing_patch = True
                    logger.info(f"📦 Starting to capture git patch...")
                elif line == '=== PATCH END ===':
                    capturing_patch = False
                    logger.info(f"📦 Finished capturing git patch ({len(git_patch)} lines)")
                elif line == '=== GIT DIFF START ===':
                    capturing_diff = True
                    logger.info(f"📊 Starting to capture git diff...")
                elif line == '=== GIT DIFF END ===':
                    capturing_diff = False
                    logger.info(f"📊 Finished capturing git diff ({len(git_diff)} lines)")
                elif line == '=== CHANGED FILES START ===':
                    capturing_files = True
                    logger.info(f"📁 Starting to capture changed files...")
                elif line == '=== CHANGED FILES END ===':
                    capturing_files = False
                    logger.info(f"📁 Finished capturing changed files ({len(changed_files)} files)")
                elif line == '=== FILE CHANGES START ===':
                    capturing_file_changes = True
                    logger.info(f"🔄 Starting to capture file changes...")
                elif line == '=== FILE CHANGES END ===':
                    capturing_file_changes = False
                    # Add the last file if we were processing one
                    if current_file:
                        file_changes.append({
                            'filename': current_file,
                            'before': '\n'.join(current_before),
                            'after': '\n'.join(current_after)
                        })
                    logger.info(f"🔄 Finished capturing file changes ({len(file_changes)} files)")
                elif capturing_file_changes:
                    if line.startswith('FILE: '):
                        # Save previous file data if exists
                        if current_file:
                            file_changes.append({
                                'filename': current_file,
                                'before': '\n'.join(current_before),
                                'after': '\n'.join(current_after)
                            })
                        # Start new file
                        current_file = line.split('FILE: ', 1)[1]
                        current_before = []
                        current_after = []
                        capturing_before = False
                        capturing_after = False
                    elif line == '=== BEFORE START ===':
                        capturing_before = True
                        capturing_after = False
                    elif line == '=== BEFORE END ===':
                        capturing_before = False
                    elif line == '=== AFTER START ===':
                        capturing_after = True
                        capturing_before = False
                    elif line == '=== AFTER END ===':
                        capturing_after = False
                    elif line == '=== FILE END ===':
                        # File processing complete
                        pass
                    elif capturing_before:
                        current_before.append(line)
                    elif capturing_after:
                        current_after.append(line)
                elif capturing_patch:
                    git_patch.append(line)
                elif capturing_diff:
                    git_diff.append(line)
                elif capturing_files:
                    if line.strip():  # Only add non-empty lines
                        changed_files.append(line.strip())
            
            logger.info(f"🔄 Updating task status to COMPLETED...")
            
            # Update task in database
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'completed',
                'commit_hash': commit_hash,
                'git_diff': '\n'.join(git_diff),
                'git_patch': '\n'.join(git_patch),
                'changed_files': changed_files,
                'execution_metadata': {
                    'file_changes': file_changes,
                    'completed_at': datetime.now().isoformat()
                }
            })
            
            logger.info(f"🎉 {model_name} Task {task_id} completed successfully! Commit: {commit_hash[:8] if commit_hash else 'N/A'}, Diff lines: {len(git_diff)}")
            
        else:
            logger.error(f"❌ Container exited with error code {result['StatusCode']}")
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'failed',
                'error': f"Container exited with code {result['StatusCode']}: {logs}"
            })
            logger.error(f"💥 {model_name} Task {task_id} failed: {logs[:200]}...")
            
    except Exception as e:
        model_name = task.get('agent', 'claude').upper() if task else 'UNKNOWN'
        logger.error(f"💥 Unexpected exception in {model_name} task {task_id}: {str(e)}")
        
        try:
            DatabaseOperations.update_task(task_id, user_id, {
                'status': 'failed',
                'error': str(e)
            })
        except:
            logger.error(f"Failed to update task {task_id} status after exception")
        
        logger.error(f"🔄 {model_name} Task {task_id} failed with exception: {str(e)}")
