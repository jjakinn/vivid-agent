import json
import os
from pathlib import Path

class Config:
    """VIVID Agent configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".vivid"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        self.data = self._load()
    
    def _load(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return self._default()
    
    def _default(self):
        return {
            "models": {
                "default": "kimi-k2.5",
                "primary": "kimi-coding/k2p5",
                "fallbacks": ["kimi/k2.5", "kimi/kimi-code", "kimi-coding/kimi-k2-thinking"]
            },
            "providers": {
                "kimi-coding": {
                    "base_url": "https://api.kimi.com/coding/",
                    "api_key": None,
                    "api_format": "anthropic-messages"
                },
                "openrouter": {
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": None,
                    "api_format": "openai"
                },
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "api_key": None,
                    "api_format": "ollama"
                }
            },
            "tools": {
                "web_search": {
                    "enabled": True,
                    "provider": "brave",
                    "api_key": None
                },
                "web_fetch": {
                    "enabled": True
                }
            },
            "memory": {
                "workspace_dir": str(Path.home() / ".openclaw" / "workspace"),
                "hot_memory": "memory.md",
                "warm_memory": "projects/*.md",
                "cold_memory": "archive/*.md"
            },
            "agent": {
                "name": "VIVID",
                "emoji": "🦆",
                "identity_file": "IDENTITY.md",
                "soul_file": "SOUL.md",
                "user_file": "USER.md"
            }
        }
    
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key, default=None):
        keys = key.split('.')
        data = self.data
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data
    
    def set(self, key, value):
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save()
    
    def get_api_key(self, provider):
        """Get API key for a provider"""
        key = self.get(f"providers.{provider}.api_key")
        if key:
            return key
        # Try environment variable
        env_map = {
            "kimi-coding": "KIMI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "ollama": None,
            "brave": "BRAVE_API_KEY"
        }
        env_var = env_map.get(provider)
        if env_var:
            return os.environ.get(env_var)
        return None
    
    def set_api_key(self, provider, key):
        """Set API key for a provider"""
        self.set(f"providers.{provider}.api_key", key)
        print(f"✅ API key set for {provider}")
    
    @property
    def workspace_dir(self):
        return Path(self.get("memory.workspace_dir", str(Path.home() / ".openclaw" / "workspace")))
