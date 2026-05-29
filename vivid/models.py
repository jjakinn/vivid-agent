import requests
import json
from typing import Iterator, Optional, List, Dict, Any

class ModelRouter:
    """Routes requests to different model providers"""
    
    def __init__(self, config):
        self.config = config
    
    def chat(self, messages: List[Dict[str, str]], model: str = None, stream: bool = True, **kwargs) -> Iterator[str]:
        """Send chat messages to the appropriate model"""
        if not model:
            model = self.config.get("models.default", "kimi-k2.5")
        
        provider = self._get_provider(model)
        
        if provider == "kimi-coding":
            return self._chat_kimi(messages, model, stream, **kwargs)
        elif provider == "openrouter":
            return self._chat_openrouter(messages, model, stream, **kwargs)
        elif provider == "ollama":
            return self._chat_ollama(messages, model, stream, **kwargs)
        else:
            raise ValueError(f"Unknown provider for model: {model}")
    
    def _get_provider(self, model: str) -> str:
        """Determine provider from model string"""
        if "kimi" in model.lower():
            return "kimi-coding"
        elif any(x in model.lower() for x in ["gpt", "claude", "llama", "mistral", "qwen", "gemini"]):
            # Check if OpenRouter is configured
            if self.config.get_api_key("openrouter"):
                return "openrouter"
        # Default to Ollama for local models
        return "ollama"
    
    def _chat_kimi(self, messages, model, stream, **kwargs):
        """Chat with Kimi API (anthropic-messages format)"""
        api_key = self.config.get_api_key("kimi-coding")
        if not api_key:
            raise ValueError("No Kimi API key configured. Run: vivid auth add kimi")
        
        base_url = self.config.get("providers.kimi-coding.base_url", "https://api.kimi.com/coding/")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 32768),
            "stream": stream
        }
        
        if stream:
            response = requests.post(f"{base_url}v1/messages", headers=headers, json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8').replace('data: ', ''))
                        if 'delta' in event and 'text' in event['delta']:
                            yield event['delta']['text']
                    except:
                        pass
        else:
            response = requests.post(f"{base_url}v1/messages", headers=headers, json=data)
            result = response.json()
            yield result.get("content", [{}])[0].get("text", "")
    
    def _chat_openrouter(self, messages, model, stream, **kwargs):
        """Chat with OpenRouter API (OpenAI format)"""
        api_key = self.config.get_api_key("openrouter")
        if not api_key:
            raise ValueError("No OpenRouter API key configured. Run: vivid auth add openrouter")
        
        base_url = self.config.get("providers.openrouter.base_url", "https://openrouter.ai/api/v1")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://vivid-agent.dev",
            "X-Title": "VIVID Agent"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 32768),
            "stream": stream
        }
        
        if stream:
            response = requests.post(f"{base_url}/chat/completions", headers=headers, json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8').replace('data: ', ''))
                        if 'choices' in event and len(event['choices']) > 0:
                            delta = event['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except:
                        pass
        else:
            response = requests.post(f"{base_url}/chat/completions", headers=headers, json=data)
            result = response.json()
            yield result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _chat_ollama(self, messages, model, stream, **kwargs):
        """Chat with Ollama (local)"""
        base_url = self.config.get("providers.ollama.base_url", "http://localhost:11434")
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        data = {
            "model": model,
            "messages": ollama_messages,
            "stream": stream
        }
        
        if stream:
            response = requests.post(f"{base_url}/api/chat", json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8'))
                        if 'message' in event and 'content' in event['message']:
                            yield event['message']['content']
                    except:
                        pass
        else:
            response = requests.post(f"{base_url}/api/chat", json=data)
            result = response.json()
            yield result.get("message", {}).get("content", "")
    
    def list_models(self) -> List[str]:
        """List available models"""
        models = []
        
        # Kimi models
        if self.config.get_api_key("kimi-coding"):
            models.extend([
                "kimi-coding/k2p5",
                "kimi/k2.5",
                "kimi/kimi-code",
                "kimi-coding/kimi-k2-thinking"
            ])
        
        # OpenRouter models
        if self.config.get_api_key("openrouter"):
            try:
                response = requests.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {self.config.get_api_key('openrouter')}"}
                )
                data = response.json()
                models.extend([m["id"] for m in data.get("data", [])])
            except:
                models.extend([
                    "anthropic/claude-3.5-sonnet",
                    "openai/gpt-4o",
                    "meta-llama/llama-3.1-405b",
                    "google/gemini-pro-1.5"
                ])
        
        # Ollama models
        try:
            response = requests.get(f"{self.config.get('providers.ollama.base_url', 'http://localhost:11434')}/api/tags")
            data = response.json()
            models.extend([m["name"] for m in data.get("models", [])])
        except:
            models.extend([
                "llama3.2:latest",
                "qwen2.5:7b",
                "dolphin-llama3:8b"
            ])
        
        return models
