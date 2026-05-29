import os
from pathlib import Path
from typing import List, Dict, Optional
import glob

class MemoryManager:
    """Manages HOT/WARM/COLD memory tiers for VIVID Agent"""
    
    def __init__(self, config):
        self.config = config
        self.workspace_dir = config.workspace_dir
    
    def load_system_context(self) -> str:
        """Build system prompt from SOUL.md, USER.md, MEMORY.md"""
        parts = []
        
        # Load IDENTITY.md
        identity = self._load_file("IDENTITY.md")
        if identity:
            parts.append(f"## Agent Identity\n{identity}\n")
        
        # Load SOUL.md
        soul = self._load_file("SOUL.md")
        if soul:
            parts.append(f"## Core Truths\n{soul}\n")
        
        # Load USER.md
        user = self._load_file("USER.md")
        if user:
            parts.append(f"## About the User\n{user}\n")
        
        # Load MEMORY.md (HOT memory - most recent)
        memory = self._load_file("MEMORY.md")
        if memory:
            parts.append(f"## Long-Term Memory\n{memory[:10000]}\n")  # Limit size
        
        # Load AGENTS.md (capabilities)
        agents = self._load_file("AGENTS.md")
        if agents:
            parts.append(f"## Capabilities\n{agents[:5000]}\n")
        
        # Load TOOLS.md
        tools = self._load_file("TOOLS.md")
        if tools:
            parts.append(f"## Tools Configuration\n{tools[:3000]}\n")
        
        # Load recent memory archives (WARM)
        recent_memories = self._load_recent_memories(3)
        if recent_memories:
            parts.append(f"## Recent Session Memories\n{recent_memories}\n")
        
        return "\n".join(parts)
    
    def _load_file(self, filename: str) -> Optional[str]:
        """Load a file from the workspace"""
        path = self.workspace_dir / filename
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception:
            return None
    
    def _load_recent_memories(self, count: int = 3) -> str:
        """Load the N most recent memory archive files"""
        memory_dir = self.workspace_dir / "memory"
        if not memory_dir.exists():
            return ""
        
        files = sorted(memory_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        parts = []
        for f in files[:count]:
            try:
                content = f.read_text(encoding='utf-8', errors='replace')
                parts.append(f"### {f.name}\n{content[:5000]}\n")
            except Exception:
                continue
        
        return "\n".join(parts)
    
    def search(self, query: str) -> List[Dict]:
        """Search all memory files for relevant content"""
        results = []
        
        # Search workspace root files
        for file in self.workspace_dir.glob("*.md"):
            result = self._score_file(file, query)
            if result:
                results.append(result)
        
        # Search memory archives
        memory_dir = self.workspace_dir / "memory"
        if memory_dir.exists():
            for file in memory_dir.glob("*.md"):
                result = self._score_file(file, query)
                if result:
                    results.append(result)
        
        # Search skills
        skills_dir = self.workspace_dir / "skills"
        if skills_dir.exists():
            for file in skills_dir.rglob("SKILL.md"):
                result = self._score_file(file, query)
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:20]
    
    def _score_file(self, file_path: Path, query: str) -> Optional[Dict]:
        """Score a file's relevance to a query"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            query_words = set(query.lower().split())
            content_lower = content.lower()
            score = sum(1 for word in query_words if word in content_lower)
            
            if score > 0:
                return {
                    "path": str(file_path),
                    "score": score,
                    "preview": content[:1500],
                    "name": file_path.name
                }
        except Exception:
            pass
        return None
    
    def append_session(self, content: str):
        """Append content to today's memory file"""
        import datetime
        memory_dir = self.workspace_dir / "memory"
        memory_dir.mkdir(exist_ok=True)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = memory_dir / f"{today}.md"
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}\n")
    
    def get_corrections(self) -> str:
        """Load recent corrections"""
        corrections_file = Path.home() / "self-improving" / "corrections.md"
        if corrections_file.exists():
            return corrections_file.read_text(encoding='utf-8', errors='replace')[:5000]
        return ""
    
    def get_reflections(self) -> str:
        """Load self-reflections"""
        reflections_file = Path.home() / "self-improving" / "reflections.md"
        if reflections_file.exists():
            return reflections_file.read_text(encoding='utf-8', errors='replace')[:5000]
        return ""
