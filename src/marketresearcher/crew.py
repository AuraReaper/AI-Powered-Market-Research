from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, EXASearchTool
from config.llm import research_llm, comparison_llm, narrative_llm, strategic_llm, formatting_llm
from crewai_tools import FileWriterTool
from utils.output_manager import get_output_manager
import os

# Tool setup
serper = SerperDevTool()
exa = EXASearchTool()

# LLM configuration
from crewai import LLM
import os

llm = LLM(
    model="nvidia_nim/deepseek-ai/deepseek-r1",
    api_key=os.getenv("NVIDIA_NIM_API_KEY")
)

@CrewBase
class Marketresearcher():
	"""Marketresearcher crew"""
	
	def __init__(self):
		super().__init__()
		self.output_manager = get_output_manager()
		self._company_name = None
	
	def set_company_name(self, company_name: str):
		"""Set the company name for dynamic output file generation"""
		self._company_name = company_name
	
	def get_unique_output_path(self, company_name: str) -> str:
		"""Get unique output path for the given company"""
		return str(self.output_manager.get_report_path(company_name))

	# === Agents ===
	@agent
	def industry_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['industry_researcher'],
			tools=[exa, serper],
			llm=llm,
			verbose=True
		)

	@agent
	def competitor_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_researcher'],
			tools=[exa, serper],
			llm=llm,
			verbose=True
		)

	@agent
	def impact_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['impact_writer'],
			tools=[exa],
			llm=llm,
			verbose=True
		)

	@agent
	def use_case_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['use_case_analyst'],
			tools=[exa],
			llm=llm,
			verbose=True
		)

	@agent
	def proposal_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['proposal_writer'],
			tools=[FileWriterTool()],
			llm=llm,
			verbose=True
		)

	# === Tasks ===
	@task
	def research_industry_task(self) -> Task:
		return Task(config=self.tasks_config['research_industry_task'])

	@task
	def identify_top_competitors_task(self) -> Task:
		return Task(config=self.tasks_config['identify_top_competitors_task'])

	@task
	def analyze_competitor_ai_strategy_task(self) -> Task:
		return Task(config=self.tasks_config['analyze_competitor_ai_strategy_task'])

	@task
	def write_competitor_impact_articles_task(self) -> Task:
		return Task(config=self.tasks_config['write_competitor_impact_articles_task'])

	@task
	def propose_ai_use_cases_task(self) -> Task:
		return Task(config=self.tasks_config['propose_ai_use_cases_task'])

	@task
	def compile_final_proposal_task(self) -> Task:
		return Task(config=self.tasks_config['compile_final_proposal_task'])

	# === Crew ===
	@crew
	def crew(self) -> Crew:
		"""Creates the MarketResearchAgent crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True
		)