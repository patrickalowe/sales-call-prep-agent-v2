# Sales Call Prep Agent

A Python tool that turns a company name, a prospect's job title, and a few optional notes into a structured pre-call briefing. It researches the account with live web search, so the brief reflects current news and not just the model's training data. Use it two ways: a terminal version that saves the brief as a timestamped markdown file, or a local website with a simple form.

---

## Overview

I spent several years in sales before moving into AI-enabled workflows. Before every discovery call, prep was manual and inconsistent. Sometimes I spent twenty minutes researching. Sometimes I walked in cold. The quality of preparation depended entirely on how much time I had that day.

This tool solves that. Give it a company name and a title, and it returns a briefing that tells you what the person likely cares about, what questions will open a real conversation, and what you do not yet know and should verify before the call. That last part matters as much as the rest.

---

## What it produces

| Section | What it contains |
|---|---|
| **Account** | What the company does, who they serve, and their current situation |
| **Persona** | What this role owns, cares about day-to-day, and is measured on |
| **Likely Priorities** | What this person is probably focused on right now |
| **Potential Pain Points** | 3 to 5 role-specific problems, each with a commercial why-it-matters line |
| **Discovery Questions** | 5 open-ended questions tailored to this persona |
| **Sample Outreach** | A cold email or LinkedIn message under 100 words |
| **Assumptions and Gaps** | What is uncertain and should be verified before the call |

---

## Example output

The following is excerpted from a real briefing generated for a VP of Sales at Capital One. [See the full output here](output/example_briefing.md), including the Agent Review Notes at the end.

---

### Persona
This VP likely owns revenue or portfolio targets across a distributed team of AEs or relationship managers, with day-to-day focus on pipeline health, forecast accuracy, and whether their reps are showing up to customer conversations ready to have the right discussion. They are measured on quota attainment and team productivity, which means rep ramp time and call quality inconsistency are personal problems, not abstract ones.

### Potential Pain Points
- **Inconsistent call preparation across the team.** When reps do their own research differently, some show up sharp and some show up generic, and the VP has no lever to fix that at scale without a process change.
- **Managers spending coaching time on basics instead of strategy.** If frontline managers are reviewing decks and coaching reps on who the buyer is, they are not spending time on deal strategy or skill development where it actually matters.

### Discovery Questions
1. When you think about your top-performing reps versus the rest of the team, what do you see them doing differently in how they prepare for a first call?
2. How are your AEs currently researching prospects before discovery calls, and how much time are they typically spending on that?
3. When a deal stalls after the first call, what do you usually trace it back to in your deal reviews?

### Agent Review Notes
*This section is generated automatically by the self-check step.*

Pain point "High prep time per call" cites a 45-minute figure presented as fact — label as assumption or benchmark, not Capital One-specific data. Discovery questions 1 and 3 can be answered with a short closed response — reframe to "walk me through" to force a real answer. The brief is otherwise strong, especially the Assumptions and Gaps section.

---

## Two ways to run it

This project shares one engine (`agent.py`) behind two launchers:

- **`main.py`** — the terminal version. Asks you questions, saves the brief to the `output/` folder.
- **`app.py`** — a local website. Fill in a form in your browser, read the brief on the page.

Setup is the same for both. You only change the last command depending on which one you want.

---

## How to run locally

You will do everything through the Terminal app on your Mac. No coding experience needed — just copy and paste each command exactly as shown.

---

### Step 1 — Open Terminal

Press **Command + Space**, type **Terminal**, and hit Enter. A black or white window will open with a `%` prompt. That is where you type commands.

---

### Step 2 — Download the project

Copy and paste this command, then hit Enter:

```bash
git clone https://github.com/patrickalowe/sales-call-prep-agent-v2.git ~/Projects/sales-call-prep-agent-v2
```

This saves the project to a `Projects` folder in your home directory.

---

### Step 3 — Navigate into the project folder

```bash
cd ~/Projects/sales-call-prep-agent-v2
```

> **Important:** You must run this command every time you open a new Terminal window before doing anything else. Think of it as "opening the project folder" — all other commands only work from inside it.

---

### Step 4 — Set up a Python environment

Copy and paste both lines, hitting Enter after each:

```bash
python3 -m venv venv
source venv/bin/activate
```

After the second line, your prompt will change to start with `(venv)`. That means it worked. You will need to run `source venv/bin/activate` again any time you open a new Terminal window.

---

### Step 5 — Install the required packages

```bash
pip install -r requirements.txt
```

This only needs to be done once.

---

### Step 6 — Add your API keys

This tool uses **two** services: Claude (to write the briefing) and Tavily (to search the web). You need a key for each.

1. **Anthropic** — go to [console.anthropic.com](https://console.anthropic.com), create an account, and copy your API key. A $5 credit top-up runs many briefings.
2. **Tavily** — go to [app.tavily.com](https://app.tavily.com), create an account, and copy your API key (it starts with `tvly-`). The free tier covers plenty of testing.
3. In the project folder, create a file called `.env` with both keys, one per line:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Replace each value with your actual key. The `.env` file is never committed to git.

> Tip: if you only want to test without searching the web, you can skip the Tavily key and always run with `--no-search` (see Step 7).

---

### Step 7 — Run it

**Terminal version:**

```bash
python3 main.py
```

The tool will ask you for a company name, a job title, and any notes. Fill those in and it will generate your briefing. Output saves automatically to the `output/` folder.

You can also run it with everything on one line:

```bash
python3 main.py --company "Acme Logistics" --persona "VP of Operations" --notes "Mid-market 3PL, expanded into last-mile."
```

To skip live web search for a cheaper, faster run (training knowledge only), add `--no-search`:

```bash
python3 main.py --company "Acme Logistics" --persona "VP of Operations" --no-search
```

Either way, the run prints its token usage and an estimated cost at the end, so you can see exactly what each briefing spends.

**Website version:**

```bash
python3 app.py
```

Then open **http://localhost:5001** in your browser. Fill in the form and the briefing appears on the page. Press `Control + C` in the Terminal to stop the website when you are done.

---

### Step 8 — View your output (terminal version)

Briefings save as `.md` files in the `output/` folder. To read one in the Terminal without needing any other app installed:

**List all saved briefings:**

```bash
ls output/
```

**Read a file with scroll controls:**

```bash
less output/filename.md
```

Use the arrow keys to scroll. Press `q` to exit. Replace `filename.md` with the name shown when you ran `ls output/`.

---

### Every time you come back

Open Terminal and run these two lines before anything else:

```bash
cd ~/Projects/sales-call-prep-agent-v2
source venv/bin/activate
```

Then run `python3 main.py` (terminal) or `python3 app.py` (website).

---

### Something went wrong?

| What you see | What to do |
|---|---|
| `no such file or directory: sales-call-prep-agent-v2` | You skipped Step 3. Run `cd ~/Projects/sales-call-prep-agent-v2` |
| `can't open file 'main.py'` | You are not in the project folder. Run `cd ~/Projects/sales-call-prep-agent-v2` |
| `No module named 'dotenv'` or `No module named 'flask'` | Run `source venv/bin/activate` then `pip install -r requirements.txt` |
| `AuthenticationError` | Your API key is missing or incorrect. Check your `.env` file |
| `Address already in use` (website) | The website is already running in another Terminal window. Close it, or stop it with `Control + C` |

---

## How it works

The agent runs four steps per briefing, each a separate call to Claude:

| Step | What it does |
|---|---|
| **1. Plan** | Decides the angle to take before generating anything |
| **2. Context** | Researches the company with live web search (recent news, funding, leadership) and organizes what it finds |
| **3. Brief** | Generates the full seven-section briefing, informed by steps 1 and 2 |
| **4. Review** | Reads its own output and flags weak spots: generic claims, bad questions, unlabeled assumptions |

When you run the terminal version you see each step as it happens:

```
Preparing briefing for VP of Sales at Capital One...

  Planning approach...
  Researching company (live web search)...
  Generating briefing...
  Running self-check...

Done. Briefing saved to: output/capital_one_20260525_1428.md
```

Each step is a separate function in `agent.py`. Each prompt lives in `prompts.py` and can be edited without touching any other step. A single system prompt applies to all four calls and sets the agent's role and rules.

`gather_context()` in `agent.py` is where live research happens. It runs a few targeted [Tavily](https://tavily.com) web searches (news/earnings, leadership, and product/strategy — see the `_SEARCH_QUERIES` list and `search.py`), trims the results, and passes them to Claude as context. Claude then writes a sourced summary that feeds straight into the briefing step. Doing the search ourselves (rather than via Claude's server-side tool) keeps token usage low: only the trimmed result snippets enter the prompt, not whole web pages. The prompt instructs Claude to lead with what the results support, name sources inline, and label anything else as inferred. The search provider is isolated in `search.py`, so swapping Tavily for another engine later only touches that one file.

---

## Tech stack

| Tool | Purpose |
|---|---|
| Python 3.9+ | Core language |
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | Claude API client |
| Claude Sonnet (`claude-sonnet-4-6`) | Language model |
| [Tavily](https://tavily.com) (`tavily-python`) | Live web search for the context step (its own API key) |
| python-dotenv | Loads the API key from `.env` |
| Flask | Serves the website version |

Both launchers share a single engine. No databases.

---

## File structure

```
sales-call-prep-agent-v2/
├── agent.py             # Shared engine: calls the Claude API, returns markdown
├── prompts.py           # One prompt per agent step plus a shared system prompt
├── search.py            # Tavily web-search wrapper (the only search-provider code)
├── main.py              # Terminal launcher: input modes, validation, file output
├── app.py               # Website launcher: Flask form and result page
├── templates/
│   └── index.html       # The web form
├── sample_input.json    # Example input for quick testing
├── requirements.txt     # Dependencies
└── output/
    └── example_briefing.md   # Full example output
```

Both `main.py` and `app.py` import the same `agent.py`. Improve a prompt or a step once, and both versions get it.

---

## Limitations

- **Search quality varies by account.** The Tavily search finds far more on well-covered public companies than on small or stealthy ones. When results are thin, the brief falls back to clearly labeled inference rather than inventing facts.
- **A few searches per briefing.** The context step runs three targeted Tavily queries (three Tavily credits, free-tier friendly). Because only trimmed result snippets enter the prompt, a full run stays cheap — a handful of cents in Claude tokens. The number of searches is the `_SEARCH_QUERIES` list in `agent.py`, easy to dial up or down. Every run prints its estimated cost; `--no-search` skips Tavily entirely for an offline-style test run.
- **One briefing per run.** Batch mode is not yet implemented.
- **Output quality scales with input quality.** A company name alone produces a more generic briefing than one with specific rep notes.
- **No CRM integration.** Briefings save as local markdown files.

---

## Future improvements

- ~~Connect `gather_context()` to live web search for current, sourced context~~ — **done in v2** (Tavily web search)
- Surface the specific prospect's public background and recent news (the legitimate, search-based version of a LinkedIn lookup)
- Batch mode: accept a CSV of accounts, output a folder of briefings
- CRM push: write briefings directly into HubSpot or Salesforce as contact notes
- A second-pass step that tightens the outreach draft and pressure-tests the discovery questions

---

## Design notes

What makes this an agent rather than a script: each step uses the output of the previous one as input, the system plans before it generates, and it reviews its own output before returning anything. The workflow is sequential and stateful, not a single prompt with a single response.

Three specific decisions worth noting:

- **Prompts are separated by step, not bundled.** Changing the tone of the planning step does not affect the briefing format. Adding a new output section does not touch the system rules. Each layer can be changed independently.
- **Uncertainty is a first-class output.** The agent is instructed to label inferences as assumptions and surface everything it does not know in a dedicated section. A briefing that presents guesses as facts is worse than no briefing.
- **One engine, two front ends.** The terminal and website versions share a single `agent.py`. The interface is separate from the logic, so a fix lands in both places at once.

---
