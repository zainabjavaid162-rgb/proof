# PROOF - Invoice factoring for Pakistani SMEs

A Sialkot factory sends a Rs 5 lakh invoice, but its buyer pays in 90 days.
PROOF verifies the invoice, gives it a unique fingerprint so it can only be
funded once, lets investors fund 90% today, and pays them 95% when the buyer pays.

Five AI agents (CrewAI + Groq) then research the market and write a business report.

## Files (all in the main folder)

| File | What it does |
|---|---|
| `app.py` | The website (Streamlit). Start reading here. |
| `config.py` | Connects to Groq's `openai/gpt-oss-120b` model. |
| `tools.py` | Plain-Python checks: NTN + Verhoeff, buyer history, invoice hash, ROI maths. |
| `crew.py` | Puts the 5 agents into one team and runs them in order. |
| `agent1_market_research.py` | Agent 1: market size and competitors. |
| `agent2_invoice_risk.py` | Agent 2: risk score and fund / reject decision. |
| `agent3_financial_analyst.py` | Agent 3: SME cost, investor return, projections. |
| `agent4_strategy.py` | Agent 4: business model, launch plan, regulation, risks. |
| `agent5_report_writer.py` | Agent 5: combines everything into the final report. |
| `requirements.txt` | Libraries Streamlit Cloud installs for you. |

## Deploy (no installs on your laptop)

1. **Groq key**: sign in at console.groq.com, open API Keys, create a key, copy it (starts with `gsk_`).
2. **GitHub**: create a new public repository named `proof`. Click *Add file > Upload files*,
   drag in every file from this folder, and click *Commit changes*.
3. **Streamlit**: sign in at share.streamlit.io with GitHub, click *Create app*,
   choose your `proof` repo, branch `main`, main file `app.py`.
4. Open **Advanced settings**: set Python version to **3.12**, and in *Secrets* paste:
   ```
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click **Deploy**. The first build takes about 3-5 minutes.

To change anything later: edit the file on GitHub (pencil icon) and commit.
Streamlit redeploys automatically within a minute.

## Using the demo

1. *Verify invoice* tab: keep the sample values and click **Verify invoice**.
2. Click **Fund this invoice**, then click **Verify invoice** again: it is blocked as already funded.
3. *Investor view* shows invested amount, profit and ROI.
4. *AI business report* runs the 5 agents (1-3 minutes).

## Honest limits of this demo

- Buyer payment history is sample data in `tools.py`.
- The Verhoeff rule on the NTN is a demo check, not FBR's official validation.
- The fingerprint is stored in the browser session, not yet on Polygon.
- Agents use the model's own knowledge (no live web search), so they label uncertain numbers.

## Common errors

| Message | Fix |
|---|---|
| Rate limit reached | Wait a minute, raise the pause slider, or pick GPT-OSS 20B. |
| Groq rejected the API key | Re-copy the key into Streamlit *Settings > Secrets*. |
| Build failed / module not found | Check `requirements.txt` was uploaded and Python is 3.12. |
| Model does not exist | Groq retired the model; pick a current one at console.groq.com/docs/models and edit `config.py`. |
