"""
Agent 5 - Report Writer
Job: combine every agent's work into one clean business report.
"""
from crewai import Agent, Task


def create_agent(llm):
    return Agent(
        role="Investor Report Writer",
        goal="Combine all findings into one clear, honest business report for founders and investors",
        backstory=(
            "You write pitch-ready reports. You keep the facts from the other analysts, "
            "remove repetition, and write in plain English a first-time founder understands."
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )


def create_task(agent, context):
    return Task(
        description=(
            "Write the final PROOF business report for the invoice from {company}. "
            "Use the work of the market, risk, financial and strategy analysts. "
            "Sections: Executive summary, The problem, Market, This invoice's verdict, "
            "Deal economics, Strategy, Risks, Next 30 days. "
            "Keep labels like 'estimate' or 'assumption' on uncertain numbers."
        ),
        expected_output="A polished markdown report of 500-700 words.",
        agent=agent,
        context=context,
        markdown=True,
    )
