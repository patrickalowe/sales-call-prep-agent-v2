"""
CLI entry point for the Sales Call Prep Agent.

Three ways to run it:
    python main.py                                         # interactive
    python main.py --input sample_input.json               # from a JSON file
    python main.py --company "Acme" --persona "VP of Ops"  # from flags
"""

import argparse
import json
import sys

import anthropic
from dotenv import load_dotenv

from agent import run_agent, save_output


def validate_inputs(company, persona):
    """Return a list of error strings. Empty list means inputs are valid."""
    errors = []
    if not company or len(company.strip()) < 2:
        errors.append("Company name is required (at least 2 characters).")
    if not persona or len(persona.strip()) < 2:
        errors.append("Prospect role is required (at least 2 characters).")
    return errors


def get_inputs_interactively():
    print("\n=== Sales Call Prep Agent ===\n")
    company = input("Company name: ").strip()
    persona = input("Prospect role/title: ").strip()
    notes = input("Optional notes (press Enter to skip): ").strip()
    return company, persona, notes


def load_inputs_from_file(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not parse {path} as valid JSON.")
        sys.exit(1)

    if "company" not in data or "persona" not in data:
        print("Error: JSON file must include 'company' and 'persona' fields.")
        sys.exit(1)

    return data["company"], data["persona"], data.get("notes", "")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generate a sales call prep briefing.")
    parser.add_argument("--input", "-i", help="Path to a JSON input file")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--persona", help="Prospect role or title")
    parser.add_argument("--notes", default="", help="Optional context for the rep")
    parser.add_argument("--no-search", action="store_true",
                        help="Skip live web search (cheaper and faster; uses training knowledge only)")
    args = parser.parse_args()

    if args.input:
        company, persona, notes = load_inputs_from_file(args.input)
    elif args.company and args.persona:
        company, persona, notes = args.company, args.persona, args.notes
    else:
        company, persona, notes = get_inputs_interactively()

    errors = validate_inputs(company, persona)
    if errors:
        for error in errors:
            print(f"Error: {error}")
        sys.exit(1)

    print(f"\nPreparing briefing for {persona} at {company}...\n")

    try:
        output = run_agent(
            company_name=company,
            persona_title=persona,
            notes=notes,
            on_step=lambda msg: print(f"  {msg}"),
            use_search=not args.no_search,
        )
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except anthropic.AuthenticationError:
        print("\nError: Invalid API key. Check that ANTHROPIC_API_KEY in .env is correct.")
        sys.exit(1)
    except anthropic.RateLimitError:
        print("\nError: Hit your account's rate limit (tokens per minute on your usage tier).")
        print("Wait a minute and run it again, or raise the limit by adding credits at")
        print("https://console.anthropic.com/settings/limits")
        sys.exit(1)
    except anthropic.APIStatusError as e:
        # The genuine low-balance error is a 400 with this message. Match on it
        # specifically so a rate limit (whose message also says "credits") is
        # never mislabeled as a billing problem.
        if e.status_code == 400 and "credit balance is too low" in str(e).lower():
            print("\nError: Insufficient API credits. Add credits at console.anthropic.com.")
        else:
            print(f"\nError: API error {e.status_code}: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

    output_path = save_output(output, company)
    print(f"\nDone. Briefing saved to: {output_path}\n")


if __name__ == "__main__":
    main()
