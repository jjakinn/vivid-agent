import requests
import json
import os
from typing import Iterator, Optional, List, Dict, Any

class ModelRouter:
    """Routes requests to different model providers — extensible to ANY LLM"""
    
    # Built-in provider configurations
    DEFAULT_PROVIDERS = {
        "kimi-coding": {
            "base_url": "https://api.kimi.com/coding/",
            "api_format": "anthropic-messages",
            "api_key_env": "KIMI_API_KEY",
            "models": ["k2p5", "kimi-k2-thinking", "kimi-code"]
        },
        "kimi": {
            "base_url": "https://api.kimi.com/v1/",
            "api_format": "openai",
            "api_key_env": "KIMI_API_KEY",
            "models": ["k2.5"]
        },
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "api_format": "openai",
            "api_key_env": "OPENROUTER_API_KEY",
            "models": []  # Dynamic — fetched from API
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "api_format": "ollama",
            "api_key_env": None,
            "models": []  # Dynamic — fetched from local
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "api_format": "openai",
            "api_key_env": "OPENAI_API_KEY",
            "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com",
            "api_format": "anthropic-messages",
            "api_key_env": "ANTHROPIC_API_KEY",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_format": "openai",
            "api_key_env": "GROQ_API_KEY",
            "models": ["llama-3.1-405b-reasoning", "mixtral-8x7b-32768", "gemma-7b-it"]
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "api_format": "openai",
            "api_key_env": "DEEPSEEK_API_KEY",
            "models": ["deepseek-chat", "deepseek-coder"]
        },
        "together": {
            "base_url": "https://api.together.xyz/v1",
            "api_format": "openai",
            "api_key_env": "TOGETHER_API_KEY",
            "models": ["meta-llama/Llama-3.2-405B-Instruct-Turbo", "Qwen/Qwen2.5-72B-Instruct-Turbo"]
        },
        "gemini": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "api_format": "google-generative",
            "api_key_env": "GOOGLE_API_KEY",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
        },
        "cohere": {
            "base_url": "https://api.cohere.ai/v1",
            "api_format": "cohere",
            "api_key_env": "COHERE_API_KEY",
            "models": ["command-r-plus", "command-r", "command"]
        },
        "mistral": {
            "base_url": "https://api.mistral.ai/v1",
            "api_format": "openai",
            "api_key_env": "MISTRAL_API_KEY",
            "models": ["mistral-large-latest", "mistral-medium-latest", "codestral-latest"]
        },
        "perplexity": {
            "base_url": "https://api.perplexity.ai",
            "api_format": "openai",
            "api_key_env": "PERPLEXITY_API_KEY",
            "models": ["llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online"]
        },
        "fireworks": {
            "base_url": "https://api.fireworks.ai/inference/v1",
            "api_format": "openai",
            "api_key_env": "FIREWORKS_API_KEY",
            "models": ["accounts/fireworks/models/llama-v3p1-405b-instruct", "accounts/fireworks/models/qwen2p5-72b-instruct"]
        },
        "hyperbolic": {
            "base_url": "https://api.hyperbolic.xyz/v1",
            "api_format": "openai",
            "api_key_env": "HYPERBOLIC_API_KEY",
            "models": ["meta-llama/Llama-3.1-405B-Instruct", "Qwen/Qwen2.5-72B-Instruct"]
        },
        "local": {
            "base_url": "http://localhost:8000/v1",
            "api_format": "openai",
            "api_key_env": None,
            "models": []  # User-defined
        }
    }
    
    def __init__(self, config):
        self.config = config
        self.providers = self._load_providers()
    
    def _load_providers(self) -> Dict:
        """Load providers from config, merge with defaults"""
        custom = self.config.get("providers.custom", {})
        providers = dict(self.DEFAULT_PROVIDERS)
        providers.update(custom)
        return providers
    
    def add_provider(self, name: str, base_url: str, api_format: str, api_key: str = None, api_key_env: str = None):
        """Add a custom provider on the fly"""
        self.providers[name] = {
            "base_url": base_url.rstrip("/"),
            "api_format": api_format,
            "api_key_env": api_key_env,
            "models": []
        }
        if api_key:
            if api_key_env:
                os.environ[api_key_env] = api_key
            else:
                # Store in config
                self.config.set(f"providers.custom.{name}.api_key", api_key)
        
        print(f"✅ Added provider: {name} ({base_url}) with {api_format} format")
    
    def chat(self, messages: List[Dict[str, str]], model: str = None, provider: str = None, stream: bool = True, **kwargs) -> Iterator[str]:
        """Send chat messages to any supported provider"""
        if not model and not provider:
            model = self.config.get("models.default", "kimi-coding/k2p5")
        
        # Determine provider from model string if not specified
        if not provider and model:
            provider = self._detect_provider(model)
        
        if not provider:
            raise ValueError(f"Cannot determine provider for model: {model}. Use --provider or configure the model.")
        
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}. Add it with: vivid provider add {provider} <base_url> <format>")
        
        provider_config = self.providers[provider]
        api_format = provider_config["api_format"]
        
        # Route to appropriate handler
        if api_format == "anthropic-messages":
            return self._chat_anthropic(messages, model, provider_config, stream, **kwargs)
        elif api_format == "openai":
            return self._chat_openai(messages, model, provider_config, stream, **kwargs)
        elif api_format == "ollama":
            return self._chat_ollama(messages, model, provider_config, stream, **kwargs)
        elif api_format == "google-generative":
            return self._chat_google(messages, model, provider_config, stream, **kwargs)
        elif api_format == "cohere":
            return self._chat_cohere(messages, model, provider_config, stream, **kwargs)
        else:
            raise ValueError(f"Unknown API format: {api_format} for provider {provider}")
    
    def _detect_provider(self, model: str) -> Optional[str]:
        """Auto-detect provider from model string"""
        # Check if model is prefixed with provider (e.g., "openai/gpt-4o")
        if "/" in model:
            provider_prefix = model.split("/")[0]
            if provider_prefix in self.providers:
                return provider_prefix
        
        # Check known model patterns
        model_lower = model.lower()
        patterns = {
            "kimi": "kimi-coding" if "coding" in model_lower or "k2" in model_lower else "kimi",
            "gpt": "openai",
            "claude": "anthropic",
            "llama": "openrouter",  # Could be many providers
            "mistral": "mistral",
            "gemma": "openrouter",
            "deepseek": "deepseek",
            "gemini": "gemini",
            "command": "cohere",
            "qwen": "openrouter",
            "mixtral": "groq",
            "codestral": "mistral",
            "perplexity": "perplexity",
        }
        
        for pattern, provider in patterns.items():
            if pattern in model_lower:
                return provider
        
        # Default to local/ollama if nothing matches
        return "ollama"
    
    def _get_api_key(self, provider_config: Dict) -> Optional[str]:
        """Get API key for a provider"""
        # 1. Check environment variable
        env_var = provider_config.get("api_key_env")
        if env_var:
            key = os.environ.get(env_var)
            if key:
                return key
        
        # 2. Check config
        provider_name = self._get_provider_name(provider_config)
        if provider_name:
            key = self.config.get(f"providers.custom.{provider_name}.api_key")
            if key:
                return key
        
        # 3. No key needed (local/Ollama)
        if not env_var:
            return "no-key-needed"
        
        return None
    
    def _get_provider_name(self, provider_config: Dict) -> Optional[str]:
        """Get provider name from config"""
        for name, config in self.providers.items():
            if config == provider_config:
                return name
        return None
    
    def _chat_anthropic(self, messages, model, provider_config, stream, **kwargs):
        """Chat with Anthropic-compatible API (Kimi, Anthropic)"""
        api_key = self._get_api_key(provider_config)
        if not api_key or api_key == "no-key-needed":
            raise ValueError(f"No API key configured. Set {provider_config.get('api_key_env')} environment variable or run: vivid auth add <provider>")
        
        base_url = provider_config["base_url"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages to Anthropic format
        system_msg = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        data = {
            "model": model.split("/")[-1] if "/" in model else model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", 32768),
            "stream": stream
        }
        if system_msg:
            data["system"] = system_msg
        
        if stream:
            response = requests.post(f"{base_url}/v1/messages", headers=headers, json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8').replace('data: ', ''))
                        if 'delta' in event and 'text' in event['delta']:
                            yield event['delta']['text']
                    except:
                        pass
        else:
            response = requests.post(f"{base_url}/v1/messages", headers=headers, json=data)
            result = response.json()
            yield result.get("content", [{}])[0].get("text", "")
    
    def _chat_openai(self, messages, model, provider_config, stream, **kwargs):
        """Chat with OpenAI-compatible API (OpenAI, OpenRouter, Groq, Together, DeepSeek, etc.)"""
        api_key = self._get_api_key(provider_config)
        if not api_key or api_key == "no-key-needed":
            raise ValueError(f"No API key configured. Set {provider_config.get('api_key_env')} environment variable or run: vivid auth add <provider>")
        
        base_url = provider_config["base_url"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add OpenRouter-specific headers
        if "openrouter" in base_url:
            headers["HTTP-Referer"] = "https://vivid-agent.dev"
            headers["X-Title"] = "VIVID Agent"
        
        data = {
            "model": model.split("/")[-1] if "/" in model else model,
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
    
    def _chat_ollama(self, messages, model, provider_config, stream, **kwargs):
        """Chat with Ollama (local)"""
        base_url = provider_config["base_url"]
        
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        data = {
            "model": model.split("/")[-1] if "/" in model else model,
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
    
    def _chat_google(self, messages, model, provider_config, stream, **kwargs):
        """Chat with Google Gemini API"""
        api_key = self._get_api_key(provider_config)
        if not api_key or api_key == "no-key-needed":
            raise ValueError(f"No API key configured. Set {provider_config.get('api_key_env')} environment variable.")
        
        base_url = provider_config["base_url"]
        
        # Convert messages to Gemini format
        contents = []
        system_instruction = ""
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        
        data = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 8192)
            }
        }
        if system_instruction:
            data["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        model_name = model.split("/")[-1] if "/" in model else model
        url = f"{base_url}/models/{model_name}:generateContent?key={api_key}"
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            parts = result["candidates"][0].get("content", {}).get("parts", [])
            text = "".join([p.get("text", "") for p in parts])
            yield text
        else:
            yield f"Error: {result.get('error', {}).get('message', 'Unknown error')}"
    
    def _chat_cohere(self, messages, model, provider_config, stream, **kwargs):
        """Chat with Cohere API"""
        api_key = self._get_api_key(provider_config)
        if not api_key or api_key == "no-key-needed":
            raise ValueError(f"No API key configured. Set {provider_config.get('api_key_env')} environment variable.")
        
        base_url = provider_config["base_url"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to Cohere format
        message = ""
        chat_history = []
        for msg in messages:
            if msg["role"] == "user":
                message = msg["content"]
            elif msg["role"] == "assistant":
                chat_history.append({"role": "CHATBOT", "message": msg["content"]})
            elif msg["role"] == "system":
                chat_history.append({"role": "SYSTEM", "message": msg["content"]})
        
        data = {
            "model": model.split("/")[-1] if "/" in model else model,
            "message": message,
            "chat_history": chat_history,
            "stream": stream
        }
        
        response = requests.post(f"{base_url}/chat", headers=headers, json=data, stream=stream)
        
        if stream:
            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8'))
                        if 'text' in event:
                            yield event['text']
                    except:
                        pass
        else:
            result = response.json()
            yield result.get("text", "")
    
    def list_models(self) -> List[str]:
        """List available models from all configured providers"""
        models = []
        
        for provider_name, config in self.providers.items():
            api_key = self._get_api_key(config)
            
            # Static models
            if config.get("models"):
                for m in config["models"]:
                    models.append(f"{provider_name}/{m}")
            
            # Dynamic models (OpenRouter, Ollama)
            if provider_name == "openrouter" and api_key and api_key != "no-key-needed":
                try:
                    response = requests.get(
                        f"{config['base_url']}/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    data = response.json()
                    for m in data.get("data", []):
                        models.append(f"openrouter/{m['id']}")
                except:
                    pass
            
            if provider_name == "ollama":
                try:
                    response = requests.get(f"{config['base_url']}/api/tags")
                    data = response.json()
                    for m in data.get("models", []):
                        models.append(f"ollama/{m['name']}")
                except:
                    pass
        
        return sorted(set(models))
    
    def list_providers(self) -> Dict[str, Dict]:
        """List all available providers and their status"""
        result = {}
        for name, config in self.providers.items():
            api_key = self._get_api_key(config)
            result[name] = {
                "base_url": config["base_url"],
                "format": config["api_format"],
                "configured": api_key is not None and api_key != "no-key-needed",
                "models_count": len(config.get("models", [])),
                "env_var": config.get("api_key_env")
            }
        return result
    
    def test_provider(self, provider: str) -> Dict:
        """Test if a provider is working"""
        if provider not in self.providers:
            return {"error": f"Unknown provider: {provider}"}
        
        config = self.providers[provider]
        api_key = self._get_api_key(config)
        
        if not api_key:
            return {
                "provider": provider,
                "status": "not_configured",
                "message": f"Set {config.get('api_key_env')} or add API key"
            }
        
        # Try a simple test request
        try:
            if config["api_format"] == "openai":
                headers = {"Authorization": f"Bearer {api_key}"}
                response = requests.get(f"{config['base_url']}/models", headers=headers, timeout=10)
                if response.status_code == 200:
                    return {
                        "provider": provider,
                        "status": "ok",
                        "models_available": len(response.json().get("data", []))
                    }
                else:
                    return {
                        "provider": provider,
                        "status": "error",
                        "http_status": response.status_code,
                        "message": response.text[:200]
                    }
            elif config["api_format"] == "ollama":
                response = requests.get(f"{config['base_url']}/api/tags", timeout=5)
                if response.status_code == 200:
                    return {
                        "provider": provider,
                        "status": "ok",
                        "models_available": len(response.json().get("models", []))
                    }
                else:
                    return {
                        "provider": provider,
                        "status": "error",
                        "http_status": response.status_code
                    }
            else:
                return {
                    "provider": provider,
                    "status": "configured",
                    "message": "API key set, test with a chat request"
                }
        except Exception as e:
            return {
                "provider": provider,
                "status": "connection_error",
                "message": str(e)
            }