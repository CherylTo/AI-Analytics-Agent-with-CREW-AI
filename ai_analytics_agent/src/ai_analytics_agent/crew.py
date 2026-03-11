from pathlib import Path
import pandas as pd
import numpy as np

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from ai_analytics_agent.models import (
    QueryPlan,
    ChartMetadata,
    InsightOutput,
    ValidationResult,
)
from ai_analytics_agent.tools.sql_executor import execute_query


@CrewBase
class AiAnalyticsAgent:
    """AiAnalyticsAgent crew with 4 agents: Manager, SQL, Visualization, Insight"""

    # YAML Configs
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Shared LLM
    llm = LLM(model="gpt-4o")

    # -----------------------------
    # Define Agents
    # -----------------------------
    @agent
    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config["manager"],
            llm=self.llm,
        )

    @agent
    def sql_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["sql_generator"],
            llm=self.llm,
        )

    @agent
    def visualizer(self) -> Agent:
        return Agent(
            config=self.agents_config["visualizer"],
            llm=self.llm,
        )

    @agent
    def insight_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["insight_generator"],
            llm=self.llm,
        )

    @agent
    def streamlit_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["streamlit_developer"],
            llm=self.llm,
        )

    # -----------------------------
    # Define Tasks
    # -----------------------------
    @task
    def manager_task(self) -> Task:
        return Task(
            config=self.tasks_config["manager_task"],
            output_pydantic=QueryPlan,
        )

    @task
    def sql_task(self) -> Task:
        return Task(
            config=self.tasks_config["sql_task"],
        )

    @task
    def sql_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["sql_validation_task"],
            output_pydantic=ValidationResult,
        )

    @task
    def visualization_task(self) -> Task:
        return Task(
            config=self.tasks_config["visualization_task"],
            output_pydantic=ChartMetadata,
        )

    @task
    def chart_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["chart_validation_task"],
            output_pydantic=ValidationResult,
        )

    @task
    def insight_task(self) -> Task:
        return Task(
            config=self.tasks_config["insight_task"],
            output_pydantic=InsightOutput,
        )

    @task
    def streamlit_task(self) -> Task:

        app_path = Path(__file__).resolve().parents[3] / "streamlit" / "app.py"
        existing_code = ""

        if app_path.exists():
            existing_code = app_path.read_text()

        description = self.tasks_config["streamlit_task"]["description"]
        if existing_code:
            description += f"\n\nThe existing app.py contents are:\n\n{existing_code}"

        return Task(
            config=self.tasks_config["streamlit_task"],
            description=description,
        )

    # -----------------------------
    # Define Crews
    # -----------------------------
    @crew
    def crew_sql(self) -> Crew:
        """Phase 1: Interpret question and generate SQL"""
        return Crew(
            agents=[self.sql_generator()],
            tasks=[self.manager_task(), self.sql_task(), self.sql_validation_task()],
            process=Process.hierarchical,
            manager_agent=self.manager(),
            manager_llm=self.llm,
            verbose=True,
        )

    @crew
    def crew_insights(self) -> Crew:
        """Phase 2: Visualize and generate insights from query results"""
        return Crew(
            agents=[self.visualizer(), self.insight_generator()],
            tasks=[
                self.visualization_task(),
                self.chart_validation_task(),
                self.insight_task(),
            ],
            process=Process.hierarchical,
            manager_agent=self.manager(),
            manager_llm=self.llm,
            verbose=True,
        )

    @crew
    def crew_streamlit(self) -> Crew:
        """One-time crew to generate or update the Streamlit app file"""
        return Crew(
            agents=[self.streamlit_developer()],
            tasks=[self.streamlit_task()],
            process=Process.sequential,
            verbose=True,
        )

    # -----------------------------
    # Main entry point
    # -----------------------------
    def run_ai_analytics(self, question: str):
        # Phase 1: Generate and validate SQL
        sql_result = self.crew_sql().kickoff(inputs={"question": question})
        sql_query = sql_result.tasks_output[1].raw  # sql_task output
        sql_query = (
            sql_query.strip()
            .removeprefix("```sql")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        # Retry loop if SQL generator returns prose instead of SQL
        max_retries = 3
        for attempt in range(max_retries):
            if sql_query.upper().startswith(("SELECT", "WITH")):
                break

            print(
                f"SQL Generator returned invalid output on attempt {attempt + 1}, retrying..."
            )

            retry_result = self.crew_sql().kickoff(
                inputs={
                    "question": question,
                    "feedback": f"Your previous response was not valid SQL. You returned: '{sql_query[:100]}'. You must return only a SELECT or WITH statement. Nothing else.",
                }
            )
            sql_query = retry_result.tasks_output[1].raw
            sql_query = (
                sql_query.strip()
                .removeprefix("```sql")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
        else:
            raise ValueError(
                f"SQL Generator failed to return valid SQL after {max_retries} attempts."
            )

        # Execute SQL outside the crew
        df = execute_query(sql_query)
        df = df.replace("None", np.nan).dropna(subset=[df.columns[0]])
        for col in df.columns[1:]:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().all():
                df[col] = converted

        if df.empty:
            return {
                "sql_query": sql_query,
                "dataframe": df,
                "chart_metadata": None,
                "insight": None,
                "error": "The query returned no results. Try rephrasing your question.",
            }

        # Phase 2: Visualize and generate insights
        final_result = self.crew_insights().kickoff(
            inputs={
                "question": question,
                "dataframe": df.to_json(orient="records"),
            }
        )

        chart_metadata = None
        insight = None
        for task_output in final_result.tasks_output:
            if isinstance(task_output.pydantic, ChartMetadata):
                chart_metadata = task_output.pydantic
            elif isinstance(task_output.pydantic, InsightOutput):
                insight = task_output.pydantic

        return {
            "sql_query": sql_query,
            "dataframe": df,
            "chart_metadata": chart_metadata,
            "insight": insight,
        }

    def generate_app(self):
        """Generate or update the Streamlit app file"""
        from pathlib import Path

        app_path = Path(__file__).resolve().parents[3] / "streamlit" / "app.py"
        app_path.parent.mkdir(parents=True, exist_ok=True)

        result = self.crew_streamlit().kickoff()
        app_code = result.raw

        # Strip any accidental code fences
        app_code = (
            app_code.strip()
            .removeprefix("```python")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        app_path.write_text(app_code)
        print(f"Streamlit app saved to {app_path}")
