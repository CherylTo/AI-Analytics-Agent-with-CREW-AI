#!/usr/bin/env python
import os
from pathlib import Path
import warnings
from dotenv import load_dotenv

from .crew import AiAnalyticsAgent

load_dotenv(Path(__file__).resolve().parents[3] / ".env")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

question = "Which state has the most canceled orders"


def generate_app():
    """One-time generation or update of the Streamlit app file"""
    agent = AiAnalyticsAgent()
    agent.generate_app()


def run(question: str):
    """
    Run the crew with a user question
    """
    try:
        agent = AiAnalyticsAgent()
        result = agent.run_ai_analytics(question=question)

        if result.get("error"):
            print(result["error"])
            return

        df = result["dataframe"]
        chart_metadata = result["chart_metadata"]
        insight = result["insight"]

        # Define output file
        output_dir = Path(__file__).resolve().parents[3] / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = str(output_dir / "ai_analytics_report.md")

        with open(output_file, "w") as f:
            f.write("# AI Analytics Report\n\n")
            f.write(f"**Question:** {question}\n\n")

            f.write("## SQL Query\n")
            f.write(f"```sql\n{result['sql_query']}\n```\n\n")

            f.write("## Data Sample\n")
            f.write(df.head().to_markdown())
            f.write("\n\n")

            f.write("## Chart Metadata\n")
            for key, value in chart_metadata.model_dump().items():
                f.write(f"- **{key}:** {value}\n")
            f.write("\n")

            f.write("## Summary\n")
            f.write(insight.summary + "\n\n")

            f.write("## Key Takeaway\n")
            f.write(insight.key_takeaway + "\n\n")

            if insight.anomalies:
                f.write("## Anomalies\n")
                f.write(insight.anomalies + "\n")

        print(f"Report saved to {output_file}")

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate_app":
        generate_app()
    else:
        question = sys.argv[1] if len(sys.argv) > 1 else question
        run(question)
