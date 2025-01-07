from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from lia.tools.main_tools import TimeTool
from lia.tools.video import MakeVideoTool
from crewai_tools import DallETool

@CrewBase
class VideoGenerateCrew:
    """VideoGenerateCrew crew"""

    agents_config = '../config/video_generate/agents.yaml'
    tasks_config = '../config/video_generate/tasks.yaml'


    @agent
    def plot_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['plot_generator'],
            verbose=True,
        )

    @agent
    def video_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['video_generator'],
            verbose=True,
        )
    
    @agent
    def video_maker(self) -> Agent:
        return Agent(
            config=self.agents_config['video_maker'],
            verbose=True,
            tools=[MakeVideoTool()],
        )

    @task
    def generate_plot_task(self) -> Task:
        return Task(
			config=self.tasks_config['generate_plot_task'],
		)
    
    @task
    def generate_video_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_video_task'],
        )
    

    
    @task
    def make_video_task(self) -> Task:
        return Task(
            config=self.tasks_config['make_video_task'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the VideoGenerateCrew crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
      		planning=True,
			planning_llm="gpt-4o-mini",
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )