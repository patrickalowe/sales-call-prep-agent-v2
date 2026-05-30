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
    sales_role = input("Your sales role [SDR/BDR or AE] (Enter for AE; SDR and BDR give the same brief): ").strip()
    notes = input("Optional notes (press Enter to skip): ").strip()
    product_name = input("Product you're selling (press Enter to skip): ").strip()
    product_benefits = ""
    target_use_case = ""
    if product_name:
        product_benefits = input("What does it do? (press Enter to skip): ").strip()
        target_use_case = input("Target use case (press Enter to skip): ").strip()
    return company, persona, notes, sales_role, product_name, product_benefits, target_use_case


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

    # Accept either the short keys (company/persona) or the longer ones
    # (company_name/persona_title) so older and newer input files both work.
    company = data.get("company") or data.get("company_name")
    persona = data.get("persona") or data.get("persona_title")
    if not company or not persona:
        print("Error: JSON file must include 'company' (or 'company_name') "
              "and 'persona' (or 'persona_title') fields.")
        sys.exit(1)

    return (
        company,
        persona,
        data.get("notes", ""),
        data.get("sales_role", ""),
        data.get("product_name", ""),
        data.get("product_benefits", ""),
        data.get("target_use_case", ""),
    )


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generate a sales call prep briefing.")
    parser.add_argument("--input", "-i", help="Path to a JSON input file")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--persona", help="Prospect role or title")
    parser.add_argument("--sales-role", default="", help="Your sales role: SDR, BDR, or AE (defaults to AE)")
    parser.add_argument("--notes", default="", help="Optional context for the rep")
    parser.add_argument("--product-name", default="", help="Optional product you are selling")
    parser.add_argument("--product-benefits", default="", help="Optional summary of what the product does")
    parser.add_argument("--target-use-case", default="", help="Optional use case the product is being sold for")
    parser.add_argument("--no-search", action="store_true",
                        help="Skip live web search (cheaper and faster; uses training knowledge only)")
    args = parser.parse_args()

    if args.input:
        company, persona, notes, sales_role, product_name, product_benefits, target_use_case = load_inputs_from_file(args.input)
    elif args.company and args.persona:
        company, persona, notes = args.company, args.persona, args.notes
        sales_role = args.sales_role
        product_name, product_benefits = args.product_name, args.product_benefits
        target_use_case = args.target_use_case
    else:
        company, persona, notes, sales_role, product_name, product_benefits, target_use_case = get_inputs_interactively()

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
            sales_role=sales_role,
            product_name=product_name,
            product_benefits=product_benefits,
            target_use_case=target_use_case,
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
