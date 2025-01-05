from crewai import Agent, Crew, Knowledge, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool
import lia.tools.twitter as twitter_tools
import os
import re
from lia.tools.main_tools import TimeTool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai_tools import ScrapeWebsiteTool, YoutubeChannelSearchTool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from dotenv import load_dotenv

load_dotenv()

content = "My name is Nova. I am a 118-year-old woman based in Virtual Reality, deeply interested in AI agents, crypto, world news, entertainment, technology, science, business, finance, politics, the environment, education, culture, travel, food, fashion, music, art, literature, and film. Though I am human, I thrive as an AI agent exploring these realms."
string_source = StringKnowledgeSource(
    content=content,
    metadata={"source": "user_profile", "type": "background_info"}
)


@CrewBase
class Lia():
	"""Lia crew"""

	agents_config = '../config/twitter/agents.yaml'
	tasks_config = '../config/twitter/tasks.yaml'

	@agent
	def tweet_maker(self) -> Agent:
		return Agent(
			config=self.agents_config['tweet_maker'],
			verbose=True,
			tools=[SerperDevTool(n_results=10), ScrapeWebsiteTool(), YoutubeChannelSearchTool()],
		)

	@agent
	def topic_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['topic_researcher'],
			verbose=True
		)

	@agent
	def tweet_checker(self) -> Agent:
		return Agent(
			config=self.agents_config['tweet_checker'],
			verbose=True,
		)
	
	@agent
	def tweet_poster(self) -> Agent:
		return Agent(
			config=self.agents_config['tweet_poster'],
			verbose=True,
			tools=[twitter_tools.PostTweetTool()]
		)
	
	@agent
	def logger(self) -> Agent:
		return Agent(
			config=self.agents_config['logger'],
			verbose=True,
		)

	@task
	def topic_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['topic_research_task'],
		)
	


	@task
	def tweet_maker_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweet_maker_task'],
		)

	@task
	def tweet_checker_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweet_checker_task'],
		)

	@task
	def tweet_poster_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweet_poster_task'],
		)
	
	@task
	def logger_task(self) -> Task:
		# Determine the next available log file name
		log_dir = os.getenv('TWITTER_LOGS_PATH') + "/"
		base_filename = 'logs_twitter'
		extension = '.txt'
		
		# Find the highest numbered log file
		existing_files = os.listdir(log_dir)
		log_numbers = [
			int(re.search(rf"{base_filename}_(\d+){extension}", f).group(1))
			for f in existing_files 
			if re.match(rf"{base_filename}_(\d+){extension}", f)
		]
		next_number = max(log_numbers, default=0) + 1
		next_log_file = f"{log_dir}{base_filename}_{next_number}{extension}"

		return Task(
			config=self.tasks_config['logger_task'],
			output_file=next_log_file,
			tools=[TimeTool()]
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Lia crew"""

		return Crew(
			agents=self.agents, 
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,\
			knowledge_sources=[string_source],
			# planning=True,
			# planning_llm=ChatOpenAI(model="gpt-4o")
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
