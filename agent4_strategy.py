"""
Agent 4 - Business Strategist
Job: business model, go-to-market, regulation, and the role of blockchain.
"""
from crewai import Agent, Task


def create_agent(llm):
    return Agent(
        role="Startup Strategy and Regulation Advisor",
        goal="Turn the research into a practical launch plan for PROOF in Pakistan",
        backstory=(
            "You advise Pakistani fintech founders. You know SECP and State Bank of "
            "Pakistan rules matter for lending and investment platforms, and you are honest "
            "about what blockchain does and does not solve."
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )


def create_task(agent, context):
    return Task(
        description=(
            "Using the market, risk and financial analysis, write PROOF's strategy: "
            "1) business model and pricing, 2) go-to-market for the first 6 months "
            "starting with {city}, 3) licences and regulators to check with "
            "(say a lawyer must confirm), 4) why the Polygon invoice hash helps "
            "(no double funding) and its limits, 5) top 5 risks with mitigations."
        ),
        expected_output="Markdown under 350 words with short headings.",
        agent=agent,
        context=context,
    )
