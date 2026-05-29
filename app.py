"""
Web server for the Sales Call Prep Agent.

Exposes two routes:
  GET  /           -- renders the input form
  POST /generate   -- runs the agent, saves the brief to output/, and
                      returns the briefing plus the saved filename as JSON

Run with: python app.py
Then open http://localhost:5001 in your browser.
"""

import anthropic
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from agent import run_agent, save_output

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    company = request.form.get("company", "").strip()
    persona = request.form.get("persona", "").strip()
    notes = request.form.get("notes", "").strip()

    if not company or not persona:
        return jsonify({"error": "Company name and prospect role are both required."}), 400

    try:
        result = run_agent(company_name=company, persona_title=persona, notes=notes)
        saved_path = save_output(result, company)
        return jsonify({"result": result, "saved_as": str(saved_path)})
    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key. Check your ANTHROPIC_API_KEY."}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Hit your account's rate limit (tokens per minute). Wait a minute and try again, or raise the limit at console.anthropic.com/settings/limits."}), 429
    except anthropic.APIStatusError as e:
        # Only a genuine 400 low-balance error is a billing problem; a 429
        # rate limit also mentions "credits" but must not be labeled that way.
        if e.status_code == 400 and "credit balance is too low" in str(e).lower():
            return jsonify({"error": "Insufficient API credits. Add credits at console.anthropic.com."}), 402
        return jsonify({"error": f"API error {e.status_code}: {e.message}"}), 500
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
