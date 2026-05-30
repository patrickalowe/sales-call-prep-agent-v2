# Sales Call Prep Agent (v2)

A Python tool that turns a company, a prospect's role, your sales role, and optional product context into a structured pre-call briefing. The brief adapts to your role: short and outbound-focused for SDRs and BDRs (personalize, qualify, book a meeting), deeper and discovery-focused for AEs (stakeholders, business case, risk, next steps). It researches the account with live web search, so the brief reflects current news and not just the model's training data. Use it two ways: a terminal version that saves the brief as a timestamped markdown file, or a local website with a simple form.

> **What's new in v2** (the [v1 repo](https://github.com/patrickalowe/sales-call-prep-agent) wrote one generic brief from the model's training knowledge only):
> - **Role-aware output**: tell it whether you are an SDR/BDR or an AE and the brief restructures itself, short and outbound-focused for early-stage reps, deep and discovery-focused for AEs.
> - **Product context**: pass what you sell and the use case you are leading with, and the pain points, objections, business case, and next step connect directly to it.
> - **Live web research** via [Tavily](https://tavily.com): the context step runs three targeted searches (one tuned to your role) and grounds the brief in current news, funding, leadership, and incumbent tools.
> - **Cost readout** printed after every run (tokens + estimated dollars), plus a `--no-search` flag for cheap offline-style test runs.
> - **Sturdier under real conditions**: accurate error messages (rate limits are no longer mislabeled as billing problems) and automatic waiting through per-minute rate limits.
>
> Requires two keys: `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` (see Step 6).

---

## Overview

I spent several years in sales before moving into AI-enabled workflows. Before every discovery call, prep was manual and inconsistent. Sometimes I spent twenty minutes researching. Sometimes I walked in cold. The quality of preparation depended entirely on how much time I had that day.

This tool solves that. Give it a company name and a title, and it returns a briefing that tells you what the person likely cares about, what questions will open a real conversation, and what you do not yet know and should verify before the call. That last part matters as much as the rest.

---

## What it produces

The brief adapts to your sales role. Three sections are shared by everyone, the middle changes by role, and a common tail closes it out.

**Shared by all roles**

| Section | What it contains |
|---|---|
| **Account** | What the company does, who they serve, and their current situation |
| **Persona** | What this role owns, cares about day-to-day, and is measured on |
| **Potential Pain Points** | Role-specific problems, each tagged with the product capability that addresses it |

**SDR / BDR middle** (kept short, optimized for booking a meeting)

| Section | What it contains |
|---|---|
| **Before You Send** | A one-line gate: is the contact verified, is there a real why-now, or "verify before sending" |
| **Why Now and Opener** | The strongest reason to reach out now, plus ready opener lines |
| **Likely Objections** | Objections vs the likely incumbent, with benefit-grounded responses |

**AE middle** (deeper, optimized for discovery)

| Section | What it contains |
|---|---|
| **Stakeholder Map** | The likely buying group, who to prioritize, who can block |
| **Business Case Angle** | Cost of the status quo, the outcome you enable, how the buyer justifies it |
| **Competitive Read** | What they likely use today and the displacement angle |
| **Risks and Watch-outs** | Deal risks, each with a way to test for it on the call |
| **Recommended Next Step** | A concrete next step that validates the use case |

**Tail (all roles)**

| Section | What it contains |
|---|---|
| **Discovery Questions** | Open-ended questions (3 to qualify for SDR/BDR, 5 to go deep for AE) |
| **Sample Outreach** | A cold message (SDR/BDR) or a pre-call note (AE), under 100 words |
| **Assumptions and Gaps** | What is uncertain and should be verified before the call |

Every factual claim is labeled **confirmed**, **likely**, or **possible**, so you always know what is grounded versus inferred.

---

## Example output

The following is excerpted from a real **AE** briefing for a VP of Sales at Gusto, selling a revenue intelligence platform for the "forecasting accuracy" use case. [See the full output here](output/example_briefing.md), including the stakeholder map, competitive read, and Agent Review Notes.

---

### Persona
The VP of Sales at Gusto owns revenue attainment, pipeline health, and forecast accuracy across a team that is actively expanding headcount. Day-to-day, this person is likely managing the tension between hitting near-term number commitments to the board or CEO and building the process infrastructure needed to sustain a larger team (likely). They are measured on quota attainment, forecast accuracy, and how fast new reps ramp to productivity (likely).

### Potential Pain Points (one of several)
**Pain:** New reps joining at pace are submitting pipeline that lacks the depth or hygiene to forecast reliably, making the weekly commit call a mix of real signal and noise.
**Why it matters:** If the VP is presenting to a CEO or board with a $1B revenue trajectory, a missed forecast is not just an operational problem. It is a credibility problem at a moment when the company is making significant investment bets based on those numbers.
**Signal to listen for:** "Our commit calls are taking longer" or "I don't fully trust what my reps are putting in."
**Addressed by:** Forecast accuracy and pipeline blind spot features, specifically surfacing deal risk from activity signals rather than rep-entered data.

### Recommended Next Step
Before closing the call, propose a scoped forecast accuracy diagnostic: a working session where you map the VP's current forecasting workflow, identify the stages where signal degrades, and show concretely where the platform would add visibility. This is more valuable than a generic demo because it forces the VP to articulate the problem in their own terms. Include the RevOps or Sales Ops lead if they exist.

*(For an SDR on the same account, the brief instead opens with a Before You Send gate and leads with a Why Now and Opener plus qualifying questions.)*

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

The tool will ask you for a company, a prospect role, your sales role (SDR/BDR or AE), optional notes, and optional product details. Fill those in and it will generate your briefing. Output saves automatically to the `output/` folder.

You can also run it with everything on one line. The role and product flags are optional (it defaults to an AE brief):

```bash
python3 main.py --company "Gusto" --persona "VP of Sales" --sales-role AE \
  --product-name "Revenue Intelligence Platform" \
  --product-benefits "Improves forecast accuracy and flags deal risk early" \
  --target-use-case "forecasting for a scaling sales team"
```

For an SDR brief, pass `--sales-role SDR` (SDR and BDR produce the same outbound brief).

To skip live web search for a cheaper, faster run (training knowledge only), add `--no-search`:

```bash
python3 main.py --company "Gusto" --persona "VP of Sales" --sales-role SDR --no-search
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

The agent runs five steps per briefing, each a separate call to Claude (plus the Tavily search in step 2):

| Step | What it does |
|---|---|
| **1. Plan** | Decides the angle to take before generating anything |
| **2. Context** | Researches the company with live web search (recent news, funding, leadership) and organizes what it finds |
| **3. Brief** | Generates the full briefing, with sections that adapt to your role (SDR/BDR vs AE), informed by steps 1 and 2 |
| **4. Refine** | Second pass that tightens the Sample Outreach and pressure-tests the Discovery Questions, then splices the improved sections back in |
| **5. Review** | Reads the refined brief and flags weak spots — generic claims, weak questions, mislabeled confidence — then applies a final test: would a senior rep use this as-is, or rewrite it before the call? |

When you run the terminal version you see each step as it happens:

```
Preparing briefing for VP of Sales at Gusto...

  Planning approach...
  Researching company (live web search)...
  Generating briefing...
  Refining outreach and questions...
  Running self-check...

Done. Briefing saved to: output/gusto_20260529_1857.md
```

Each step is a separate function in `agent.py`. Each prompt lives in `prompts.py` and can be edited without touching any other step. A single system prompt applies to all five calls and sets the agent's role and rules.

`gather_context()` in `agent.py` is where live research happens. It runs three targeted [Tavily](https://tavily.com) web searches: two base queries (news/earnings and leadership) plus one tuned to your role, a hiring/expansion trigger query for SDR/BDR or a stack-and-competitor query for AE (see `_SEARCH_QUERIES_BASE` and `_SEARCH_QUERIES_BY_ROLE` in `agent.py`, and `search.py`). It trims the results and passes them to Claude as context. Claude then writes a sourced summary that feeds straight into the briefing step. Doing the search ourselves (rather than via Claude's server-side tool) keeps token usage low: only the trimmed result snippets enter the prompt, not whole web pages. The prompt instructs Claude to lead with what the results support, name sources inline (and treat those cited facts as confirmed), and label everything else as likely or possible. The search provider is isolated in `search.py`, so swapping Tavily for another engine later only touches that one file.

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
├── sample_input.json         # Example input (company/persona/notes)
├── sample_input_product.json # Example input with sales role and product context
├── requirements.txt          # Dependencies
└── output/
    └── example_briefing.md   # Full example output
```

Both `main.py` and `app.py` import the same `agent.py`. Improve a prompt or a step once, and both versions get it.

---

## Limitations

- **Search quality varies by account.** The Tavily search finds far more on well-covered public companies than on small or stealthy ones. When results are thin, the brief falls back to clearly labeled inference rather than inventing facts.
- **A few searches per briefing.** The context step runs three targeted Tavily queries (three Tavily credits, free-tier friendly). Because only trimmed result snippets enter the prompt, a full run stays cheap — a handful of cents in Claude tokens. The searches live in `_SEARCH_QUERIES_BASE` and `_SEARCH_QUERIES_BY_ROLE` in `agent.py`, easy to adjust. Every run prints its estimated cost; `--no-search` skips Tavily entirely for an offline-style test run.
- **One briefing per run.** Batch mode is not yet implemented.
- **Output quality scales with input quality.** A company name alone produces a more generic briefing than one with specific rep notes.
- **No CRM integration.** Briefings save as local markdown files.

---

## Future improvements

- ~~Connect `gather_context()` to live web search for current, sourced context~~ — **done in v2** (Tavily web search)
- Surface the specific prospect's public background and recent news (the legitimate, search-based version of a LinkedIn lookup)
- Batch mode: accept a CSV of accounts, output a folder of briefings
- CRM push: write briefings directly into HubSpot or Salesforce as contact notes
- ~~A second-pass step that tightens the outreach draft and pressure-tests the discovery questions~~ — **done** (step 4, Refine)

---

## Design notes

What makes this an agent rather than a script: each step uses the output of the previous one as input, the system plans before it generates, and it reviews its own output before returning anything. The workflow is sequential and stateful, not a single prompt with a single response.

Three specific decisions worth noting:

- **Prompts are separated by step, not bundled.** Changing the tone of the planning step does not affect the briefing format. Adding a new output section does not touch the system rules. Each layer can be changed independently.
- **Role-aware without multiple agents.** SDR/BDR and AE share one pipeline and one prompt set. The role just switches which sections the briefing step emits and tunes one of the searches. There are no separate agents to keep in sync.
- **Uncertainty is a first-class output.** Every claim is tagged on a three-tier confidence scale — confirmed (from search results), likely (a reasonable inference from company size, industry, or role), or possible (speculative but worth exploring) — and everything still unknown is collected in a dedicated Assumptions and Gaps section. A briefing that presents guesses as facts is worse than no briefing.
- **One engine, two front ends.** The terminal and website versions share a single `agent.py`. The interface is separate from the logic, so a fix lands in both places at once.

---
