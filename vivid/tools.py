import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

class ToolRegistry:
    """Executes tools and skills for VIVID Agent"""
    
    AVAILABLE_TOOLS = {
        # File operations
        "read_file": {
            "description": "Read contents of a file",
            "params": {"file_path": "Path to file"}
        },
        "write_file": {
            "description": "Write content to a file",
            "params": {"file_path": "Path to file", "content": "File content"}
        },
        "edit_file": {
            "description": "Edit a file by replacing text",
            "params": {"file_path": "Path to file", "old_string": "Text to replace", "new_string": "Replacement text"}
        },
        # Shell operations
        "exec": {
            "description": "Execute a shell command",
            "params": {"command": "Command to run", "workdir": "Working directory (optional)"}
        },
        # Search operations
        "web_search": {
            "description": "Search the web using Brave",
            "params": {"query": "Search query", "count": "Number of results (default 10)"}
        },
        "web_fetch": {
            "description": "Fetch content from a URL",
            "params": {"url": "URL to fetch"}
        },
        # Code operations
        "github": {
            "description": "Run GitHub CLI commands",
            "params": {"command": "gh command to run"}
        },
        "git": {
            "description": "Run git commands",
            "params": {"command": "git command to run"}
        },
        # Analysis
        "image": {
            "description": "Analyze an image",
            "params": {"image": "Path or URL to image", "prompt": "Analysis prompt"}
        },
        "pdf": {
            "description": "Analyze PDF documents",
            "params": {"pdf": "Path or URL to PDF", "prompt": "Analysis prompt"}
        },
        # System
        "memory_search": {
            "description": "Search memory files",
            "params": {"query": "Search query"}
        },
        "memory_get": {
            "description": "Read specific memory file",
            "params": {"path": "Memory file path", "from": "Line to start from", "lines": "Number of lines"}
        },
        "sessions_list": {
            "description": "List active sessions",
            "params": {}
        },
        "sessions_send": {
            "description": "Send message to another session",
            "params": {"session_key": "Session key", "message": "Message to send"}
        }
    }
    
    def __init__(self, config):
        self.config = config
        self.brave_api_key = config.get("tools.web_search.api_key") or os.environ.get("BRAVE_API_KEY")
    
    def list_tools(self) -> Dict[str, Dict]:
        """List all available tools"""
        return self.AVAILABLE_TOOLS
    
    def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_name not in self.AVAILABLE_TOOLS:
            return {"error": f"Unknown tool: {tool_name}", "available": list(self.AVAILABLE_TOOLS.keys())}
        
        try:
            if tool_name == "read_file":
                return self._read_file(params["file_path"])
            elif tool_name == "write_file":
                return self._write_file(params["file_path"], params["content"])
            elif tool_name == "edit_file":
                return self._edit_file(params["file_path"], params["old_string"], params["new_string"])
            elif tool_name == "exec":
                return self._exec(params["command"], params.get("workdir"))
            elif tool_name == "web_search":
                return self._web_search(params["query"], params.get("count", 10))
            elif tool_name == "web_fetch":
                return self._web_fetch(params["url"])
            elif tool_name == "github":
                return self._exec(f"gh {params['command']}")
            elif tool_name == "git":
                return self._exec(f"git {params['command']}")
            elif tool_name == "memory_search":
                return self._memory_search(params["query"])
            elif tool_name == "memory_get":
                return self._memory_get(params["path"], params.get("from"), params.get("lines"))
            else:
                return {"error": f"Tool {tool_name} not yet implemented"}
        except Exception as e:
            return {"error": str(e), "tool": tool_name}
    
    def _read_file(self, file_path: str) -> Dict:
        path = Path(file_path).expanduser()
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return {"content": content, "path": str(path), "size": len(content)}
        except Exception as e:
            return {"error": str(e)}
    
    def _write_file(self, file_path: str, content: str) -> Dict:
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": str(path), "bytes_written": len(content)}
    
    def _edit_file(self, file_path: str, old_string: str, new_string: str) -> Dict:
        path = Path(file_path).expanduser()
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        if old_string not in content:
            return {"error": f"Old string not found in file"}
        content = content.replace(old_string, new_string, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": str(path)}
    
    def _exec(self, command: str, workdir: Optional[str] = None) -> Dict:
        try:
            cwd = Path(workdir).expanduser() if workdir else None
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out", "command": command}
        except Exception as e:
            return {"error": str(e), "command": command}
    
    def _web_search(self, query: str, count: int = 10) -> Dict:
        if not self.brave_api_key:
            return {"error": "No Brave API key configured. Run: vivid auth add brave"}
        try:
            import requests
            headers = {"X-Subscription-Token": self.brave_api_key}
            params = {"q": query, "count": min(count, 10)}
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )
            data = response.json()
            results = []
            for result in data.get("web", {}).get("results", [])[:count]:
                results.append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "description": result.get("description")
                })
            return {"results": results, "query": query}
        except Exception as e:
            return {"error": str(e)}
    
    def _web_fetch(self, url: str) -> Dict:
        try:
            import requests
            response = requests.get(url, timeout=30)
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # Simple HTML to text extraction
                text = self._html_to_text(response.text)
            else:
                text = response.text
            return {
                "content": text[:50000],  # Limit size
                "url": url,
                "status_code": response.status_code,
                "content_type": content_type
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion"""
        import re
        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Decode entities
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    
    def _memory_search(self, query: str) -> Dict:
        """Search memory files for relevant content"""
        memory_dir = self.config.workspace_dir / "memory"
        if not memory_dir.exists():
            return {"results": [], "message": "No memory directory found"}
        
        results = []
        for file_path in memory_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                # Simple relevance scoring
                query_lower = query.lower()
                score = sum(1 for word in query_lower.split() if word in content.lower())
                if score > 0:
                    # Get context around matches
                    lines = content.split('\n')
                    context = '\n'.join(lines[:50])  # First 50 lines as preview
                    results.append({
                        "file": str(file_path),
                        "score": score,
                        "preview": context[:2000]
                    })
            except Exception:
                continue
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"results": results[:10], "query": query}
    
    def _memory_get(self, path: str, from_line: Optional[int] = None, num_lines: Optional[int] = None) -> Dict:
        """Get specific lines from a memory file"""
        file_path = Path(path).expanduser()
        if not file_path.exists():
            # Try relative to workspace
            file_path = self.config.workspace_dir / path
        
        if not file_path.exists():
            return {"error": f"Memory file not found: {path}"}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            start = (from_line - 1) if from_line else 0
            end = start + num_lines if num_lines else len(lines)
            selected = lines[start:end]
            
            return {
                "content": ''.join(selected),
                "path": str(file_path),
                "total_lines": len(lines),
                "shown_lines": len(selected),
                "from": start + 1
            }
        except Exception as e:
            return {"error": str(e)}
