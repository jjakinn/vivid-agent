import os
import json
import subprocess
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

class SkillRegistry:
    """
    Complete skill registry — all 80 skills from OpenClaw setup.
    Each skill is a Python callable that the agent can invoke.
    """
    
    def __init__(self, config):
        self.config = config
        self.tools = self._build_registry()
    
    def _build_registry(self) -> Dict[str, Dict]:
        """Build the complete skill registry"""
        return {
            # ==================== DEVELOPMENT ====================
            "code": {
                "description": "Full coding workflow: plan, implement, verify, test",
                "category": "development",
                "params": {"task": "Description of coding task", "language": "Programming language", "context": "Additional context"},
                "handler": self._skill_code
            },
            "github": {
                "description": "GitHub CLI operations — issues, PRs, CI, code review",
                "category": "development",
                "params": {"command": "gh command to run", "args": "Additional arguments"},
                "handler": self._skill_github
            },
            "gh_issues": {
                "description": "Fetch issues, spawn sub-agents to fix, monitor PR reviews",
                "category": "development",
                "params": {"repo": "owner/repo", "label": "Issue label filter", "limit": "Max issues to fetch"},
                "handler": self._skill_gh_issues
            },
            "gitnexus": {
                "description": "Code intelligence — impact analysis, change detection, safe refactoring",
                "category": "development",
                "params": {"repo_path": "Path to repo", "action": "impact|detect_changes|rename", "target": "File or symbol to analyze"},
                "handler": self._skill_gitnexus
            },
            "mcporter": {
                "description": "MCP server management — list, configure, auth, call servers",
                "category": "development",
                "params": {"action": "list|call|config", "server": "Server name", "tool": "Tool name", "params": "Tool parameters"},
                "handler": self._skill_mcporter
            },
            "agent_browser": {
                "description": "Headless browser automation with accessibility tree snapshots",
                "category": "development",
                "params": {"url": "URL to open", "action": "navigate|snapshot|click|type", "selector": "Element selector"},
                "handler": self._skill_agent_browser
            },
            "session_logs": {
                "description": "Search and analyze conversation logs with jq",
                "category": "development",
                "params": {"query": "Search query", "filter": "jq filter expression"},
                "handler": self._skill_session_logs
            },
            "skill_creator": {
                "description": "Create or update AgentSkills with scripts, references, assets",
                "category": "development",
                "params": {"name": "Skill name", "description": "Skill description", "files": "Files to include"},
                "handler": self._skill_skill_creator
            },
            "data_analysis": {
                "description": "SQL, Python, visualization, statistical rigor — analysis with decision briefs",
                "category": "development",
                "params": {"data": "Data source or query", "analysis_type": "sql|python|visualization", "goal": "What decision to support"},
                "handler": self._skill_data_analysis
            },
            
            # ==================== COMMUNICATION ====================
            "gmail": {
                "description": "Gmail API — read, send, manage emails, threads, labels, drafts",
                "category": "communication",
                "params": {"action": "read|send|search|label", "to": "Recipient", "subject": "Subject", "body": "Email body"},
                "handler": self._skill_gmail
            },
            "google_meet": {
                "description": "Google Meet API — create meeting spaces, manage participants",
                "category": "communication",
                "params": {"action": "create|list|manage", "meeting_id": "Meeting ID"},
                "handler": self._skill_google_meet
            },
            "google_slides": {
                "description": "Google Slides API — create presentations, add slides, insert content",
                "category": "communication",
                "params": {"action": "create|add_slide|insert", "presentation_id": "Presentation ID", "content": "Content to insert"},
                "handler": self._skill_google_slides
            },
            "google_workspace_admin": {
                "description": "Google Workspace Admin — manage users, groups, organizational units",
                "category": "communication",
                "params": {"action": "list_users|create_user|manage_group", "user_email": "User email"},
                "handler": self._skill_google_workspace_admin
            },
            "apple_notes": {
                "description": "Manage Apple Notes via memo CLI — create, view, edit, delete, search",
                "category": "communication",
                "params": {"action": "create|view|edit|delete|search", "title": "Note title", "content": "Note content"},
                "handler": self._skill_apple_notes
            },
            "notion": {
                "description": "Notion API — create and manage pages, databases, blocks",
                "category": "communication",
                "params": {"action": "create_page|query_database|update_block", "parent_id": "Parent page/database ID"},
                "handler": self._skill_notion
            },
            "calendly": {
                "description": "Calendly API — event types, scheduled events, invitees, availability",
                "category": "communication",
                "params": {"action": "list_events|check_availability|book_meeting", "event_type": "Event type URI"},
                "handler": self._skill_calendly
            },
            "api_gateway": {
                "description": "Connect to 100+ APIs (Google, Microsoft, GitHub, Notion, Slack, etc.) via managed OAuth",
                "category": "communication",
                "params": {"service": "Service name", "action": "API action", "params": "API parameters"},
                "handler": self._skill_api_gateway
            },
            "telegram": {
                "description": "Telegram bot operations — send messages, manage channels",
                "category": "communication",
                "params": {"action": "send|manage", "chat_id": "Chat ID", "message": "Message text"},
                "handler": self._skill_telegram
            },
            
            # ==================== MARKETING ====================
            "copywriting": {
                "description": "Write, rewrite, improve marketing copy for any page — homepage, landing, pricing, about, product",
                "category": "marketing",
                "params": {"page_type": "homepage|landing|pricing|about|product", "product": "Product description", "tone": "Tone of voice"},
                "handler": self._skill_copywriting
            },
            "ad_creative": {
                "description": "Generate, iterate, scale ad creative — headlines, descriptions, primary text, full variations",
                "category": "marketing",
                "params": {"platform": "facebook|google|linkedin", "product": "Product description", "variations": "Number of variations"},
                "handler": self._skill_ad_creative
            },
            "email_sequence": {
                "description": "Create or optimize email sequences, drip campaigns, automated flows, lifecycle emails",
                "category": "marketing",
                "params": {"sequence_type": "welcome|onboarding|re-engagement|nurture", "emails": "Number of emails", "product": "Product description"},
                "handler": self._skill_email_sequence
            },
            "cold_email": {
                "description": "Write B2B cold emails and follow-up sequences that get replies",
                "category": "marketing",
                "params": {"target": "Target persona", "offer": "What you're offering", "followups": "Number of follow-ups"},
                "handler": self._skill_cold_email
            },
            "seo_audit": {
                "description": "Traditional technical and on-page SEO audits",
                "category": "marketing",
                "params": {"url": "Website URL", "depth": "Audit depth (quick|full)"},
                "handler": self._skill_seo_audit
            },
            "ai_seo": {
                "description": "Optimize content for AI search engines — get cited by LLMs, appear in AI-generated answers",
                "category": "marketing",
                "params": {"content": "Content to optimize", "target_ai": "chatgpt|perplexity|claude"},
                "handler": self._skill_ai_seo
            },
            "content_strategy": {
                "description": "Plan content strategy, decide what to create, topic clusters, editorial calendar",
                "category": "marketing",
                "params": {"niche": "Business niche", "goals": "Content goals", "timeline": "Planning timeline"},
                "handler": self._skill_content_strategy
            },
            "community_marketing": {
                "description": "Build and leverage online communities — Discord, Slack, forums, brand advocates",
                "category": "marketing",
                "params": {"platform": "discord|slack|reddit|forum", "goal": "community_goal", "audience": "Target audience"},
                "handler": self._skill_community_marketing
            },
            "competitor_profiling": {
                "description": "Research, profile, analyze competitors from their URLs",
                "category": "marketing",
                "params": {"urls": "List of competitor URLs", "depth": "quick|deep"},
                "handler": self._skill_competitor_profiling
            },
            "competitor_alternatives": {
                "description": "Create competitor comparison or alternative pages for SEO and sales enablement",
                "category": "marketing",
                "params": {"product": "Your product", "competitors": "Competitor names", "format": "singular|plural|vs|comparison"},
                "handler": self._skill_competitor_alternatives
            },
            "customer_research": {
                "description": "Conduct, analyze, synthesize customer research — interviews, surveys, support tickets, Reddit mining",
                "category": "marketing",
                "params": {"source": "interviews|surveys|reviews|reddit|tickets", "topic": "Research topic"},
                "handler": self._skill_customer_research
            },
            "ab_test_setup": {
                "description": "Plan, design, implement A/B tests — split tests, multivariate tests, growth experimentation",
                "category": "marketing",
                "params": {"element": "Element to test", "variants": "Number of variants", "hypothesis": "Test hypothesis"},
                "handler": self._skill_ab_test_setup
            },
            "analytics_tracking": {
                "description": "Set up, improve, audit analytics tracking — GA4, GTM, Mixpanel, Segment, conversion tracking",
                "category": "marketing",
                "params": {"platform": "ga4|gtm|mixpanel|segment", "action": "setup|audit|improve", "site": "Website URL"},
                "handler": self._skill_analytics_tracking
            },
            "churn_prevention": {
                "description": "Reduce churn, build cancellation flows, set up save offers, recover failed payments",
                "category": "marketing",
                "params": {"action": "audit|build_flow|save_offers|dunning", "product": "Product description"},
                "handler": self._skill_churn_prevention
            },
            "directory_submissions": {
                "description": "Submit product to startup, SaaS, AI, agent, MCP, no-code, review directories for backlinks",
                "category": "marketing",
                "params": {"product": "Product name/description", "directories": "Specific directories or 'all'"},
                "handler": self._skill_directory_submissions
            },
            "free_tool_strategy": {
                "description": "Plan, evaluate, build free tools for marketing — lead generation, SEO value, brand awareness",
                "category": "marketing",
                "params": {"tool_idea": "Tool concept", "goal": "leads|seo|brand", "audience": "Target audience"},
                "handler": self._skill_free_tool_strategy
            },
            "lead_magnets": {
                "description": "Create downloadable content lead magnets — ebooks, checklists, templates, guides",
                "category": "marketing",
                "params": {"type": "ebook|checklist|template|guide", "topic": "Lead magnet topic", "audience": "Target audience"},
                "handler": self._skill_lead_magnets
            },
            "page_cro": {
                "description": "Optimize any page for conversion — landing pages, pricing, feature pages, about pages",
                "category": "marketing",
                "params": {"page_url": "Page URL", "goal": "Conversion goal", "current_rate": "Current conversion rate"},
                "handler": self._skill_page_cro
            },
            "popup_cro": {
                "description": "Optimize popups, modals, overlays for conversion — timing, copy, design, triggers",
                "category": "marketing",
                "params": {"popup_type": "exit_intent|timed|scroll|click", "goal": "email|sale|signup", "current_performance": "Current metrics"},
                "handler": self._skill_popup_cro
            },
            "form_cro": {
                "description": "Optimize non-signup forms — lead capture, contact, demo request, application, checkout",
                "category": "marketing",
                "params": {"form_type": "lead|contact|demo|checkout", "fields": "Current fields", "conversion_rate": "Current rate"},
                "handler": self._skill_form_cro
            },
            "signup_flow_cro": {
                "description": "Optimize signup and registration flows — reduce friction, increase completion",
                "category": "marketing",
                "params": {"flow_type": "saas|mobile|social", "steps": "Number of steps", "drop_off": "Where users drop off"},
                "handler": self._skill_signup_flow_cro
            },
            "onboarding_cro": {
                "description": "Optimize user onboarding — first-run experience, activation, early retention",
                "category": "marketing",
                "params": {"product_type": "saas|app|platform", "activation_event": "Key activation action", "current_activation": "Current activation rate"},
                "handler": self._skill_onboarding_cro
            },
            "paywall_upgrade_cro": {
                "description": "Optimize in-app upgrade paywalls — pricing presentation, feature gating, trial offers",
                "category": "marketing",
                "params": {"product": "Product description", "tier_structure": "Current tiers", "upgrade_rate": "Current upgrade rate"},
                "handler": self._skill_paywall_upgrade_cro
            },
            "pricing_strategy": {
                "description": "Design and optimize pricing — value metrics, tier structure, packaging, positioning",
                "category": "marketing",
                "params": {"product": "Product description", "current_pricing": "Current pricing", "competitors": "Competitor pricing"},
                "handler": self._skill_pricing_strategy
            },
            "product_marketing_context": {
                "description": "Build product marketing context — positioning, messaging, competitive differentiation",
                "category": "marketing",
                "params": {"product": "Product description", "market": "Target market", "differentiators": "Key differentiators"},
                "handler": self._skill_product_marketing_context
            },
            "programmatic_seo": {
                "description": "Build programmatic SEO pages at scale — template pages, data-driven content",
                "category": "marketing",
                "params": {"template": "Page template", "data_source": "Data source", "target_keywords": "Target keywords"},
                "handler": self._skill_programmatic_seo
            },
            "referral_program": {
                "description": "Design and build referral programs — incentives, tracking, viral loops",
                "category": "marketing",
                "params": {"product": "Product description", "incentive_structure": "Reward structure", "target_k": "Viral coefficient goal"},
                "handler": self._skill_referral_program
            },
            "revops": {
                "description": "Revenue operations — pipeline management, forecasting, quota planning, compensation",
                "category": "marketing",
                "params": {"focus": "pipeline|forecasting|compensation|tools", "current_stack": "Current tools"},
                "handler": self._skill_revops
            },
            "sales_enablement": {
                "description": "Build sales collateral — battle cards, decks, one-pagers, demo scripts, objection handling",
                "category": "marketing",
                "params": {"collateral_type": "battle_card|deck|one_pager|demo_script", "product": "Product description"},
                "handler": self._skill_sales_enablement
            },
            "schema_markup": {
                "description": "Implement structured data — Schema.org markup, rich snippets, knowledge graph optimization",
                "category": "marketing",
                "params": {"page_type": "product|article|organization|faq", "content": "Page content"},
                "handler": self._skill_schema_markup
            },
            "site_architecture": {
                "description": "Design site architecture — URL structure, internal linking, content hierarchy, crawl optimization",
                "category": "marketing",
                "params": {"site_type": "ecommerce|saas|content|local", "pages": "Number of pages", "goal": "seo|conversion|both"},
                "handler": self._skill_site_architecture
            },
            "social_content": {
                "description": "Create social media content — posts, threads, carousels, video scripts for all platforms",
                "category": "marketing",
                "params": {"platform": "twitter|linkedin|instagram|tiktok|youtube", "content_type": "post|thread|carousel|script", "topic": "Content topic"},
                "handler": self._skill_social_content
            },
            "aso_audit": {
                "description": "Audit or optimize App Store or Google Play listing — keywords, screenshots, description, reviews",
                "category": "marketing",
                "params": {"app_url": "App Store or Play Store URL", "platform": "ios|android|both", "focus": "keywords|creative|reviews"},
                "handler": self._skill_aso_audit
            },
            "video": {
                "description": "Video marketing — scripts, thumbnails, editing guidance, platform optimization",
                "category": "marketing",
                "params": {"video_type": "explainer|tutorial|ad|vlog", "platform": "youtube|tiktok|instagram", "topic": "Video topic"},
                "handler": self._skill_video
            },
            
            # ==================== INFRASTRUCTURE ====================
            "auto_updater": {
                "description": "Automatically update OpenClaw and all installed skills once daily",
                "category": "infrastructure",
                "params": {"action": "check|update|schedule", "schedule": "cron expression"},
                "handler": self._skill_auto_updater
            },
            "heartbeat": {
                "description": "Design better HEARTBEAT.md files with adaptive cadence, safe checks, cron handoffs",
                "category": "infrastructure",
                "params": {"action": "design|check|update", "file": "HEARTBEAT.md path"},
                "handler": self._skill_heartbeat
            },
            "healthcheck": {
                "description": "Host security hardening — audits, firewall/SSH/update hardening, risk posture",
                "category": "infrastructure",
                "params": {"action": "audit|harden|check", "scope": "full|ssh|firewall|updates"},
                "handler": self._skill_healthcheck
            },
            "clawhub": {
                "description": "Use ClawHub CLI to search, install, update, publish agent skills",
                "category": "infrastructure",
                "params": {"action": "search|install|update|publish", "skill_name": "Skill name"},
                "handler": self._skill_clawhub
            },
            "free_ride": {
                "description": "Manage free AI models from OpenRouter — rank models, configure fallbacks",
                "category": "infrastructure",
                "params": {"action": "list|configure|rank", "model": "Model name"},
                "handler": self._skill_free_ride
            },
            "n8n_workflow_automation": {
                "description": "n8n integration — workflow design, node configuration, trigger setup",
                "category": "infrastructure",
                "params": {"action": "design|deploy|monitor", "workflow": "Workflow name or JSON"},
                "handler": self._skill_n8n_workflow
            },
            
            # ==================== TOOLS ====================
            "web_search": {
                "description": "Search the web using Brave Search API — fast research with titles, URLs, snippets",
                "category": "tools",
                "params": {"query": "Search query", "count": "Number of results (1-10)", "freshness": "pd|pw|pm|py|date_range"},
                "handler": self._skill_web_search
            },
            "web_fetch": {
                "description": "Fetch and extract readable content from a URL — HTML to markdown/text",
                "category": "tools",
                "params": {"url": "URL to fetch", "extract_mode": "markdown|text", "max_chars": "Maximum characters"},
                "handler": self._skill_web_fetch
            },
            "image": {
                "description": "Analyze images with vision model — single or batch analysis",
                "category": "tools",
                "params": {"image": "Image path or URL", "prompt": "Analysis prompt", "model": "Vision model"},
                "handler": self._skill_image
            },
            "pdf": {
                "description": "Analyze PDF documents — native analysis for Anthropic/Google, fallback for others",
                "category": "tools",
                "params": {"pdf": "PDF path or URL", "prompt": "Analysis prompt", "pages": "Page range"},
                "handler": self._skill_pdf
            },
            "weather": {
                "description": "Get current weather and forecasts — no API key needed",
                "category": "tools",
                "params": {"location": "City or location", "forecast": "current|forecast"},
                "handler": self._skill_weather
            },
            "video_frames": {
                "description": "Extract frames or short clips from videos using ffmpeg",
                "category": "tools",
                "params": {"video": "Video path", "output_dir": "Output directory", "interval": "Frame interval"},
                "handler": self._skill_video_frames
            },
            "peekaboo": {
                "description": "Capture and automate macOS UI with Peekaboo CLI",
                "category": "tools",
                "params": {"action": "capture|click|type|scroll", "app": "Target application", "coords": "Screen coordinates"},
                "handler": self._skill_peekaboo
            },
            "desktop_control": {
                "description": "Advanced desktop automation — mouse, keyboard, screen control",
                "category": "tools",
                "params": {"action": "move|click|type|screenshot", "x": "X coordinate", "y": "Y coordinate"},
                "handler": self._skill_desktop_control
            },
            "agent_phone_call": {
                "description": "Agent Phone Call — get a phone number, make/receive calls, complete tasks over phone",
                "category": "tools",
                "params": {"action": "call|receive|list_calls", "phone_number": "Phone number", "task": "Task description"},
                "handler": self._skill_agent_phone_call
            },
            "polymarket_trade": {
                "description": "Polymarket trading — view markets, place trades, manage positions",
                "category": "tools",
                "params": {"action": "list|trade|positions", "market": "Market ID", "amount": "Trade amount"},
                "handler": self._skill_polymarket_trade
            },
            "x_twitter": {
                "description": "X/Twitter operations — post, search, analyze, manage accounts",
                "category": "tools",
                "params": {"action": "post|search|analyze|schedule", "content": "Tweet content"},
                "handler": self._skill_x_twitter
            },
            "youtube_watcher": {
                "description": "YouTube operations — search, download, analyze, transcript extraction",
                "category": "tools",
                "params": {"action": "search|download|transcript|analyze", "video_id": "YouTube video ID"},
                "handler": self._skill_youtube_watcher
            },
            "openclaw_youtube_transcript": {
                "description": "Extract YouTube transcripts and ingest as knowledge for the agent",
                "category": "tools",
                "params": {"video_url": "YouTube URL", "save_to": "Where to save transcript"},
                "handler": self._skill_youtube_transcript
            },
            "imap_smtp_email": {
                "description": "IMAP/SMTP email operations — read, send, search, manage via direct protocols",
                "category": "tools",
                "params": {"action": "read|send|search|manage", "server": "IMAP/SMTP server"},
                "handler": self._skill_imap_smtp
            },
            "outlook_api": {
                "description": "Microsoft Outlook API — emails, calendar, contacts, tasks",
                "category": "tools",
                "params": {"action": "read_email|send_email|calendar|contacts", "to": "Recipient"},
                "handler": self._skill_outlook_api
            },
            "typeform": {
                "description": "Typeform API — create forms, manage responses, analyze data",
                "category": "tools",
                "params": {"action": "create|responses|analyze", "form_id": "Form ID"},
                "handler": self._skill_typeform
            },
            "microsoft_excel": {
                "description": "Microsoft Excel operations — create, edit, analyze spreadsheets",
                "category": "tools",
                "params": {"action": "create|edit|analyze|formula", "file_path": "Excel file path"},
                "handler": self._skill_microsoft_excel
            },
            "shopify": {
                "description": "Shopify operations — products, orders, customers, store management",
                "category": "tools",
                "params": {"action": "products|orders|customers|store", "store": "Store domain"},
                "handler": self._skill_shopify
            },
            "discord": {
                "description": "Discord operations — messages, channels, webhooks, server management",
                "category": "tools",
                "params": {"action": "send|manage|webhook", "channel_id": "Channel ID"},
                "handler": self._skill_discord
            },
            "answeroverflow": {
                "description": "Search indexed Discord community discussions via Answer Overflow",
                "category": "tools",
                "params": {"query": "Search query", "community": "Discord community"},
                "handler": self._skill_answeroverflow
            },
            "multi_search_engine": {
                "description": "Multi-search across Google, Bing, DuckDuckGo, Brave simultaneously",
                "category": "tools",
                "params": {"query": "Search query", "engines": "google|bing|duckduckgo|brave", "count": "Results per engine"},
                "handler": self._skill_multi_search
            },
            "humanizer": {
                "description": "Remove signs of AI-generated writing — detect and fix inflated symbolism, promotional language, etc.",
                "category": "tools",
                "params": {"text": "Text to humanize", "level": "light|medium|heavy"},
                "handler": self._skill_humanizer
            },
            
            # ==================== CRO / OPTIMIZATION ====================
            "ui_ux_pro_max": {
                "description": "UI/UX professional optimization — design review, accessibility, conversion optimization",
                "category": "cro",
                "params": {"url": "Website or app URL", "focus": "design|accessibility|conversion|all"},
                "handler": self._skill_ui_ux_pro_max
            },
            "laser_browser": {
                "description": "Laser-focused browser automation — precise element targeting, form filling, data extraction",
                "category": "cro",
                "params": {"url": "Target URL", "task": "Task description", "data_to_extract": "Data points to extract"},
                "handler": self._skill_laser_browser
            },
        }
    
    # ============= SKILL HANDLERS =============
    
    def _run_command(self, cmd: str, **kwargs) -> Dict:
        """Execute a shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 300),
                cwd=kwargs.get("cwd")
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "command": cmd}
        except Exception as e:
            return {"success": False, "error": str(e), "command": cmd}
    
    def _read_file(self, path: str, limit: int = 1000) -> str:
        """Read file contents"""
        try:
            p = Path(path).expanduser()
            with open(p, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()[:limit * 100]
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _write_file(self, path: str, content: str) -> bool:
        """Write content to file"""
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            return False
    
    def _skill_code(self, **params) -> Dict:
        """Code development skill"""
        task = params.get("task", "")
        language = params.get("language", "")
        
        # Return guidance for the LLM
        return {
            "skill": "code",
            "guidance": f"You are an expert {language} developer. Follow these steps:",
            "steps": [
                "1. Plan: Break down the task into components",
                "2. Implement: Write clean, documented code",
                "3. Verify: Run tests and check for errors",
                "4. Review: Ensure code quality and best practices",
            ],
            "best_practices": [
                "Use GitNexus for impact analysis before editing",
                "Test in isolation before integration",
                "Document all functions and classes",
                "Handle edge cases and errors",
            ],
            "tools_available": ["read_file", "write_file", "edit_file", "exec", "gitnexus"],
            "task": task
        }
    
    def _skill_github(self, **params) -> Dict:
        """GitHub CLI operations"""
        command = params.get("command", "")
        args = params.get("args", "")
        return self._run_command(f"gh {command} {args}")
    
    def _skill_gh_issues(self, **params) -> Dict:
        """GitHub issues automation"""
        repo = params.get("repo", "")
        label = params.get("label", "")
        limit = params.get("limit", 5)
        return self._run_command(f"gh issue list --repo {repo} --label {label} --limit {limit} --json number,title,body,labels")
    
    def _skill_gitnexus(self, **params) -> Dict:
        """Code intelligence"""
        repo_path = params.get("repo_path", ".")
        action = params.get("action", "impact")
        target = params.get("target", "")
        
        # Check if gitnexus is available
        gitnexus_path = Path.home() / "gitnexus"
        if not (gitnexus_path / "gitnexus_impact.py").exists():
            return {
                "skill": "gitnexus",
                "error": "GitNexus not found. Clone from https://github.com/abhigyanpatwari/GitNexus",
                "available": False
            }
        
        return {
            "skill": "gitnexus",
            "guidance": f"Run gitnexus_{action}() on {target} in {repo_path}",
            "command": f"cd {repo_path} && python3 ~/gitnexus/gitnexus_{action}.py --target {target}",
            "available": True
        }
    
    def _skill_mcporter(self, **params) -> Dict:
        """MCP server management"""
        action = params.get("action", "list")
        server = params.get("server", "")
        
        if action == "list":
            return self._run_command("mcporter list")
        elif action == "call":
            tool = params.get("tool", "")
            tool_params = params.get("params", "")
            return self._run_command(f'mcporter call {server} {tool} --params \'{json.dumps(tool_params)}\'')
        else:
            return {"skill": "mcporter", "action": action, "status": "not_implemented"}
    
    def _skill_agent_browser(self, **params) -> Dict:
        """Browser automation"""
        url = params.get("url", "")
        action = params.get("action", "navigate")
        
        # Return guidance for browser automation
        return {
            "skill": "agent_browser",
            "guidance": "Use the browser tool to automate web interactions",
            "url": url,
            "action": action,
            "selector": params.get("selector", ""),
            "tools_available": ["browser.navigate", "browser.snapshot", "browser.click", "browser.type"]
        }
    
    def _skill_session_logs(self, **params) -> Dict:
        """Session log analysis"""
        query = params.get("query", "")
        filter_expr = params.get("filter", "")
        return self._run_command(f'openclaw session-logs list | jq \'{filter_expr or "."}\'')
    
    def _skill_skill_creator(self, **params) -> Dict:
        """Create new skills"""
        name = params.get("name", "")
        description = params.get("description", "")
        
        skill_dir = Path.home() / ".openclaw" / "workspace" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        skill_md = skill_dir / "SKILL.md"
        content = f"""# {name}

## Description

{description}

## Usage

```bash
# How to use this skill
```

## Parameters

- `param1`: Description of parameter 1
- `param2`: Description of parameter 2

## Examples

```bash
# Example usage
```

## Notes

Add any important notes or caveats here.
"""
        skill_md.write_text(content)
        
        return {
            "skill": "skill_creator",
            "created": str(skill_dir),
            "name": name,
            "next_step": f"Edit {skill_dir}/SKILL.md to add implementation details"
        }
    
    def _skill_data_analysis(self, **params) -> Dict:
        """Data analysis"""
        data = params.get("data", "")
        analysis_type = params.get("analysis_type", "python")
        goal = params.get("goal", "")
        
        return {
            "skill": "data_analysis",
            "guidance": "Perform rigorous data analysis with decision brief format",
            "format": """
ANSWER: [the finding]
EVIDENCE: [the data]
CONFIDENCE: [high/medium/low]
CAVEATS: [limitations]
RECOMMENDATION: [next action]
""",
            "data": data,
            "analysis_type": analysis_type,
            "goal": goal
        }
    
    def _skill_gmail(self, **params) -> Dict:
        """Gmail operations"""
        action = params.get("action", "read")
        return {
            "skill": "gmail",
            "action": action,
            "guidance": f"Use Gmail API to {action} emails. Configure via `vivid auth add gmail`",
            "requires": "Google OAuth credentials"
        }
    
    def _skill_google_meet(self, **params) -> Dict:
        """Google Meet"""
        action = params.get("action", "create")
        return {
            "skill": "google_meet",
            "action": action,
            "guidance": f"Use Google Meet API to {action} meetings"
        }
    
    def _skill_google_slides(self, **params) -> Dict:
        """Google Slides"""
        action = params.get("action", "create")
        return {
            "skill": "google_slides",
            "action": action,
            "guidance": f"Use Google Slides API to {action} presentations"
        }
    
    def _skill_google_workspace_admin(self, **params) -> Dict:
        """Google Workspace Admin"""
        action = params.get("action", "list_users")
        return {
            "skill": "google_workspace_admin",
            "action": action,
            "guidance": f"Use Google Workspace Admin SDK to {action}"
        }
    
    def _skill_apple_notes(self, **params) -> Dict:
        """Apple Notes"""
        action = params.get("action", "create")
        title = params.get("title", "")
        content = params.get("content", "")
        
        if action == "create":
            # Use osascript or memo CLI
            return self._run_command(f'memo create "{title}" "{content}"')
        return {
            "skill": "apple_notes",
            "action": action,
            "title": title
        }
    
    def _skill_notion(self, **params) -> Dict:
        """Notion"""
        action = params.get("action", "create_page")
        return {
            "skill": "notion",
            "action": action,
            "guidance": f"Use Notion API to {action}. Requires integration token."
        }
    
    def _skill_calendly(self, **params) -> Dict:
        """Calendly"""
        action = params.get("action", "list_events")
        return {
            "skill": "calendly",
            "action": action,
            "guidance": f"Use Calendly API to {action}. Requires OAuth."
        }
    
    def _skill_api_gateway(self, **params) -> Dict:
        """API Gateway"""
        service = params.get("service", "")
        action = params.get("action", "")
        return {
            "skill": "api_gateway",
            "service": service,
            "action": action,
            "guidance": f"Use Maton.ai API Gateway for {service}. Requires OAuth connection."
        }
    
    def _skill_telegram(self, **params) -> Dict:
        """Telegram"""
        action = params.get("action", "send")
        return {
            "skill": "telegram",
            "action": action,
            "guidance": "Use Telegram Bot API. Requires bot token from @BotFather"
        }
    
    def _skill_copywriting(self, **params) -> Dict:
        """Copywriting"""
        page_type = params.get("page_type", "homepage")
        product = params.get("product", "")
        tone = params.get("tone", "professional")
        
        return {
            "skill": "copywriting",
            "page_type": page_type,
            "product": product,
            "tone": tone,
            "guidance": f"Write compelling {page_type} copy for {product} in a {tone} tone",
            "framework": "AIDA (Attention, Interest, Desire, Action) or PAS (Problem, Agitate, Solution)"
        }
    
    def _skill_ad_creative(self, **params) -> Dict:
        """Ad creative"""
        platform = params.get("platform", "facebook")
        product = params.get("product", "")
        variations = params.get("variations", 3)
        
        return {
            "skill": "ad_creative",
            "platform": platform,
            "product": product,
            "variations": variations,
            "guidance": f"Generate {variations} ad creative variations for {platform}",
            "elements": ["headlines", "descriptions", "primary_text", "CTAs"]
        }
    
    def _skill_email_sequence(self, **params) -> Dict:
        """Email sequence"""
        sequence_type = params.get("sequence_type", "welcome")
        emails = params.get("emails", 5)
        product = params.get("product", "")
        
        return {
            "skill": "email_sequence",
            "sequence_type": sequence_type,
            "emails": emails,
            "product": product,
            "guidance": f"Create {emails}-email {sequence_type} sequence for {product}"
        }
    
    def _skill_cold_email(self, **params) -> Dict:
        """Cold email"""
        target = params.get("target", "")
        offer = params.get("offer", "")
        followups = params.get("followups", 3)
        
        return {
            "skill": "cold_email",
            "target": target,
            "offer": offer,
            "followups": followups,
            "guidance": f"Write cold email sequence targeting {target} with {followups} follow-ups",
            "framework": "Personalized opener → Value proposition → Soft CTA → Follow-up sequence"
        }
    
    def _skill_seo_audit(self, **params) -> Dict:
        """SEO audit"""
        url = params.get("url", "")
        depth = params.get("depth", "full")
        
        return {
            "skill": "seo_audit",
            "url": url,
            "depth": depth,
            "guidance": f"Perform {depth} SEO audit of {url}",
            "checks": [
                "Technical: crawlability, indexability, speed, mobile-friendliness",
                "On-page: titles, meta, headings, content quality, internal links",
                "Off-page: backlinks, domain authority, brand mentions",
                "Content: keyword strategy, content gaps, cannibalization"
            ]
        }
    
    def _skill_ai_seo(self, **params) -> Dict:
        """AI SEO optimization"""
        content = params.get("content", "")
        target_ai = params.get("target_ai", "chatgpt")
        
        return {
            "skill": "ai_seo",
            "target_ai": target_ai,
            "guidance": f"Optimize content for {target_ai} AI search visibility",
            "tactics": [
                "Structure content with clear questions and direct answers",
                "Use schema markup for entities and relationships",
                "Build topical authority with comprehensive coverage",
                "Get cited in authoritative sources"
            ]
        }
    
    def _skill_content_strategy(self, **params) -> Dict:
        """Content strategy"""
        niche = params.get("niche", "")
        goals = params.get("goals", "")
        timeline = params.get("timeline", "12 months")
        
        return {
            "skill": "content_strategy",
            "niche": niche,
            "goals": goals,
            "timeline": timeline,
            "guidance": f"Develop {timeline} content strategy for {niche}",
            "deliverables": [
                "Content pillars and topic clusters",
                "Editorial calendar",
                "Content distribution strategy",
                "Performance metrics and KPIs"
            ]
        }
    
    def _skill_community_marketing(self, **params) -> Dict:
        """Community marketing"""
        platform = params.get("platform", "discord")
        goal = params.get("goal", "engagement")
        
        return {
            "skill": "community_marketing",
            "platform": platform,
            "goal": goal,
            "guidance": f"Build and grow {platform} community focused on {goal}",
            "tactics": [
                "Create valuable content and resources",
                "Engage consistently with members",
                "Build brand advocates and evangelists",
                "Foster word-of-mouth and organic growth"
            ]
        }
    
    def _skill_competitor_profiling(self, **params) -> Dict:
        """Competitor profiling"""
        urls = params.get("urls", [])
        depth = params.get("depth", "deep")
        
        return {
            "skill": "competitor_profiling",
            "urls": urls,
            "depth": depth,
            "guidance": f"Perform {depth} competitor analysis",
            "framework": [
                "Product features and positioning",
                "Pricing strategy and packaging",
                "Marketing channels and messaging",
                "Strengths, weaknesses, opportunities, threats"
            ]
        }
    
    def _skill_competitor_alternatives(self, **params) -> Dict:
        """Competitor alternatives"""
        product = params.get("product", "")
        competitors = params.get("competitors", [])
        format_type = params.get("format", "vs")
        
        return {
            "skill": "competitor_alternatives",
            "product": product,
            "competitors": competitors,
            "format": format_type,
            "guidance": f"Create {format_type} comparison pages for {product} vs {competitors}"
        }
    
    def _skill_customer_research(self, **params) -> Dict:
        """Customer research"""
        source = params.get("source", "interviews")
        topic = params.get("topic", "")
        
        return {
            "skill": "customer_research",
            "source": source,
            "topic": topic,
            "guidance": f"Conduct {source} research on {topic}",
            "methods": [
                "Customer interviews and surveys",
                "Support ticket analysis",
                "Reddit and forum mining",
                "Review analysis (G2, Capterra, etc.)",
                "Jobs-to-be-done framework"
            ]
        }
    
    def _skill_ab_test_setup(self, **params) -> Dict:
        """A/B test setup"""
        element = params.get("element", "")
        variants = params.get("variants", 2)
        hypothesis = params.get("hypothesis", "")
        
        return {
            "skill": "ab_test_setup",
            "element": element,
            "variants": variants,
            "hypothesis": hypothesis,
            "guidance": f"Design A/B test for {element} with {variants} variants",
            "framework": [
                "Hypothesis: If [change], then [metric] will [direction] because [reason]",
                "Primary metric and secondary metrics",
                "Sample size calculation",
                "Test duration and statistical power",
                "Stopping rules and winner selection"
            ]
        }
    
    def _skill_analytics_tracking(self, **params) -> Dict:
        """Analytics tracking"""
        platform = params.get("platform", "ga4")
        action = params.get("action", "setup")
        site = params.get("site", "")
        
        return {
            "skill": "analytics_tracking",
            "platform": platform,
            "action": action,
            "site": site,
            "guidance": f"{action} {platform} tracking for {site}",
            "components": [
                "Event tracking plan",
                "Conversion funnels",
                "Attribution modeling",
                "Custom dimensions and metrics",
                "Data validation and QA"
            ]
        }
    
    def _skill_churn_prevention(self, **params) -> Dict:
        """Churn prevention"""
        action = params.get("action", "audit")
        product = params.get("product", "")
        
        return {
            "skill": "churn_prevention",
            "action": action,
            "product": product,
            "guidance": f"{action} churn prevention for {product}",
            "tactics": [
                "Cancellation flow with save offers",
                "Dunning management for failed payments",
                "Win-back email sequences",
                "Exit surveys and feedback collection",
                "Proactive health scoring"
            ]
        }
    
    def _skill_directory_submissions(self, **params) -> Dict:
        """Directory submissions"""
        product = params.get("product", "")
        directories = params.get("directories", "all")
        
        return {
            "skill": "directory_submissions",
            "product": product,
            "directories": directories,
            "guidance": f"Submit {product} to directories for backlinks and discovery",
            "directories_list": [
                "Product Hunt, BetaList, Futurepedia",
                "AI directories: TheresAnAIForThat, AI Tools Directory",
                "SaaS directories: SaaSHub, Capterra, G2",
                "Developer directories: GitHub Trending, Devpost",
                "Niche directories based on product category"
            ]
        }
    
    def _skill_free_tool_strategy(self, **params) -> Dict:
        """Free tool strategy"""
        tool_idea = params.get("tool_idea", "")
        goal = params.get("goal", "leads")
        
        return {
            "skill": "free_tool_strategy",
            "tool_idea": tool_idea,
            "goal": goal,
            "guidance": f"Design free tool strategy: {tool_idea} for {goal}",
            "framework": [
                "Identify painful, frequent problem",
                "Build minimum viable tool",
                "Gate advanced features or require email",
                "Distribute through SEO and communities",
                "Convert tool users to product users"
            ]
        }
    
    def _skill_lead_magnets(self, **params) -> Dict:
        """Lead magnets"""
        type_ = params.get("type", "ebook")
        topic = params.get("topic", "")
        
        return {
            "skill": "lead_magnets",
            "type": type_,
            "topic": topic,
            "guidance": f"Create {type_} lead magnet about {topic}",
            "types": [
                "Ebooks and guides",
                "Checklists and templates",
                "Calculators and tools",
                "Webinars and courses",
                "Research reports and data"
            ]
        }
    
    def _skill_page_cro(self, **params) -> Dict:
        """Page CRO"""
        page_url = params.get("page_url", "")
        goal = params.get("goal", "conversion")
        
        return {
            "skill": "page_cro",
            "page_url": page_url,
            "goal": goal,
            "guidance": f"Optimize {page_url} for {goal}",
            "elements": [
                "Headline and value proposition",
                "Social proof and trust signals",
                "Call-to-action clarity and prominence",
                "Form optimization and friction reduction",
                "Visual hierarchy and readability"
            ]
        }
    
    def _skill_popup_cro(self, **params) -> Dict:
        """Popup CRO"""
        popup_type = params.get("popup_type", "exit_intent")
        goal = params.get("goal", "email")
        
        return {
            "skill": "popup_cro",
            "popup_type": popup_type,
            "goal": goal,
            "guidance": f"Optimize {popup_type} popup for {goal} capture",
            "best_practices": [
                "Don't show immediately — wait for engagement",
                "Clear value proposition in headline",
                "Minimal form fields (usually just email)",
                "Easy dismiss with escape or click outside",
                "Mobile-friendly design"
            ]
        }
    
    def _skill_form_cro(self, **params) -> Dict:
        """Form CRO"""
        form_type = params.get("form_type", "lead")
        fields = params.get("fields", [])
        
        return {
            "skill": "form_cro",
            "form_type": form_type,
            "fields": fields,
            "guidance": f"Optimize {form_type} form with fields: {fields}",
            "principles": [
                "Minimize fields — only ask what's necessary",
                "Use multi-step forms for complex inputs",
                "Inline validation to prevent errors",
                "Progress indicators for long forms",
                "Smart defaults and autofill"
            ]
        }
    
    def _skill_signup_flow_cro(self, **params) -> Dict:
        """Signup flow CRO"""
        flow_type = params.get("flow_type", "saas")
        steps = params.get("steps", 3)
        
        return {
            "skill": "signup_flow_cro",
            "flow_type": flow_type,
            "steps": steps,
            "guidance": f"Optimize {flow_type} signup flow with {steps} steps",
            "tactics": [
                "Social signup options (Google, GitHub, etc.)",
                "Progressive profiling — ask for info over time",
                "Clear value preview before signup",
                "Remove unnecessary verification steps",
                "Welcome and activation sequence post-signup"
            ]
        }
    
    def _skill_onboarding_cro(self, **params) -> Dict:
        """Onboarding CRO"""
        product_type = params.get("product_type", "saas")
        activation_event = params.get("activation_event", "")
        
        return {
            "skill": "onboarding_cro",
            "product_type": product_type,
            "activation_event": activation_event,
            "guidance": f"Optimize {product_type} onboarding for {activation_event} activation",
            "strategies": [
                "Personalized welcome based on signup source",
                "Guided product tour with key features",
                "Quick wins and early value delivery",
                "Checklists and progress tracking",
                "Contextual help and tooltips"
            ]
        }
    
    def _skill_paywall_upgrade_cro(self, **params) -> Dict:
        """Paywall upgrade CRO"""
        product = params.get("product", "")
        tier_structure = params.get("tier_structure", [])
        
        return {
            "skill": "paywall_upgrade_cro",
            "product": product,
            "tier_structure": tier_structure,
            "guidance": f"Optimize {product} paywall for upgrades",
            "tactics": [
                "Feature-gated trial with clear upgrade path",
                "Usage-based triggers (e.g., 'You've used 80% of free tier')",
                "Side-by-side tier comparison",
                "Annual discount and savings highlight",
                "Social proof from similar users"
            ]
        }
    
    def _skill_pricing_strategy(self, **params) -> Dict:
        """Pricing strategy"""
        product = params.get("product", "")
        current_pricing = params.get("current_pricing", "")
        
        return {
            "skill": "pricing_strategy",
            "product": product,
            "current_pricing": current_pricing,
            "guidance": f"Design pricing strategy for {product}",
            "frameworks": [
                "Value-based pricing (perceived value)",
                "Competitor-based pricing (market position)",
                "Cost-plus pricing (margin requirements)",
                "Freemium and tiered strategies",
                "Usage-based and seat-based models"
            ]
        }
    
    def _skill_product_marketing_context(self, **params) -> Dict:
        """Product marketing context"""
        product = params.get("product", "")
        market = params.get("market", "")
        
        return {
            "skill": "product_marketing_context",
            "product": product,
            "market": market,
            "guidance": f"Build product marketing context for {product} in {market}",
            "deliverables": [
                "Positioning statement and differentiation",
                "Ideal customer profile and personas",
                "Key messaging and narrative",
                "Competitive battle cards",
                "Launch and GTM strategy"
            ]
        }
    
    def _skill_programmatic_seo(self, **params) -> Dict:
        """Programmatic SEO"""
        template = params.get("template", "")
        data_source = params.get("data_source", "")
        
        return {
            "skill": "programmatic_seo",
            "template": template,
            "data_source": data_source,
            "guidance": f"Build programmatic SEO pages from {data_source}",
            "approach": [
                "Define page template with variables",
                "Source structured data (API, database, scraping)",
                "Generate pages at scale",
                "Internal linking architecture",
                "Monitor and optimize performance"
            ]
        }
    
    def _skill_referral_program(self, **params) -> Dict:
        """Referral program"""
        product = params.get("product", "")
        incentive_structure = params.get("incentive_structure", "")
        
        return {
            "skill": "referral_program",
            "product": product,
            "incentive_structure": incentive_structure,
            "guidance": f"Design referral program for {product}",
            "elements": [
                "Incentive structure (dual-sided, tiered, gamified)",
                "Referral tracking and attribution",
                "Sharing mechanisms and viral loops",
                "Onboarding for referred users",
                "Optimization and A/B testing"
            ]
        }
    
    def _skill_revops(self, **params) -> Dict:
        """Revenue operations"""
        focus = params.get("focus", "pipeline")
        
        return {
            "skill": "revops",
            "focus": focus,
            "guidance": f"Optimize revenue operations: {focus}",
            "areas": [
                "Pipeline management and forecasting",
                "Quota planning and territory design",
                "Compensation and SPIF design",
                "Tool stack integration (CRM, marketing, support)",
                "Data quality and attribution"
            ]
        }
    
    def _skill_sales_enablement(self, **params) -> Dict:
        """Sales enablement"""
        collateral_type = params.get("collateral_type", "battle_card")
        product = params.get("product", "")
        
        return {
            "skill": "sales_enablement",
            "collateral_type": collateral_type,
            "product": product,
            "guidance": f"Create {collateral_type} for {product}",
            "types": [
                "Battle cards (competitive positioning)",
                "Sales decks and presentations",
                "One-pagers and solution briefs",
                "Demo scripts and talk tracks",
                "Objection handling guides"
            ]
        }
    
    def _skill_schema_markup(self, **params) -> Dict:
        """Schema markup"""
        page_type = params.get("page_type", "product")
        content = params.get("content", "")
        
        return {
            "skill": "schema_markup",
            "page_type": page_type,
            "guidance": f"Implement Schema.org markup for {page_type} pages",
            "types": [
                "Product schema (offers, reviews, availability)",
                "Article schema (headline, author, date)",
                "Organization schema (logo, contact, social)",
                "FAQ schema (questions and answers)",
                "Breadcrumb schema (navigation hierarchy)"
            ]
        }
    
    def _skill_site_architecture(self, **params) -> Dict:
        """Site architecture"""
        site_type = params.get("site_type", "saas")
        pages = params.get("pages", 50)
        
        return {
            "skill": "site_architecture",
            "site_type": site_type,
            "pages": pages,
            "guidance": f"Design site architecture for {site_type} with {pages} pages",
            "components": [
                "URL structure and hierarchy",
                "Internal linking strategy",
                "Content categorization and taxonomy",
                "Navigation and user flows",
                "Crawl optimization and XML sitemaps"
            ]
        }
    
    def _skill_social_content(self, **params) -> Dict:
        """Social content"""
        platform = params.get("platform", "twitter")
        content_type = params.get("content_type", "post")
        topic = params.get("topic", "")
        
        return {
            "skill": "social_content",
            "platform": platform,
            "content_type": content_type,
            "topic": topic,
            "guidance": f"Create {content_type} for {platform} about {topic}",
            "best_practices": [
                "Hook in first 3 seconds/lines",
                "Use platform-native formats (threads, carousels, reels)",
                "Include clear CTA",
                "Optimize for shareability",
                "Post at optimal times for audience"
            ]
        }
    
    def _skill_aso_audit(self, **params) -> Dict:
        """ASO audit"""
        app_url = params.get("app_url", "")
        platform = params.get("platform", "both")
        
        return {
            "skill": "aso_audit",
            "app_url": app_url,
            "platform": platform,
            "guidance": f"Perform ASO audit for {platform}",
            "checks": [
                "Keyword optimization (title, subtitle, description)",
                "Screenshot and video preview optimization",
                "Rating and review management",
                "Conversion rate optimization",
                "Competitor keyword analysis"
            ]
        }
    
    def _skill_video(self, **params) -> Dict:
        """Video marketing"""
        video_type = params.get("video_type", "explainer")
        platform = params.get("platform", "youtube")
        
        return {
            "skill": "video",
            "video_type": video_type,
            "platform": platform,
            "guidance": f"Create {video_type} video for {platform}",
            "elements": [
                "Script and storyboard",
                "Thumbnail design and optimization",
                "Title, description, and tags (SEO)",
                "Call-to-action and end screens",
                "Distribution and promotion strategy"
            ]
        }
    
    def _skill_auto_updater(self, **params) -> Dict:
        """Auto updater"""
        action = params.get("action", "check")
        
        return {
            "skill": "auto_updater",
            "action": action,
            "guidance": f"Manage automatic updates: {action}",
            "setup": [
                "Configure cron for daily checks",
                "Set up update notifications",
                "Test updates in staging first",
                "Rollback plan for failed updates"
            ]
        }
    
    def _skill_heartbeat(self, **params) -> Dict:
        """Heartbeat"""
        action = params.get("action", "design")
        
        return {
            "skill": "heartbeat",
            "action": action,
            "guidance": f"Manage heartbeat system: {action}",
            "features": [
                "Adaptive cadence based on activity",
                "Safe checks that don't disrupt workflows",
                "Cron handoffs for precise scheduling",
                "Alerts for urgent conditions",
                "Status reporting and logging"
            ]
        }
    
    def _skill_healthcheck(self, **params) -> Dict:
        """Healthcheck"""
        action = params.get("action", "audit")
        scope = params.get("scope", "full")
        
        return {
            "skill": "healthcheck",
            "action": action,
            "scope": scope,
            "guidance": f"Perform {scope} security {action}",
            "areas": [
                "SSH hardening (keys, configs, access)",
                "Firewall rules and port exposure",
                "System updates and patches",
                "User permissions and access control",
                "Log monitoring and intrusion detection"
            ]
        }
    
    def _skill_clawhub(self, **params) -> Dict:
        """ClawHub"""
        action = params.get("action", "search")
        skill_name = params.get("skill_name", "")
        
        if action == "search":
            return self._run_command(f"clawhub search {skill_name}")
        elif action == "install":
            return self._run_command(f"clawhub install {skill_name}")
        elif action == "update":
            return self._run_command(f"clawhub update {skill_name}")
        
        return {"skill": "clawhub", "action": action}
    
    def _skill_free_ride(self, **params) -> Dict:
        """Free Ride"""
        action = params.get("action", "list")
        
        return {
            "skill": "free_ride",
            "action": action,
            "guidance": "Manage free AI models from OpenRouter",
            "models": [
                "HuggingFaceH4/zephyr-7b-beta",
                "meta-llama/Llama-2-7b-chat-hf",
                "mistralai/Mistral-7B-Instruct-v0.1",
                "google/gemma-7b-it"
            ]
        }
    
    def _skill_n8n_workflow(self, **params) -> Dict:
        """n8n workflow"""
        action = params.get("action", "design")
        workflow = params.get("workflow", "")
        
        return {
            "skill": "n8n_workflow_automation",
            "action": action,
            "guidance": f"{action} n8n workflow: {workflow}",
            "components": [
                "Trigger configuration (schedule, webhook, event)",
                "Node configuration and connections",
                "Error handling and retries",
                "Data transformation and mapping",
                "Testing and deployment"
            ]
        }
    
    def _skill_web_search(self, **params) -> Dict:
        """Web search"""
        from .tools import ToolRegistry
        tools = ToolRegistry(self.config)
        return tools.execute("web_search", params)
    
    def _skill_web_fetch(self, **params) -> Dict:
        """Web fetch"""
        from .tools import ToolRegistry
        tools = ToolRegistry(self.config)
        return tools.execute("web_fetch", params)
    
    def _skill_image(self, **params) -> Dict:
        """Image analysis"""
        image_path = params.get("image", "")
        prompt = params.get("prompt", "Describe this image")
        
        return {
            "skill": "image",
            "image": image_path,
            "prompt": prompt,
            "guidance": "Analyze image with vision model. Provide detailed description.",
            "note": "Use the model's vision capabilities directly"
        }
    
    def _skill_pdf(self, **params) -> Dict:
        """PDF analysis"""
        pdf_path = params.get("pdf", "")
        prompt = params.get("prompt", "Summarize this document")
        pages = params.get("pages", "")
        
        return {
            "skill": "pdf",
            "pdf": pdf_path,
            "prompt": prompt,
            "pages": pages,
            "guidance": "Analyze PDF document. Extract key information."
        }
    
    def _skill_weather(self, **params) -> Dict:
        """Weather"""
        location = params.get("location", "")
        forecast = params.get("forecast", "current")
        
        # Use wttr.in or Open-Meteo
        if forecast == "current":
            return self._run_command(f'curl -s "wttr.in/{location}?format=3"')
        else:
            return self._run_command(f'curl -s "wttr.in/{location}?format=v2"')
    
    def _skill_video_frames(self, **params) -> Dict:
        """Video frame extraction"""
        video = params.get("video", "")
        output_dir = params.get("output_dir", "frames")
        interval = params.get("interval", "1s")
        
        return self._run_command(f'ffmpeg -i "{video}" -vf "fps=1/{interval}" -q:v 2 "{output_dir}/frame_%04d.jpg"')
    
    def _skill_peekaboo(self, **params) -> Dict:
        """macOS UI automation"""
        action = params.get("action", "capture")
        app = params.get("app", "")
        
        return {
            "skill": "peekaboo",
            "action": action,
            "app": app,
            "guidance": f"Use Peekaboo CLI to {action} {app}",
            "requires": "macOS with Peekaboo installed"
        }
    
    def _skill_desktop_control(self, **params) -> Dict:
        """Desktop control"""
        action = params.get("action", "screenshot")
        x = params.get("x", 0)
        y = params.get("y", 0)
        
        if action == "screenshot":
            return self._run_command("screencapture -x screenshot.png")
        elif action == "move":
            return self._run_command(f"cliclick m:{x},{y}")
        elif action == "click":
            return self._run_command(f"cliclick c:{x},{y}")
        
        return {"skill": "desktop_control", "action": action}
    
    def _skill_agent_phone_call(self, **params) -> Dict:
        """Agent phone call"""
        action = params.get("action", "call")
        phone = params.get("phone_number", "")
        
        return {
            "skill": "agent_phone_call",
            "action": action,
            "phone": phone,
            "guidance": f"Use agent phone system to {action} {phone}",
            "requires": "Agent phone service subscription"
        }
    
    def _skill_polymarket_trade(self, **params) -> Dict:
        """Polymarket trading"""
        action = params.get("action", "list")
        market = params.get("market", "")
        
        return {
            "skill": "polymarket_trade",
            "action": action,
            "market": market,
            "guidance": f"Polymarket {action} for market {market}",
            "warning": "Trading involves risk. Not financial advice."
        }
    
    def _skill_x_twitter(self, **params) -> Dict:
        """X/Twitter"""
        action = params.get("action", "post")
        content = params.get("content", "")
        
        if action == "post":
            return self._run_command(f'twitpost "{content}"')
        
        return {
            "skill": "x_twitter",
            "action": action,
            "guidance": f"X/Twitter {action}"
        }
    
    def _skill_youtube_watcher(self, **params) -> Dict:
        """YouTube operations"""
        action = params.get("action", "search")
        video_id = params.get("video_id", "")
        
        if action == "download":
            return self._run_command(f"yt-dlp 'https://youtube.com/watch?v={video_id}'")
        elif action == "transcript":
            return self._run_command(f"yt-dlp --write-auto-sub --skip-download 'https://youtube.com/watch?v={video_id}'")
        
        return {
            "skill": "youtube_watcher",
            "action": action,
            "video_id": video_id
        }
    
    def _skill_youtube_transcript(self, **params) -> Dict:
        """YouTube transcript"""
        video_url = params.get("video_url", "")
        save_to = params.get("save_to", "")
        
        return self._run_command(f"yt-dlp --write-auto-sub --skip-download --sub-langs en '{video_url}' -o '{save_to}'")
    
    def _skill_imap_smtp(self, **params) -> Dict:
        """IMAP/SMTP email"""
        action = params.get("action", "read")
        server = params.get("server", "")
        
        return {
            "skill": "imap_smtp_email",
            "action": action,
            "server": server,
            "guidance": f"Use IMAP/SMTP for {action}. Configure server credentials."
        }
    
    def _skill_outlook_api(self, **params) -> Dict:
        """Outlook API"""
        action = params.get("action", "read_email")
        
        return {
            "skill": "outlook_api",
            "action": action,
            "guidance": f"Use Microsoft Graph API for Outlook {action}"
        }
    
    def _skill_typeform(self, **params) -> Dict:
        """Typeform"""
        action = params.get("action", "create")
        form_id = params.get("form_id", "")
        
        return {
            "skill": "typeform",
            "action": action,
            "form_id": form_id,
            "guidance": f"Typeform {action}"
        }
    
    def _skill_microsoft_excel(self, **params) -> Dict:
        """Microsoft Excel"""
        action = params.get("action", "create")
        file_path = params.get("file_path", "")
        
        return {
            "skill": "microsoft_excel",
            "action": action,
            "file_path": file_path,
            "guidance": f"Excel {action}: {file_path}"
        }
    
    def _skill_shopify(self, **params) -> Dict:
        """Shopify"""
        action = params.get("action", "products")
        store = params.get("store", "")
        
        return {
            "skill": "shopify",
            "action": action,
            "store": store,
            "guidance": f"Shopify {action} for store {store}"
        }
    
    def _skill_discord(self, **params) -> Dict:
        """Discord"""
        action = params.get("action", "send")
        channel_id = params.get("channel_id", "")
        
        return {
            "skill": "discord",
            "action": action,
            "channel_id": channel_id,
            "guidance": f"Discord {action} in channel {channel_id}"
        }
    
    def _skill_answeroverflow(self, **params) -> Dict:
        """Answer Overflow"""
        query = params.get("query", "")
        community = params.get("community", "")
        
        return {
            "skill": "answeroverflow",
            "query": query,
            "community": community,
            "guidance": f"Search Answer Overflow for '{query}' in {community}"
        }
    
    def _skill_multi_search(self, **params) -> Dict:
        """Multi-search engine"""
        query = params.get("query", "")
        engines = params.get("engines", "google|bing|duckduckgo|brave")
        count = params.get("count", 5)
        
        results = {}
        for engine in engines.split("|"):
            if engine == "brave":
                # Use web_search tool
                from .tools import ToolRegistry
                tools = ToolRegistry(self.config)
                results["brave"] = tools.execute("web_search", {"query": query, "count": count})
            else:
                results[engine] = {"status": f"Search via {engine} requires additional setup"}
        
        return {
            "skill": "multi_search_engine",
            "query": query,
            "engines": engines,
            "results": results
        }
    
    def _skill_humanizer(self, **params) -> Dict:
        """Humanizer"""
        text = params.get("text", "")
        level = params.get("level", "medium")
        
        return {
            "skill": "humanizer",
            "text_length": len(text),
            "level": level,
            "guidance": "Remove AI-generated patterns from text",
            "patterns_to_remove": [
                "Inflated symbolism and metaphors",
                "Promotional/salesy language",
                "Superficial -ing analyses",
                "Vague attributions ('many believe', 'some say')",
                "Em dash overuse",
                "Rule of three",
                "AI vocabulary words ('delve', 'tapestry', 'landscape')",
                "Negative parallelisms",
                "Excessive conjunctive phrases"
            ]
        }
    
    def _skill_ui_ux_pro_max(self, **params) -> Dict:
        """UI/UX Pro Max"""
        url = params.get("url", "")
        focus = params.get("focus", "all")
        
        return {
            "skill": "ui_ux_pro_max",
            "url": url,
            "focus": focus,
            "guidance": f"Perform comprehensive UI/UX {focus} analysis of {url}",
            "areas": [
                "Visual design and aesthetics",
                "Usability and user flows",
                "Accessibility (WCAG compliance)",
                "Performance and loading",
                "Mobile responsiveness",
                "Conversion optimization"
            ]
        }
    
    def _skill_laser_browser(self, **params) -> Dict:
        """Laser Browser"""
        url = params.get("url", "")
        task = params.get("task", "")
        
        return {
            "skill": "laser_browser",
            "url": url,
            "task": task,
            "guidance": f"Use precision browser automation for {task} on {url}",
            "features": [
                "Exact element targeting via multiple selectors",
                "Form filling with validation",
                "Data extraction with schema",
                "Session persistence",
                "Stealth mode and anti-detection"
            ]
        }
    
    # ============= PUBLIC API =============
    
    def list_skills(self) -> Dict[str, Dict]:
        """List all available skills"""
        return {
            name: {
                "description": info["description"],
                "category": info["category"],
                "params": info["params"]
            }
            for name, info in self.tools.items()
        }
    
    def execute(self, skill_name: str, **params) -> Dict:
        """Execute a skill with given parameters"""
        if skill_name not in self.tools:
            available = list(self.tools.keys())
            categories = {}
            for name, info in self.tools.items():
                cat = info["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(name)
            
            return {
                "error": f"Skill '{skill_name}' not found",
                "available_count": len(available),
                "categories": categories
            }
        
        skill = self.tools[skill_name]
        try:
            result = skill["handler"](**params)
            result["_skill"] = skill_name
            result["_category"] = skill["category"]
            return result
        except Exception as e:
            import traceback
            return {
                "error": str(e),
                "_skill": skill_name,
                "_traceback": traceback.format_exc()
            }
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get skills organized by category"""
        categories = {}
        for name, info in self.tools.items():
            cat = info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)
        return categories
    
    def search(self, query: str) -> List[Dict]:
        """Search skills by description"""
        query_lower = query.lower()
        results = []
        
        for name, info in self.tools.items():
            score = 0
            if query_lower in name.lower():
                score += 10
            if query_lower in info["description"].lower():
                score += 5
            for word in query_lower.split():
                if word in info["description"].lower():
                    score += 2
            
            if score > 0:
                results.append({
                    "name": name,
                    "description": info["description"],
                    "category": info["category"],
                    "score": score
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:20]
