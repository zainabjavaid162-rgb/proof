"""
Agent 1 - Market Research Analyst
Job: size the problem (SME cash stuck in unpaid invoices) and map competitors.
"""
from crewai import Agent, Task


def create_agent(llm):
    return Agent(
        role="Pakistan SME Finance Market Researcher",
        goal="Explain how big the invoice-financing gap is for Pakistani SMEs and who else is solving it",
        backstory=(
            "You have studied SME lending in Pakistan for years: State Bank of Pakistan SME "
            "policies, export clusters like Sialkot, Faisalabad and Karachi, and fintechs. "
            "You never invent statistics: if you are not sure of a number you label it "
            "as an estimate or an assumption."
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )


def create_task(agent):
    return Task(
        description=(
            "Research the market for PROOF, an invoice-factoring platform for Pakistani SMEs "
            "that uses AI verification and a blockchain record to stop double funding.\n"
            "Focus example: a {sector} business in {city}.\n"
            "Cover: 1) why SMEs wait 60-120 days to be paid and why banks refuse them, "
            "2) a rough market size for SME receivables in Pakistan (the founders claim "
            "Rs 400B; say whether that looks plausible and what it depends on), "
            "3) three to five competitors or alternatives (banks, fintechs, informal lenders), "
            "4) the target customer and the target investor."
        ),
        expected_output=(
            "A concise market brief under 350 words in markdown with short headings. "
            "Mark every number as 'reported', 'estimate' or 'assumption'."
        ),
        agent=agent,
    )
