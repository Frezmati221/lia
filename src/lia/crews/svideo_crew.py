from crewai import Agent, Crew, Knowledge, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool
import lia.tools.twitter as twitter_tools
import os
import re
from lia.tools.main_tools import TimeTool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai_tools import DallETool
from lia.tools.main_tools import ImageTool, ImageSearchTool, FetchImageTool
from crewai_tools import ScrapeWebsiteTool
from lia.tools.youtube import YoutubeUploadTool
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
from lia.tools.video import MakeVideoTool

from dotenv import load_dotenv

load_dotenv()




@CrewBase
class SVideoCrew():
	"""SVideo crew"""

	agents_config = '../config/svideo/agents.yaml'
	tasks_config = '../config/svideo/tasks.yaml'

	@agent
	def topic_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['topic_researcher'],
			verbose=True,
			tools=[SerperDevTool(), ScrapeWebsiteTool()]
		)

	@agent
	def plot_maker(self) -> Agent:
		return Agent(
			config=self.agents_config['plot_maker'],
			verbose=True,
			tools=[SerperDevTool(), ScrapeWebsiteTool()]

		)
	
	@agent
	def image_generator(self) -> Agent:
		return Agent(
			config=self.agents_config['image_generator'],
			verbose=True,
			tools=[ImageTool(), ImageSearchTool(), FetchImageTool()]
		)

	@agent
	def video_maker(self) -> Agent:
		return Agent(
			config=self.agents_config['video_maker'],
			verbose=True,
			tools=[MakeVideoTool()]
		)
	
	@agent
	def logger(self) -> Agent:
		return Agent(
			config=self.agents_config['logger'],
			verbose=True,
		)
	
	@agent
	def video_uploader(self) -> Agent:
		return Agent(
			config=self.agents_config['video_uploader'],
			verbose=True,
			tools=[YoutubeUploadTool()]
		)

	@task
	def topic_researcher_task(self) -> Task:
		# Determine the next available log file name
		log_dir = os.getenv('VIDEO_EXCLUDE_TOPICS_PATH') + "/"
		base_filename = 'svideo_exclude_topic'
		extension = '.txt'
		
		existing_files = os.listdir(log_dir)
		log_numbers = [
			int(re.search(rf"{base_filename}_(\d+){extension}", f).group(1))
			for f in existing_files 
			if re.match(rf"{base_filename}_(\d+){extension}", f)
		]
		next_number = max(log_numbers, default=0) + 1
		next_log_file = f"{log_dir}{base_filename}_{next_number}{extension}"
		
		return Task(
			config=self.tasks_config['topic_researcher_task'],
			output_file=next_log_file,
		)
	
	@task
	def plot_maker_task(self) -> Task:
		return Task(
			config=self.tasks_config['plot_maker_task'],
			output_file="svideo/svideo_plot.txt",
		)
	
	@task
	def image_generator_task(self) -> Task:
		return Task(
			config=self.tasks_config['image_generator_task'],
		)
	
	@task
	def video_maker_task(self) -> Task:
		return Task(
			config=self.tasks_config['video_maker_task'],
		)
	

	
	@task
	def logger_task(self) -> Task:
		# Determine the next available log file name
		log_dir = os.getenv('YOUTUBE_LOGS_PATH') + "/"
		base_filename = 'logs_youtube'
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
	
	@task
	def video_uploader_task(self) -> Task:
		return Task(
			config=self.tasks_config['video_uploader_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Lia crew"""

		return Crew(
			agents=self.agents, 
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
			# planning=True,
			# planning_llm=ChatOpenAI(model="gpt-4o")
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
