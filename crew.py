"""
crew.py - puts the 5 agents together into one team (a "Crew") and runs them.

Order of work (sequential):
  1 Market researcher  ->  2 Invoice risk analyst  ->  3 Financial analyst
  ->  4 Strategist  ->  5 Report writer
Later agents receive earlier agents' answers through `context`.
"""
import time

from crewai import Crew, Process

import agent1_market_research as a1
import agent2_invoice_risk as a2
import agent3_financial_analyst as a3
import agent4_strategy as a4
import agent5_report_writer as a5

AGENT_NAMES = [
    "Market researcher",
    "Invoice risk analyst",
    "Financial analyst",
    "Strategist",
    "Report writer",
]


def build_crew(llm, pause_seconds: int = 0, on_task_done=None):
    # Create the agents
    market = a1.create_agent(llm)
    risk = a2.create_agent(llm)
    finance = a3.create_agent(llm)
    strategy = a4.create_agent(llm)
    writer = a5.create_agent(llm)

    # Create the tasks, linking who reads whose work
    t_market = a1.create_task(market)
    t_risk = a2.create_task(risk)
    t_finance = a3.create_task(finance, context=[t_market, t_risk])
    t_strategy = a4.create_task(strategy, context=[t_market, t_risk, t_finance])
    t_report = a5.create_task(
        writer, context=[t_market, t_risk, t_finance, t_strategy]
    )

    finished = {"count": 0}

    def after_each_task(output):
        """Runs after every task: updates the UI and pauses to respect Groq rate limits."""
        finished["count"] += 1
        if on_task_done:
            on_task_done(finished["count"], output)
        if pause_seconds and finished["count"] < len(AGENT_NAMES):
            time.sleep(pause_seconds)

    return Crew(
        agents=[market, risk, finance, strategy, writer],
        tasks=[t_market, t_risk, t_finance, t_strategy, t_report],
        process=Process.sequential,
        max_rpm=10,  # at most 10 LLM calls per minute
        task_callback=after_each_task,
        verbose=False,
    )


def run_crew(llm, inputs: dict, pause_seconds: int = 0, on_task_done=None):
    """Run the whole team. Returns (final_report, list_of_each_agent_output)."""
    crew = build_crew(llm, pause_seconds, on_task_done)
    result = crew.kickoff(inputs=inputs)
    steps = [t.raw for t in result.tasks_output]
    return result.raw, steps
