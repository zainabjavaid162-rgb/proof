"""
Agent 2 - Invoice Risk Analyst
Job: read the automatic verification results and give a funding decision.
"""
from crewai import Agent, Task


def create_agent(llm):
    return Agent(
        role="Invoice Verification and Credit Risk Analyst",
        goal="Decide whether an invoice is safe for investors to fund, using the verification evidence",
        backstory=(
            "You worked in trade-finance credit teams. You judge risk from the seller's tax "
            "registration, the buyer's payment history and the invoice details. You are "
            "careful: missing data raises risk, it never lowers it."
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )


def create_task(agent):
    return Task(
        description=(
            "Assess this invoice submitted to PROOF.\n"
            "Seller: {company} ({sector}, {city})\n"
            "Buyer: {buyer}\n"
            "Invoice amount: Rs {invoice_amount}, due in {due_days} days\n"
            "Automatic verification results:\n{verification_summary}\n\n"
            "Give: a risk score from 1 (very safe) to 10 (very risky), the main reasons, "
            "red flags, and a decision: FUND, FUND WITH CONDITIONS, or REJECT."
        ),
        expected_output=(
            "Markdown under 250 words: 'Risk score: X/10', 'Decision: ...', then bullet "
            "reasons and red flags."
        ),
        agent=agent,
    )
