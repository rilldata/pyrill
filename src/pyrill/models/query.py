"""
Pydantic models for Rill query requests and responses

This module contains all query-related models including:
- Query request models (MetricsQuery, MetricsSqlQuery, SqlQuery)
- Query building blocks (Expression, Condition, Dimension, Measure, etc.)
- Query result models (QueryResult)
- Supporting enums and types (Operator, TimeGrain)
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel


class Operator(str, Enum):
    """Comparison or logical operator for query expressions"""
    UNSPECIFIED = ""
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    IN = "in"
    NIN = "nin"
    ILIKE = "ilike"
    NILIKE = "nilike"
    OR = "or"
    AND = "and"


class TimeGrain(str, Enum):
    """Time granularity for time-based operations"""
    UNSPECIFIED = ""
    MILLISECOND = "millisecond"
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class Expression(BaseModel):
    """
    Expression for filtering, conditions, or computed values.

    An expression can be:
    - A named field reference
    - A constant value
    - A condition (logical/comparison operation)
    - A subquery

    Example:
        >>> # Simple field reference
        >>> expr = Expression(name="publisher")

        >>> # Constant value
        >>> expr = Expression(val="example.com")

        >>> # Condition
        >>> expr = Expression(
        ...     cond=Condition(
        ...         op=Operator.EQ,
        ...         exprs=[Expression(name="publisher"), Expression(val="example.com")]
        ...     )
        ... )
    """
    name: Optional[str] = None
    val: Optional[Any] = None
    cond: Optional["Condition"] = None
    subquery: Optional["Subquery"] = None

    model_config = {"extra": "forbid"}


class Condition(BaseModel):
    """
    Condition combining expressions with an operator.

    Example:
        >>> # publisher = 'example.com'
        >>> cond = Condition(
        ...     op=Operator.EQ,
        ...     exprs=[Expression(name="publisher"), Expression(val="example.com")]
        ... )

        >>> # clicks > 100 AND impressions > 1000
        >>> cond = Condition(
        ...     op=Operator.AND,
        ...     exprs=[
        ...         Expression(cond=Condition(op=Operator.GT, exprs=[Expression(name="clicks"), Expression(val=100)])),
        ...         Expression(cond=Condition(op=Operator.GT, exprs=[Expression(name="impressions"), Expression(val=1000)]))
        ...     ]
        ... )
    """
    op: Operator
    exprs: Optional[List[Expression]] = None

    model_config = {"extra": "forbid"}


class DimensionComputeTimeFloor(BaseModel):
    """Time floor computation for dimension"""
    dimension: str
    grain: TimeGrain

    model_config = {"extra": "forbid"}


class DimensionCompute(BaseModel):
    """Computation to apply to a dimension"""
    time_floor: Optional[DimensionComputeTimeFloor] = None

    model_config = {"extra": "forbid"}


class Dimension(BaseModel):
    """
    Dimension for grouping query results.

    Example:
        >>> # Simple dimension
        >>> dim = Dimension(name="publisher")

        >>> # Time-floored dimension
        >>> dim = Dimension(
        ...     name="timestamp_day",
        ...     compute=DimensionCompute(
        ...         time_floor=DimensionComputeTimeFloor(
        ...             dimension="timestamp",
        ...             grain=TimeGrain.DAY
        ...         )
        ...     )
        ... )
    """
    name: str
    compute: Optional[DimensionCompute] = None

    model_config = {"extra": "forbid"}


class MeasureComputeCountDistinct(BaseModel):
    """Count distinct values of a dimension"""
    dimension: str

    model_config = {"extra": "forbid"}


class MeasureComputeComparisonValue(BaseModel):
    """Get comparison value for a measure"""
    measure: str

    model_config = {"extra": "forbid"}


class MeasureComputeComparisonDelta(BaseModel):
    """Get delta between current and comparison value"""
    measure: str

    model_config = {"extra": "forbid"}


class MeasureComputeComparisonRatio(BaseModel):
    """Get ratio between current and comparison value"""
    measure: str

    model_config = {"extra": "forbid"}


class MeasureComputePercentOfTotal(BaseModel):
    """Calculate percentage of total"""
    measure: str
    total: Optional[float] = None

    model_config = {"extra": "forbid"}


class MeasureComputeURI(BaseModel):
    """Generate URI for a dimension"""
    dimension: str

    model_config = {"extra": "forbid"}


class MeasureCompute(BaseModel):
    """
    Computation to apply to a measure.

    Supports various aggregations and comparisons.

    Example:
        >>> # Simple count
        >>> compute = MeasureCompute(count=True)

        >>> # Count distinct
        >>> compute = MeasureCompute(
        ...     count_distinct=MeasureComputeCountDistinct(dimension="user_id")
        ... )

        >>> # Comparison delta
        >>> compute = MeasureCompute(
        ...     comparison_delta=MeasureComputeComparisonDelta(measure="revenue")
        ... )
    """
    count: Optional[bool] = None
    count_distinct: Optional[MeasureComputeCountDistinct] = None
    comparison_value: Optional[MeasureComputeComparisonValue] = None
    comparison_delta: Optional[MeasureComputeComparisonDelta] = None
    comparison_ratio: Optional[MeasureComputeComparisonRatio] = None
    percent_of_total: Optional[MeasureComputePercentOfTotal] = None
    uri: Optional[MeasureComputeURI] = None

    model_config = {"extra": "forbid"}


class Measure(BaseModel):
    """
    Measure for aggregation in query results.

    Example:
        >>> # Simple measure reference
        >>> measure = Measure(name="total_clicks")

        >>> # Computed measure
        >>> measure = Measure(
        ...     name="unique_users",
        ...     compute=MeasureCompute(
        ...         count_distinct=MeasureComputeCountDistinct(dimension="user_id")
        ...     )
        ... )
    """
    name: str
    compute: Optional[MeasureCompute] = None

    model_config = {"extra": "forbid"}


class Subquery(BaseModel):
    """
    Subquery for complex filtering.

    Example:
        >>> subquery = Subquery(
        ...     dimension=Dimension(name="publisher"),
        ...     measures=[Measure(name="clicks")],
        ...     where=Expression(
        ...         cond=Condition(
        ...             op=Operator.GT,
        ...             exprs=[Expression(name="clicks"), Expression(val=1000)]
        ...         )
        ...     )
        ... )
    """
    dimension: Dimension
    measures: List[Measure]
    where: Optional[Expression] = None
    having: Optional[Expression] = None

    model_config = {"extra": "forbid"}


class Sort(BaseModel):
    """
    Sort specification for query results.

    Example:
        >>> # Ascending by clicks
        >>> sort = Sort(name="clicks", desc=False)

        >>> # Descending by revenue
        >>> sort = Sort(name="revenue", desc=True)
    """
    name: str
    desc: bool = False

    model_config = {"extra": "forbid"}


class TimeRange(BaseModel):
    """
    Time range specification for queries.

    Supports various ways to specify time ranges:
    - Absolute: start + end timestamps
    - Relative: ISO duration + offset
    - Expression: Dynamic range expression

    Example:
        >>> # Absolute range
        >>> time_range = TimeRange(
        ...     start="2024-01-01T00:00:00Z",
        ...     end="2024-01-31T23:59:59Z"
        ... )

        >>> # Relative range (last 7 days)
        >>> time_range = TimeRange(
        ...     iso_duration="P7D",
        ...     round_to_grain=TimeGrain.DAY
        ... )

        >>> # Expression-based
        >>> time_range = TimeRange(expression="LAST_7_DAYS")
    """
    start: Optional[str] = None
    end: Optional[str] = None
    iso_duration: Optional[str] = None
    iso_offset: Optional[str] = None
    expression: Optional[str] = None
    round_to_grain: Optional[TimeGrain] = None

    model_config = {"extra": "forbid"}


class TimeSpine(BaseModel):
    """Time spine for generating regular time intervals"""
    start: str
    end: str
    grain: TimeGrain

    model_config = {"extra": "forbid"}


class WhereSpine(BaseModel):
    """Where clause for spine filtering"""
    expr: Optional[Expression] = None

    model_config = {"extra": "forbid"}


class Spine(BaseModel):
    """
    Spine for generating base query structure.

    Can be time-based or condition-based.
    """
    time: Optional[TimeSpine] = None
    where: Optional[WhereSpine] = None

    model_config = {"extra": "forbid"}


class MetricsQuery(BaseModel):
    """
    Structured metrics query request.

    This is the main query interface for exploring metrics views.

    Example:
        >>> query = MetricsQuery(
        ...     metrics_view="ad_bids_metrics",
        ...     dimensions=[Dimension(name="publisher")],
        ...     measures=[Measure(name="bid_price")],
        ...     time_range=TimeRange(expression="LAST_7_DAYS"),
        ...     sort=[Sort(name="bid_price", desc=True)],
        ...     limit=100
        ... )
    """
    metrics_view: str
    dimensions: Optional[List[Dimension]] = None
    measures: Optional[List[Measure]] = None
    where: Optional[Expression] = None
    having: Optional[Expression] = None
    time_range: Optional[TimeRange] = None
    comparison_time_range: Optional[TimeRange] = None
    spine: Optional[Spine] = None
    sort: Optional[List[Sort]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    pivot_on: Optional[List[str]] = None
    time_zone: Optional[str] = None
    use_display_names: Optional[bool] = None
    rows: Optional[bool] = None

    model_config = {"extra": "forbid"}


class MetricsSqlQuery(BaseModel):
    """
    SQL query with metrics context.

    Allows SQL queries that reference metrics view context.

    Example:
        >>> query = MetricsSqlQuery(
        ...     sql="SELECT publisher, SUM(bid_price) as total FROM metrics WHERE clicks > 100 GROUP BY publisher",
        ...     additional_where=Expression(
        ...         cond=Condition(
        ...             op=Operator.GT,
        ...             exprs=[Expression(name="timestamp"), Expression(val="2024-01-01")]
        ...         )
        ...     )
        ... )
    """
    sql: str
    additional_where: Optional[Expression] = None

    model_config = {"extra": "forbid"}


class SqlQuery(BaseModel):
    """
    Raw SQL query request (admin-only).

    Execute arbitrary SQL against the project's data warehouse.
    Access is restricted to administrators.

    Example:
        >>> query = SqlQuery(
        ...     sql="SELECT * FROM ad_bids LIMIT 100",
        ...     connector="duckdb"
        ... )
    """
    sql: str
    connector: Optional[str] = None

    model_config = {"extra": "forbid"}


class QueryResult(BaseModel):
    """
    Query result response.

    Contains rows of data returned from a query.

    Example result structure:
        >>> result = QueryResult(data=[
        ...     {"publisher": "example.com", "clicks": 1000, "revenue": 500.0},
        ...     {"publisher": "test.com", "clicks": 800, "revenue": 400.0}
        ... ])
    """
    data: List[Dict[str, Any]]

    model_config = {"extra": "allow"}
