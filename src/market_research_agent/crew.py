import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
# from crewai_tools import EXASearchTool


serper_tool = SerperDevTool()
# exa_tool = EXASearchTool(api_key=os.getenv("EXA_API_KEY"))

llm = LLM(
    model="gemini/gemini-1.5-flash", 
    api_key=os.environ.get("API_KEY"),
)

@CrewBase
class MarketResearchAgentCrew():
	"""MarketResearchAgent crew"""

	@agent
	def industry_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['industry_researcher'],
			tools=[serper_tool],
			llm=llm,
			verbose=True
		)

	@agent
	def competitor_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_researcher'],
			llm=llm,
			tools=[serper_tool],
			verbose=True
		)

	@agent
	def impact_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['impact_writer'],
			llm=llm,
			tools=[serper_tool],
			verbose=True
		)

	@agent
	def use_case_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['use_case_analyst'],
			llm=llm,
			tools=[serper_tool],
			verbose=True
		)

	@agent
	def proposal_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['proposal_writer'],
			llm=llm,
			tools=[serper_tool],
			verbose=True
		)

	@task
	def research_industry_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_industry_task'],
		)

	@task
	def competitor_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_research_task'],
		)

	@task
	def competitor_benefit_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_benefit_analysis_task'],
		)

	@task
	def market_standards_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['market_standards_analysis_task'],
		)

	@task
	def final_proposal_compilation_task(self) -> Task:
		return Task(
			config=self.tasks_config['final_proposal_compilation_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the MarketResearchAgent crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)