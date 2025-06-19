#!/bin/bash

echo "Testing Claude Code Model Selection API..."

# Test Claude model
echo "Testing Claude Code model..."
curl -X POST http://localhost:5000/start-task \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add a test comment to README",
    "repo_url": "https://github.com/test/repo",
    "branch": "main",
    "github_token": "test_token",
    "model": "claude"
  }'

echo -e "\n\nTesting invalid model (should fail)..."
curl -X POST http://localhost:5000/start-task \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add a test comment to README",
    "repo_url": "https://github.com/test/repo",
    "branch": "main",
    "github_token": "test_token",
    "model": "codex"
  }'

echo -e "\n\nTesting another invalid model..."
curl -X POST http://localhost:5000/start-task \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add a test comment to README",
    "repo_url": "https://github.com/test/repo",
    "branch": "main",
    "github_token": "test_token",
    "model": "invalid_model"
  }'