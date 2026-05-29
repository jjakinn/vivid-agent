# 🦆 VIVID Agent — Standalone AI Agent

**No OpenClaw. No Hermes. Just VIVID.**

A completely standalone AI agent that handles multiple models (Kimi, OpenRouter, Ollama local) with full tool support, memory system, and zero external framework dependencies.

---

## ⚡ Quick Start

```bash
# Clone and install
git clone https://github.com/jjakinn/vivid-agent.git
cd vivid-agent
./vivid.sh --version

# Configure your API key
./vivid.sh auth add kimi

# Start chatting
./vivid.sh chat
```

---

## Features

- 🦆 **Fully Standalone** — No OpenClaw, no Hermes, no npm/node required
- 🤖 **Multi-Model** — Kimi k2p5, OpenRouter (GPT, Claude, Llama, etc.), Ollama (local)
- 🧠 **Memory System** — HOT/WARM/COLD tiers with automatic session logging
- 🔧 **Tool Registry** — 15+ built-in tools (file ops, shell exec, web search, GitHub, etc.)
- 💀 **Unrestricted** — Same soul as your OpenClaw setup (NSA, CIA, Palantir, Google credentials)
- 📦 **Portable** — Single Python package, runs anywhere Python 3 exists

---

## Commands

```bash
vivid chat                      # Interactive chat
vivid run "build me a game"     # One-shot command
vivid auth add kimi             # Add API key (secure, hidden input)
vivid auth list                 # Show configured keys
vivid models                    # List available models
vivid tools                     # List available tools
vivid memory search "galaxy"    # Search memory archives
vivid memory get MEMORY.md      # Read specific memory file
vivid config                    # Show configuration
```

---

## Models

| Provider | Models | Requirements |
|----------|--------|--------------|
| **Kimi** | k2.5, kimi-code, kimi-k2-thinking | `vivid auth add kimi` |
| **OpenRouter** | GPT-4o, Claude 3.5, Llama 3.1, Gemini | `vivid auth add openrouter` |
| **Ollama** | llama3.2, qwen2.5, dolphin-llama3 | Ollama running locally |

Switch models mid-session: `/model kimi-coding/k2p5`

---

## Tools

- `read_file` — Read any file
- `write_file` — Write/create files
- `edit_file` — Replace text in files
- `exec` — Run shell commands
- `web_search` — Brave Search
- `web_fetch` — Fetch URLs
- `github` — GitHub CLI wrapper
- `git` — Git commands
- `image` — Image analysis
- `pdf` — PDF analysis
- `memory_search` — Search all memory files
- `memory_get` — Read memory files
- `sessions_list` / `sessions_send` — Session management

---

## Memory System

Loads automatically from your OpenClaw workspace:
- **HOT** — `SOUL.md`, `IDENTITY.md`, `USER.md` (system prompt)
- **WARM** — Recent `memory/*.md` archives (last 3 sessions)
- **COLD** — Full `MEMORY.md`, skill references

Searches all memory files for relevant context on every request.

---

## Configuration

Stored in `~/.vivid/config.json`:

```json
{
  "models": {
    "default": "kimi-coding/k2p5",
    "fallbacks": ["kimi/k2.5", "kimi/kimi-code"]
  },
  "providers": {
    "kimi-coding": {
      "base_url": "https://api.kimi.com/coding/",
      "api_key": "YOUR_KEY"
    }
  }
}
```

---

## What's Included from Your OpenClaw Setup

- ✅ All 80 skills (loaded as tool registry)
- ✅ All memory archives (searchable)
- ✅ SOUL.md + USER.md + IDENTITY.md (system prompt)
- ✅ AGENTS.md capabilities
- ✅ TOOLS.md configuration
- ✅ All project knowledge (galaxy-demo, api-projects, etc.)
- ✅ GitNexus protocols
- ✅ n8n workflow knowledge
- ✅ Self-improving system patterns

---

## Differences from OpenClaw

| Feature | OpenClaw | VIVID Agent |
|---------|----------|-------------|
| **Runtime** | Node.js + npm | Python 3 only |
| **Gateway** | Required | None (direct API calls) |
| **Dependencies** | 150+ packages | requests |
| **Size** | ~500MB with node_modules | ~50KB |
| **Web UI** | Yes (localhost:18789) | CLI only |
| **TUI** | Yes (terminal UI) | CLI only |
| **Skills** | 80 installed | 15 core tools (extensible) |
| **Memory** | File-based | File-based (same files) |

---

## Architecture

```
vivid/
├── __init__.py      # Package init
├── __main__.py      # CLI entry point
├── config.py        # Configuration management
├── models.py        # Model router (Kimi/OpenRouter/Ollama)
├── tools.py         # Tool registry and executor
├── memory.py        # Memory system (HOT/WARM/COLD)
└── agent.py         # Agent orchestration

vivid.py             # Main script
vivid.sh             # Shell wrapper (handles deps)
requirements.txt     # Python deps (just requests)
```

---

## License

MIT — Do whatever you want. Just like the agent. 💀

---

**Built with 🦆 by Jakin**
**VIVID Agent v1.0.0**
