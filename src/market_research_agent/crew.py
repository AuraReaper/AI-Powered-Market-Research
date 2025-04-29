import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool


browser_tool = SerperDevTool()

llm = LLM(model="together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo",
          api_key=os.environ.get("TOGETHER_API_KEY"),
          base_url="https://api.together.xyz/v1"
        )

@CrewBase
class MarketResearchAgentCrew():
	"""MarketResearchAgent crew"""

	@agent
	def industry_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['industry_researcher'],
			tools=[browser_tool],
			llm=llm,
			verbose=True
		)

	@agent
	def use_case_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['use_case_analyst'],
			llm=llm,
			tools=[browser_tool],
			verbose=True
		)

	@agent
	def resource_collector(self) -> Agent:
		return Agent(
			config=self.agents_config['resource_collector'],
			llm=llm,
			tools=[browser_tool],
			verbose=True
		)

	@task
	def research_industry_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_industry_task'],
		)

	@task
	def market_standards_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['market_standards_analysis_task'],
		)

	@task
	def resource_collection_task(self) -> Task:
		return Task(
			config=self.tasks_config['resource_collection_task'],
			output_file='report.md'
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