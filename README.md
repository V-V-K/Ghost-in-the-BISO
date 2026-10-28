# 👻 The Ghost in the BISO

**An offline-first, open-weight AI companion for security risk, audit readiness, and remediation.**

> The past leaves evidence. The future inherits risk.

The Ghost in the BISO turns a fictional BISO risk register into an interactive security governance demo. It highlights aging findings, missing owners, evidence gaps, and high-severity open items; then uses a locally running model to explain the data and draft a leadership briefing.

## Why this exists

Security teams often have risk registers and audit trackers spread across tools. This prototype explores how local AI can help a BISO interpret that information without sending sensitive records to a hosted AI API.

## Features

- **Ghost Radar:** transparent Python-based metrics and a findings dashboard.
- **Evidence Séance:** identify missing evidence and generate a request checklist.
- **Ask the Ghost:** question the fictional register in natural language.
- **BISO Briefing:** generate and download a Markdown leadership summary.
- **Local inference:** uses Ollama's local API and an open-weight model.
- **Fictional sample data:** safe for demos; no enterprise connection.

## Architecture

```text
Fictional CSV
    |
    v
Python + Pandas ----> deterministic counts and risk sorting
    |
    v
Streamlit UI --------> Ghost Radar / Evidence / Q&A / Briefing
    |
    v
Ollama local API ----> open-weight model running on this computer
```

The model explains and summarizes records. Python calculates the dashboard metrics. This separation keeps key numbers reproducible and easier to verify.

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10+
- [Ollama](https://ollama.com/download)
- Enough RAM for the selected model; try `qwen3:1.7b` on constrained hardware or `qwen3:4b` for a stronger local demo

## Run locally

1. Install Ollama from <https://ollama.com/download>.
2. Open a terminal and download the model:

   ```bash
   ollama pull qwen3:4b
   ```

   For a smaller model, use `ollama pull qwen3:1.7b` and change the model field in the app.

3. In the project directory, create a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   streamlit run app.py
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

4. The app opens in your browser, usually at <http://localhost:8501>.
5. Keep Ollama running. After the model is downloaded, local inference can work without an internet connection.

## Try these prompts

- Which open risks should the BISO follow up on first?
- Which findings have been open for more than 30 days and why does that matter?
- What evidence should we request for the privileged access review?
- Draft a leadership briefing that separates facts from recommendations.
- What information is missing before we can confidently assess these findings?

## CSV format

The uploaded CSV must include:

`finding_id,title,domain,severity,status,owner,days_open,evidence_status,business_impact`

The app expects common values such as Critical/High/Medium/Low, Open/In Progress/Closed, and Complete/Verified/Partial/Missing. It is a prototype, so validate your input format.

## Privacy and safety

- The default dataset is fictional.
- The app sends prompt content only to the local Ollama endpoint at `localhost`.
- Do not use real employer data, names, internal URLs, tickets, audit evidence, secrets, or confidential information in a public demo.
- The model can be wrong. Treat output as a draft, verify it against evidence, and keep human approval in the loop.
- This is not an automated compliance verdict or a replacement for professional security review.

## Open innovation

Local, swappable models make it possible to experiment without tying the core workflow to one hosted AI API. Running inference on-device can keep test records local and allows the demo to work offline after model download. Model weights and software licenses vary; check the selected model's license and terms before redistribution or commercial use.

## Roadmap

- [ ] Add unit tests for risk metrics and CSV validation
- [ ] Add evidence citations by finding ID to every generated recommendation
- [ ] Add export to HTML/PDF
- [ ] Add a model selector with model health check
- [ ] Add optional local retrieval over audit documents
- [ ] Add accessibility and light-theme options

## License

MIT for this project's code. The model has its own separate license and terms.
