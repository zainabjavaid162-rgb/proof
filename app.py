"""
app.py - the PROOF web app (Streamlit).
Streamlit Cloud runs this file. Three tabs:
  1. Verify invoice   - instant checks + a fingerprint that blocks double funding
  2. Investor view    - ROI for funded invoices
  3. AI business report - 5 CrewAI agents research and write the report
"""

# --- sqlite fix: must run BEFORE crewai is imported (needed on some Linux servers) ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass  # on your laptop or Windows this is not needed

import os
from datetime import date, timedelta

import streamlit as st

os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from config import AVAILABLE_MODELS, DEFAULT_MODEL_LABEL, get_llm
from tools import (
    DEMO_BUYERS, check_buyer, check_ntn, deal_numbers, days_until,
    invoice_hash, verhoeff_make_check_digit,
)

st.set_page_config(page_title="PROOF - invoice factoring", page_icon="🧾", layout="wide")

# A little styling: the verification result looks like a rubber stamp on an invoice.
st.markdown("""
<style>
.stamp {display:inline-block; padding:.6rem 1.2rem; border:3px solid; border-radius:6px;
        font-weight:800; font-size:1.4rem; transform:rotate(-3deg); letter-spacing:.02em;}
.stamp.ok  {color:#1F7A4D; border-color:#1F7A4D;}
.stamp.bad {color:#B3261E; border-color:#B3261E;}
.hash {font-family:monospace; font-size:.8rem; word-break:break-all; color:#555;}
</style>
""", unsafe_allow_html=True)

# Memory for this browser session (a stand-in for the Polygon ledger).
if "ledger" not in st.session_state:
    st.session_state.ledger = []          # list of funded invoices
if "last_check" not in st.session_state:
    st.session_state.last_check = None

SAMPLE_NTN = "1234567-" + verhoeff_make_check_digit("1234567")

# ---------------- Sidebar: API key and model ----------------
with st.sidebar:
    st.header("Settings")
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:  # no secrets file (e.g. first run) - that's fine
        secret_key = ""
    api_key = secret_key or st.text_input("Groq API key", type="password",
                                          help="Free key at console.groq.com/keys")
    if secret_key:
        st.success("Groq key loaded from app secrets")
    model_label = st.selectbox("Model", list(AVAILABLE_MODELS),
                               index=list(AVAILABLE_MODELS).index(DEFAULT_MODEL_LABEL))
    pause = st.slider("Pause between agents (seconds)", 0, 30, 10,
                      help="Groq's free plan limits tokens per minute. A pause avoids errors.")
    st.caption(f"Test NTN that passes the check: **{SAMPLE_NTN}**")

st.title("PROOF")
st.write("Get paid today for invoices your buyers will pay in 90 days. "
         "Each invoice is verified, fingerprinted and can only be funded once.")

tab_verify, tab_investor, tab_report = st.tabs(
    ["Verify invoice", "Investor view", "AI business report"])

# ---------------- Tab 1: Verify invoice ----------------
with tab_verify:
    left, right = st.columns([1, 1], gap="large")
    with left:
        company = st.text_input("Your company", "Sialkot Sports Works")
        sector = st.text_input("Sector", "Sports goods manufacturing")
        city = st.text_input("City", "Sialkot")
        ntn = st.text_input("Your NTN", SAMPLE_NTN)
        buyer = st.selectbox("Buyer", list(DEMO_BUYERS) + ["Other (new buyer)"])
        if buyer == "Other (new buyer)":
            buyer = st.text_input("Buyer name", "New Buyer Pvt Ltd")
        invoice_no = st.text_input("Invoice number", "INV-2026-0147")
        amount = st.number_input("Invoice amount (Rs)", min_value=10_000,
                                 value=500_000, step=10_000)
        due = st.date_input("Buyer pays on", date.today() + timedelta(days=90))
        check = st.button("Verify invoice", type="primary")

    if check:
        ntn_result = check_ntn(ntn)
        buyer_result = check_buyer(buyer)
        fingerprint = invoice_hash(ntn, invoice_no, buyer, amount)
        already = any(x["hash"] == fingerprint for x in st.session_state.ledger)
        st.session_state.last_check = {
            "company": company, "sector": sector, "city": city, "ntn": ntn,
            "buyer": buyer, "invoice_no": invoice_no, "amount": amount,
            "days": days_until(due), "ntn_result": ntn_result,
            "buyer_result": buyer_result, "hash": fingerprint, "already": already,
        }

    with right:
        c = st.session_state.last_check
        if not c:
            st.info("Fill in the invoice and select **Verify invoice** to see the result here.")
        else:
            passed = c["ntn_result"]["ok"] and not c["already"]
            if c["already"]:
                st.markdown('<span class="stamp bad">Already funded - blocked</span>',
                            unsafe_allow_html=True)
            elif passed:
                st.markdown('<span class="stamp ok">Verified</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="stamp bad">Not verified</span>', unsafe_allow_html=True)

            st.write("")
            st.write(("✅ " if c["ntn_result"]["ok"] else "❌ ") + "NTN: " + c["ntn_result"]["reason"])
            st.write(("✅ " if c["buyer_result"]["known"] else "⚠️ ") + "Buyer: " + c["buyer_result"]["summary"])
            st.write(("❌ " if c["already"] else "✅ ") + "Double funding: " +
                     ("this exact invoice was already funded." if c["already"] else "no earlier funding found."))
            st.markdown(f'Invoice fingerprint (would be saved on Polygon):<br>'
                        f'<span class="hash">{c["hash"]}</span>', unsafe_allow_html=True)

            d = deal_numbers(c["amount"], c["days"])
            m1, m2, m3 = st.columns(3)
            m1.metric("Cash to you today", f"Rs {d['advance_to_sme']:,}")
            m2.metric("Investor profit", f"Rs {d['investor_profit']:,}")
            m3.metric("Your total cost", f"{d['sme_total_cost_pct']}%")

            if passed and st.button("Fund this invoice"):
                st.session_state.ledger.append({**c, **d})
                st.session_state.last_check["already"] = True
                st.success("Funded and fingerprint recorded. Try funding it again to see it blocked.")
                st.rerun()

# ---------------- Tab 2: Investor view ----------------
with tab_investor:
    ledger = st.session_state.ledger
    if not ledger:
        st.info("No invoices funded yet. Verify and fund one in the first tab.")
    else:
        invested = sum(x["advance_to_sme"] for x in ledger)
        returned = sum(x["investor_receives"] for x in ledger)
        a, b, c3 = st.columns(3)
        a.metric("Total invested", f"Rs {invested:,}")
        b.metric("Expected back", f"Rs {returned:,}")
        c3.metric("Expected profit", f"Rs {returned - invested:,}",
                  f"{(returned / invested - 1) * 100:.2f}%")
        st.dataframe(
            [{"Invoice": x["invoice_no"], "Seller": x["company"], "Buyer": x["buyer"],
              "Invested (Rs)": x["advance_to_sme"], "Back (Rs)": x["investor_receives"],
              "ROI %": x["investor_roi_pct"], "Annualised %": x["investor_annualised_pct"],
              "Days": x["days"]} for x in ledger],
            width="stretch", hide_index=True)
        st.bar_chart({x["invoice_no"]: x["investor_profit"] for x in ledger})

# ---------------- Tab 3: AI business report ----------------
with tab_report:
    st.write("Five AI agents work in order: market researcher, invoice risk analyst, "
             "financial analyst, strategist and report writer. It takes about 1-3 minutes.")
    c = st.session_state.last_check
    if not c:
        st.info("Verify an invoice first so the agents have real details to analyse.")
    elif not api_key:
        st.warning("Add your Groq API key in the sidebar (or in the app's secrets) to run the agents.")
    elif st.button("Generate business report", type="primary"):
        from crew import AGENT_NAMES, run_crew  # imported only when needed

        d = deal_numbers(c["amount"], c["days"])
        inputs = {
            "company": c["company"], "sector": c["sector"], "city": c["city"],
            "buyer": c["buyer"], "invoice_amount": f"{c['amount']:,.0f}",
            "due_days": c["days"],
            "verification_summary": (
                f"- NTN check: {c['ntn_result']['reason']}\n"
                f"- Buyer history: {c['buyer_result']['summary']}\n"
                f"- Double funding: {'ALREADY FUNDED' if c['already'] else 'none found'}"),
            "deal_summary": "\n".join(f"- {k}: {v}" for k, v in d.items()),
        }
        progress = st.progress(0, text="Starting the agents...")

        def on_done(n, output):
            nxt = AGENT_NAMES[n] if n < len(AGENT_NAMES) else "done"
            progress.progress(n / len(AGENT_NAMES),
                              text=f"{AGENT_NAMES[n - 1]} finished. Next: {nxt}")

        try:
            llm = get_llm(api_key, AVAILABLE_MODELS[model_label])
            report, steps = run_crew(llm, inputs, pause, on_done)
            st.session_state.report = (report, steps)
            progress.progress(1.0, text="Report ready")
        except Exception as e:
            msg = str(e)
            if "rate" in msg.lower() or "429" in msg or "413" in msg:
                st.error("Groq rate limit reached. Wait one minute, raise the pause in the "
                         "sidebar or switch to GPT-OSS 20B, then try again.")
            elif "401" in msg or "api key" in msg.lower():
                st.error("Groq rejected the API key. Check it at console.groq.com/keys.")
            else:
                st.error(f"The agents stopped with an error: {msg[:400]}")

    if "report" in st.session_state:
        report, steps = st.session_state.report
        st.markdown(report)
        st.download_button("Download report (.md)", report, file_name="proof_report.md")
        with st.expander("See each agent's work"):
            from crew import AGENT_NAMES
            for name, text in zip(AGENT_NAMES, steps):
                st.subheader(name)
                st.markdown(text)
