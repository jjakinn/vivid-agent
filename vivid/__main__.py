#!/usr/bin/env python3
"""
VIVID Agent CLI — Entry Point
Usage: python -m vivid [command] [options]
"""

import sys
import argparse
from pathlib import Path

from vivid import VividAgent
from vivid.config import Config

def main():
    parser = argparse.ArgumentParser(
        description="🦆 VIVID Agent — Standalone AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vivid chat                     # Start interactive chat
  vivid run "build me a game"    # One-shot command
  vivid auth add kimi            # Add API key
  vivid auth list                # List configured keys
  vivid models                   # List available models
  vivid tools                    # List available tools
  vivid skills                   # List available skills
  vivid skill code               # Show skill details
  vivid memory search "galaxy"   # Search memory
  vivid memory get MEMORY.md     # Read memory file
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    chat_parser.add_argument("--model", "-m", help="Model to use")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Execute a one-shot command")
    run_parser.add_argument("prompt", help="The prompt to send")
    run_parser.add_argument("--model", "-m", help="Model to use")
    
    # Auth commands
    auth_parser = subparsers.add_parser("auth", help="Manage API keys")
    auth_sub = auth_parser.add_subparsers(dest="auth_command")
    auth_add = auth_sub.add_parser("add", help="Add an API key")
    auth_add.add_argument("provider", choices=["kimi", "openrouter", "brave", "ollama"], help="Provider name")
    auth_list = auth_sub.add_parser("list", help="List configured keys")
    
    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")
    
    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available tools")
    
    # Skills command
    skills_parser = subparsers.add_parser("skills", help="List available skills")
    skills_parser.add_argument("--category", "-c", help="Filter by category")
    skills_parser.add_argument("--search", "-s", help="Search skills")
    
    # Skill detail command
    skill_parser = subparsers.add_parser("skill", help="Show skill details")
    skill_parser.add_argument("name", help="Skill name")
    
    # Memory commands
    memory_parser = subparsers.add_parser("memory", help="Search or read memory")
    memory_sub = memory_parser.add_subparsers(dest="memory_command")
    memory_search = memory_sub.add_parser("search", help="Search memory files")
    memory_search.add_argument("query", help="Search query")
    memory_get = memory_sub.add_parser("get", help="Read a memory file")
    memory_get.add_argument("path", help="Path to memory file")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    
    # Repos command
    repos_parser = subparsers.add_parser("repos", help="Manage repositories")
    repos_sub = repos_parser.add_subparsers(dest="repos_command")
    repos_clone = repos_sub.add_parser("clone-all", help="Clone all repositories")
    repos_list = repos_sub.add_parser("list", help="List repositories")
    repos_update = repos_sub.add_parser("update-all", help="Update all repositories")
    
    # Version
    parser.add_argument("--version", "-v", action="version", version="VIVID Agent 1.0.0")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    agent = VividAgent()
    config = Config()
    
    if args.command == "chat":
        agent.interactive(model=args.model)
    
    elif args.command == "run":
        agent.run_command(args.prompt, model=args.model)
    
    elif args.command == "auth":
        if args.auth_command == "add":
            import getpass
            provider_map = {
                "kimi": "kimi-coding",
                "openrouter": "openrouter",
                "brave": "brave",
                "ollama": "ollama"
            }
            provider = provider_map[args.provider]
            key = getpass.getpass(f"Enter API key for {provider}: ")
            if key:
                config.set_api_key(provider, key)
            else:
                print("❌ No key provided")
        elif args.auth_command == "list":
            print("🔑 Configured API keys:")
            for provider in ["kimi-coding", "openrouter", "ollama"]:
                key = config.get_api_key(provider)
                status = "✅ Set" if key else "❌ Not set"
                print(f"  {provider}: {status}")
            brave_key = config.get("tools.web_search.api_key") or config.get_api_key("brave")
            print(f"  brave: {'✅ Set' if brave_key else '❌ Not set'}")
        else:
            auth_parser.print_help()
    
    elif args.command == "models":
        print("📊 Available models:")
        for model in agent.models.list_models():
            print(f"  - {model}")
    
    elif args.command == "tools":
        print("🔧 Available tools:")
        for name, info in agent.tools.list_tools().items():
            print(f"  - {name}: {info['description']}")
    
    elif args.command == "skills":
        if args.category:
            categories = agent.skills.get_categories()
            if args.category in categories:
                print(f"🎯 Skills in category '{args.category}':")
                for name in sorted(categories[args.category]):
                    info = agent.skills.list_skills()[name]
                    print(f"  - {name}: {info['description'][:80]}")
            else:
                print(f"❌ Category '{args.category}' not found")
                print(f"Available: {', '.join(categories.keys())}")
        elif args.search:
            results = agent.skills.search(args.search)
            print(f"🔍 Skills matching '{args.search}':")
            for r in results:
                print(f"  - {r['name']} ({r['category']}): {r['description'][:80]}")
        else:
            categories = agent.skills.get_categories()
            print("🎯 Available skills by category:")
            for cat, skill_list in sorted(categories.items()):
                print(f"\n  {cat.upper()} ({len(skill_list)} skills):")
                for name in sorted(skill_list)[:5]:
                    info = agent.skills.list_skills()[name]
                    print(f"    - {name}: {info['description'][:60]}...")
                if len(skill_list) > 5:
                    print(f"    ... and {len(skill_list) - 5} more")
            print(f"\nTotal: {len(agent.skills.list_skills())} skills")
            print("\nUse 'vivid skills --search <query>' to search")
            print("Use 'vivid skill <name>' to see details")
    
    elif args.command == "skill":
        skills = agent.skills.list_skills()
        if args.name in skills:
            info = skills[args.name]
            print(f"\n🎯 Skill: {args.name}")
            print(f"   Category: {info['category']}")
            print(f"   Description: {info['description']}")
            print(f"   Parameters:")
            for param, desc in info['params'].items():
                print(f"     - {param}: {desc}")
        else:
            print(f"❌ Skill '{args.name}' not found")
            results = agent.skills.search(args.name)
            if results:
                print("Did you mean:")
                for r in results[:5]:
                    print(f"  - {r['name']}")
    
    elif args.command == "memory":
        if args.memory_command == "search":
            results = agent.memory.search(args.query)
            print(f"🔍 Search results for '{args.query}':")
            for r in results:
                print(f"\n📄 {r['name']} (score: {r['score']})")
                print(f"   Path: {r['path']}")
                print(f"   Preview: {r['preview'][:200]}...")
        elif args.memory_command == "get":
            result = agent.tools._memory_get(args.path)
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"📄 {result['path']} ({result['shown_lines']}/{result['total_lines']} lines)")
                print(result['content'])
        else:
            memory_parser.print_help()
    
    elif args.command == "config":
        print(f"⚙️  Configuration directory: {config.config_dir}")
        print(f"   Workspace: {config.workspace_dir}")
        print(f"   Default model: {config.get('models.default')}")
        print(f"   Skills: {len(agent.skills.list_skills())} loaded")
        print(f"   Config file: {config.config_file}")
        if config.config_file.exists():
            print(f"   ✅ Config exists")
        else:
            print(f"   ❌ No config file (will be created on first run)")
    
    elif args.command == "repos":
        from vivid.repos import clone_all, list_repos, update_all
        if args.repos_command == "clone-all":
            clone_all()
        elif args.repos_command == "list":
            list_repos()
        elif args.repos_command == "update-all":
            update_all()
        else:
            repos_parser.print_help()

if __name__ == "__main__":
    main()
