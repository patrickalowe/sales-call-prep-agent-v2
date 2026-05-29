"""
Core agent logic for the Sales Call Prep Agent.

Runs a four-step workflow per briefing:
  1. plan_approach  -- decide the angle before generating
  2. gather_context -- organize what is known about the company
  3. generate_brief -- produce the full seven-section briefing
  4. review_brief   -- flag weak spots in the output

run_agent() is the main entry point. It runs all four steps and returns
a formatted markdown string ready to save.

Each step is a separate function so they can be read, tested, or swapped
out independently. The gather_context() step uses live web search so the
briefing is grounded in current, sourced information rather than the model's
training knowledge alone.
"""

from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

from prompts import (
    SYSTEM_PROMPT,
    PLANNING_PROMPT,
    CONTEXT_PROMPT,
    BRIEFING_PROMPT,
    REVIEW_PROMPT,
)

MODEL = "claude-sonnet-4-6"

# Anthropic's server-side web search tool. Claude runs the searches on
# Anthropic's infrastructure and folds the results (with sources) back into
# its answer. max_uses caps how many searches one briefing can trigger, which
# bounds both latency and cost.
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}

# Safety cap on the server-side tool loop, so a runaway search session can't
# spin forever. Each pause_turn is one resume.
_MAX_SEARCH_RESUMES = 8


def _call(client, prompt, max_tokens, tools=None):
    """Make an API call and return the combined text response.

    When `tools` includes the web search tool, Claude may pause mid-turn to run
    searches (stop_reason == "pause_turn"); we resume until it finishes. The
    response can contain several blocks (search calls, results, text), so we
    join every text block rather than reading only the first.
    """
    messages = [{"role": "user", "content": prompt}]

    for _ in range(_MAX_SEARCH_RESUMES + 1):
        kwargs = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = client.messages.create(**kwargs)

        if response.stop_reason == "pause_turn":
            # Server-side search loop hit its iteration limit. Append what we
            # have and re-send; the API resumes the search automatically.
            messages.append({"role": "assistant", "content": response.content})
            continue
        break

    return "".join(b.text for b in response.content if b.type == "text").strip()


def plan_approach(client, company_name, persona_title, notes):
    """Step 1: Plan the angle before generating the brief."""
    prompt = PLANNING_PROMPT.format(
        company_name=company_name,
        persona_title=persona_title,
        notes=notes or "None provided.",
    )
    return _call(client, prompt, max_tokens=400)


def gather_context(client, company_name, persona_title, plan):
    """Step 2: Research the company and persona using live web search.

    This is the step that grounds the brief in current reality (recent news,
    funding, leadership, product launches) instead of stale training data.
    """
    prompt = CONTEXT_PROMPT.format(
        company_name=company_name,
        persona_title=persona_title,
        plan=plan,
    )
    return _call(client, prompt, max_tokens=2000, tools=[WEB_SEARCH_TOOL])


def generate_brief(client, company_name, persona_title, notes, plan, context):
    """Step 3: Generate the full seven-section briefing."""
    prompt = BRIEFING_PROMPT.format(
        company_name=company_name,
        persona_title=persona_title,
        notes=notes or "None provided.",
        plan=plan,
        context=context,
    )
    return _call(client, prompt, max_tokens=3000)


def review_brief(client, brief):
    """Step 4: Flag weak spots in the generated output."""
    prompt = REVIEW_PROMPT.format(brief=brief)
    return _call(client, prompt, max_tokens=400)


def format_output(company_name, persona_title, brief, review):
    """Assemble the final markdown document with metadata and review notes."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# Sales Call Brief

**Company:** {company_name}
**Persona:** {persona_title}
**Generated:** {timestamp}

---

{brief}

---

## Agent Review Notes

{review}
"""


def save_output(content, company):
    """Save a finished brief to output/ as a timestamped markdown file.

    Shared by both the CLI (main.py) and the web app (app.py) so a briefing
    is saved the same way no matter which one generated it. Returns the path.
    """
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    slug = company.lower().replace(" ", "_").replace("/", "_").replace(".", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filepath = output_dir / f"{slug}_{timestamp}.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


def run_agent(company_name, persona_title, notes="", on_step=None):
    """
    Run the full four-step agent workflow and return formatted markdown.

    on_step is an optional callback that receives a status string at each step.
    main.py uses it to print progress without this module knowing about the UI.
    """
    def step(msg):
        if on_step:
            on_step(msg)

    client = Anthropic()

    step("Planning approach...")
    plan = plan_approach(client, company_name, persona_title, notes)

    step("Researching company (live web search)...")
    context = gather_context(client, company_name, persona_title, plan)

    step("Generating briefing...")
    brief = generate_brief(client, company_name, persona_title, notes, plan, context)

    step("Running self-check...")
    review = review_brief(client, brief)

    return format_output(company_name, persona_title, brief, review)
