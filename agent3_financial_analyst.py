"""
Agent 3 - Financial Analyst
Job: explain the deal economics for the SME, the investor and the platform.
The numbers are calculated by Python (tools.py) so they are exact;
the agent explains them and builds simple projections.
"""
from crewai import Agent, Task


def create_agent(llm):
    return Agent(
        role="Fintech Financial Analyst",
        goal="Show clearly whether PROOF works financially for SMEs, investors and the company",
        backstory=(
            "You build unit-economics models for lending start-ups. You use the exact "
            "numbers you are given and you show your assumptions openly."
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )


def create_task(agent, context):
    return Task(
        description=(
            "Use these exact deal numbers (already calculated, do not change them):\n"
            "{deal_summary}\n\n"
            "Explain: 1) what the SME pays and whether that beats bank or informal loans, "
            "2) the investor return and the main risks to it, 3) platform revenue per invoice, "
            "4) a simple year-1 projection if PROOF funds 200, 1,000 and 5,000 invoices of "
            "this size (state assumptions such as default rate and repeat customers)."
        ),
        expected_output="Markdown under 350 words with one small table for the projection.",
        agent=agent,
        context=context,  # can read the market and risk agents' answers
    )
