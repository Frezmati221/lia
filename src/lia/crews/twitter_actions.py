from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool
import lia.tools.twitter as twitter_tools
import os
import re
from lia.tools.main_tools import TimeTool
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from dotenv import load_dotenv

load_dotenv()
@CrewBase
class LiaTwitterActions():
	"""Lia crew"""

	agents_config = '../config/twitter_actions/agents.yaml'
	tasks_config = '../config/twitter_actions/tasks.yaml'

	@agent
	def tweets_searcher(self) -> Agent:
		return Agent(
			config=self.agents_config['tweets_searcher'],
			verbose=True,
			tools=[twitter_tools.SearchTweetsTool()],
		)
	
	@agent
	def tweets_reader(self) -> Agent:
		return Agent(
			config=self.agents_config['tweets_reader'],
			verbose=True,
		)
	
	@agent
	def tweets_quote_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['tweets_quote_writer'],
			verbose=True,
			tools=[twitter_tools.QuotePostTool()],
		)
		

	@agent
	def tweets_retweeter(self) -> Agent:
		return Agent(
			config=self.agents_config['tweets_retweeter'],
			verbose=True,
			tools=[twitter_tools.RetweetPostTool()],
		)
	
	@agent
	def logger(self) -> Agent:
		return Agent(
			config=self.agents_config['logger'],
			verbose=True,
		)

	@task
	def tweets_searcher_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweets_searcher_task'],
		)
	

	@task
	def tweets_reader_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweets_reader_task'],
		)
	
	@task
	def tweets_quote_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweets_quote_task'],
		)
	
	@task
	def tweets_retweet_task(self) -> Task:
		return Task(
			config=self.tasks_config['tweets_retweet_task'],
		)
	
	@task
	def logger_task(self) -> Task:
		# Determine the next available log file name
		log_dir = os.getenv('TWITTER_LOGS_PATH') + "/"
		base_filename = 'logs_twitter_actions'
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
			verbose=True,
			planning=True,
			planning_llm="gpt-4o-mini",
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
