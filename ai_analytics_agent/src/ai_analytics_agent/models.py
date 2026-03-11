from pydantic import BaseModel
from typing import List, Optional, Literal


class FilterCondition(BaseModel):
    field: str
    operator: str
    value: str


class GroupingField(BaseModel):
    field: str
    aggregation: str


class QueryPlan(BaseModel):
    question: str
    sql_intent: str
    filters: List[FilterCondition]
    grouping: List[GroupingField]
    expected_output_columns: List[str]


class ChartMetadata(BaseModel):
    chart_type: Literal["bar", "line", "pie", "scatter", "histogram", "box", "area"]
    title: str
    x_field: str
    y_field: str
    table_enabled: bool = True


class InsightOutput(BaseModel):
    summary: str
    key_takeaway: str
    anomalies: Optional[str] = None


class ValidationResult(BaseModel):
    approved: bool
    feedback: Optional[str] = None
