"""
QueryBuilder - Fluent API for constructing MetricsQuery objects

Provides a clean, streamlined interface for building queries with:
- Simple types (strings, lists, dicts)
- Clear validation errors
- Progressive disclosure (simple queries are simple, complex queries possible)
- Fluent chaining API
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, timezone

from .models import (
    MetricsQuery,
    Dimension,
    Measure,
    Expression,
    Condition,
    Operator,
    TimeRange,
    TimeGrain,
    Sort,
    DimensionCompute,
    DimensionComputeTimeFloor,
    MeasureCompute,
    MeasureComputeCountDistinct,
)


class QueryBuilder:
    """
    Fluent builder for constructing MetricsQuery objects.

    Accepts simple types and handles internal complexity, providing clear
    validation errors. All methods return self for chaining (except .build()).

    Example:
        >>> query = (QueryBuilder()
        ...     .metrics_view('bids_metrics')
        ...     .dimensions(['advertiser_name', 'device_type'])
        ...     .measures(['overall_spend', 'total_bids'])
        ...     .where({"op": "eq", "field": "device_type", "value": "mobile"})
        ...     .time_range({"iso_duration": "P7D"})
        ...     .sort('overall_spend', desc=True)
        ...     .limit(20)
        ...     .build())
    """

    def __init__(self):
        """Initialize empty query builder."""
        self._metrics_view: Optional[str] = None
        self._dimensions: List[Union[str, Dimension]] = []
        self._measures: List[Union[str, Measure]] = []
        self._where: Optional[Expression] = None
        self._having: Optional[Expression] = None
        self._time_range: Optional[TimeRange] = None
        self._comparison_time_range: Optional[TimeRange] = None
        self._sorts: List[Sort] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._pivot_on: Optional[List[str]] = None
        self._time_zone: Optional[str] = None
        self._use_display_names: Optional[bool] = None

    def metrics_view(self, name: str) -> "QueryBuilder":
        """
        Set the metrics view name.

        Args:
            name: Metrics view name

        Returns:
            Self for chaining

        Example:
            >>> builder.metrics_view('bids_metrics')
        """
        self._metrics_view = name
        return self

    def dimensions(self, names: Union[str, List[str]]) -> "QueryBuilder":
        """
        Add dimension(s) by name. Can be called multiple times to accumulate.

        Args:
            names: Single dimension name or list of dimension names

        Returns:
            Self for chaining

        Example:
            >>> builder.dimensions('advertiser_name')
            >>> builder.dimensions(['device_type', 'device_region'])
        """
        if isinstance(names, str):
            names = [names]
        self._dimensions.extend(names)
        return self

    def dimension(
        self, name: str, compute: Optional[dict] = None
    ) -> "QueryBuilder":
        """
        Add a single dimension with optional compute specification.

        Args:
            name: Dimension name
            compute: Optional compute dict for complex dimensions

        Returns:
            Self for chaining

        Example:
            >>> # Simple dimension
            >>> builder.dimension('advertiser_name')
            >>> # Time-floored dimension
            >>> builder.dimension('timestamp_day', {
            ...     "time_floor": {
            ...         "dimension": "__time",
            ...         "grain": "day"
            ...     }
            ... })
        """
        if compute is None:
            self._dimensions.append(name)
        else:
            dim = self._dict_to_dimension(name, compute)
            self._dimensions.append(dim)
        return self

    def measures(self, names: Union[str, List[str]]) -> "QueryBuilder":
        """
        Add measure(s) by name. Can be called multiple times to accumulate.

        Args:
            names: Single measure name or list of measure names

        Returns:
            Self for chaining

        Example:
            >>> builder.measures('overall_spend')
            >>> builder.measures(['total_bids', 'impressions'])
        """
        if isinstance(names, str):
            names = [names]
        self._measures.extend(names)
        return self

    def measure(
        self, name: str, compute: Optional[dict] = None
    ) -> "QueryBuilder":
        """
        Add a single measure with optional compute specification.

        Args:
            name: Measure name
            compute: Optional compute dict for complex measures

        Returns:
            Self for chaining

        Example:
            >>> # Simple measure
            >>> builder.measure('overall_spend')
            >>> # Computed measure
            >>> builder.measure('unique_users', {
            ...     "count_distinct": {
            ...         "dimension": "user_id"
            ...     }
            ... })
        """
        if compute is None:
            self._measures.append(name)
        else:
            meas = self._dict_to_measure(name, compute)
            self._measures.append(meas)
        return self

    def where(self, filter_dict: dict) -> "QueryBuilder":
        """
        Set WHERE filter from dict.

        Args:
            filter_dict: Filter specification dict

        Returns:
            Self for chaining

        Example:
            >>> builder.where({"op": "eq", "field": "device_type", "value": "mobile"})
            >>> builder.where({"op": "in", "field": "device_region", "values": ["US", "GB"]})
            >>> builder.where({
            ...     "op": "and",
            ...     "conditions": [
            ...         {"op": "eq", "field": "device_type", "value": "mobile"},
            ...         {"op": "in", "field": "device_region", "values": ["US", "GB"]}
            ...     ]
            ... })
        """
        self._validate_where_dict(filter_dict)
        self._where = self._dict_to_expression(filter_dict)
        return self

    def having(self, having_dict: dict) -> "QueryBuilder":
        """
        Set HAVING filter from dict.

        Args:
            having_dict: HAVING filter specification dict

        Returns:
            Self for chaining

        Example:
            >>> builder.having({"op": "gt", "field": "total_spend", "value": 1000})
        """
        self._validate_where_dict(having_dict)
        self._having = self._dict_to_expression(having_dict)
        return self

    def time_range(self, range_dict: dict) -> "QueryBuilder":
        """
        Set time range from dict.

        Accepts various formats:
        - Absolute: {"start": "2024-01-01", "end": "2024-01-31"}
        - Absolute with datetime: {"start": datetime(2024, 1, 1), "end": datetime(2024, 1, 31)}
        - Absolute with date: {"start": date(2024, 1, 1), "end": date(2024, 1, 31)}
        - Relative: {"iso_duration": "P7D"}
        - Expression: {"expression": "P7D"}

        Args:
            range_dict: Time range specification dict

        Returns:
            Self for chaining

        Example:
            >>> builder.time_range({"start": "2024-01-01", "end": "2024-01-31"})
            >>> builder.time_range({"iso_duration": "P7D"})
            >>> builder.time_range({"start": datetime(2024, 1, 1), "end": datetime(2024, 1, 31)})
        """
        self._validate_time_range_dict(range_dict)
        self._time_range = self._dict_to_time_range(range_dict)
        return self

    def comparison_time_range(self, range_dict: dict) -> "QueryBuilder":
        """
        Set comparison time range from dict.

        Args:
            range_dict: Time range specification dict

        Returns:
            Self for chaining

        Example:
            >>> builder.comparison_time_range({"iso_duration": "P7D", "iso_offset": "P7D"})
        """
        self._validate_time_range_dict(range_dict)
        self._comparison_time_range = self._dict_to_time_range(range_dict)
        return self

    def sort(self, name: str, desc: bool = False) -> "QueryBuilder":
        """
        Add a sort. Can be called multiple times.

        Args:
            name: Field name to sort by
            desc: Sort descending if True, ascending if False

        Returns:
            Self for chaining

        Example:
            >>> builder.sort('overall_spend', desc=True)
            >>> builder.sort('advertiser_name')
        """
        self._sorts.append(Sort(name=name, desc=desc))
        return self

    def sorts(self, sort_list: List[dict]) -> "QueryBuilder":
        """
        Add multiple sorts from list.

        Args:
            sort_list: List of sort dicts with 'name' and optional 'desc'

        Returns:
            Self for chaining

        Example:
            >>> builder.sorts([
            ...     {"name": "timestamp_day", "desc": False},
            ...     {"name": "overall_spend", "desc": True}
            ... ])
        """
        for sort_dict in sort_list:
            if "name" not in sort_dict:
                raise ValueError("Each sort dict must have a 'name' key")
            name = sort_dict["name"]
            desc = sort_dict.get("desc", False)
            self._sorts.append(Sort(name=name, desc=desc))
        return self

    def limit(self, n: int) -> "QueryBuilder":
        """
        Set result limit.

        Args:
            n: Maximum number of results

        Returns:
            Self for chaining

        Example:
            >>> builder.limit(100)
        """
        self._limit = n
        return self

    def offset(self, n: int) -> "QueryBuilder":
        """
        Set result offset.

        Args:
            n: Number of results to skip

        Returns:
            Self for chaining

        Example:
            >>> builder.offset(50)
        """
        self._offset = n
        return self

    def pivot_on(self, columns: List[str]) -> "QueryBuilder":
        """
        Set pivot columns.

        Args:
            columns: List of column names to pivot on

        Returns:
            Self for chaining

        Example:
            >>> builder.pivot_on(['device_type'])
        """
        self._pivot_on = columns
        return self

    def time_zone(self, tz: str) -> "QueryBuilder":
        """
        Set time zone.

        Args:
            tz: Time zone string (e.g., 'America/New_York')

        Returns:
            Self for chaining

        Example:
            >>> builder.time_zone('America/New_York')
        """
        self._time_zone = tz
        return self

    def use_display_names(self, enabled: bool = True) -> "QueryBuilder":
        """
        Toggle display names.

        Args:
            enabled: Use display names if True

        Returns:
            Self for chaining

        Example:
            >>> builder.use_display_names(True)
        """
        self._use_display_names = enabled
        return self

    def build(self) -> MetricsQuery:
        """
        Build and validate the final MetricsQuery.

        Returns:
            MetricsQuery object

        Raises:
            ValueError: If metrics_view is not set

        Example:
            >>> query = builder.build()
        """
        if not self._metrics_view:
            raise ValueError("metrics_view is required. Call .metrics_view(name) first.")

        # Convert dimensions to proper format
        dimensions = []
        for dim in self._dimensions:
            if isinstance(dim, str):
                dimensions.append(Dimension(name=dim))
            else:
                dimensions.append(dim)

        # Convert measures to proper format
        measures = []
        for meas in self._measures:
            if isinstance(meas, str):
                measures.append(Measure(name=meas))
            else:
                measures.append(meas)

        return MetricsQuery(
            metrics_view=self._metrics_view,
            dimensions=dimensions if dimensions else None,
            measures=measures if measures else None,
            where=self._where,
            having=self._having,
            time_range=self._time_range,
            comparison_time_range=self._comparison_time_range,
            sort=self._sorts if self._sorts else None,
            limit=self._limit,
            offset=self._offset,
            pivot_on=self._pivot_on,
            time_zone=self._time_zone,
            use_display_names=self._use_display_names,
        )

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_where_dict(self, d: dict) -> None:
        """
        Validate where/having filter dict structure.

        Args:
            d: Filter dict to validate

        Raises:
            ValueError: If dict structure is invalid
        """
        if not isinstance(d, dict):
            raise ValueError("Filter must be a dict")

        if "op" not in d:
            raise ValueError(
                "Missing required key 'op' in filter dict. "
                "Example: {\"op\": \"eq\", \"field\": \"device_type\", \"value\": \"mobile\"}"
            )

        op = d["op"]
        valid_ops = ["eq", "neq", "lt", "lte", "gt", "gte", "in", "nin", "ilike", "nilike", "and", "or"]
        if op not in valid_ops:
            raise ValueError(
                f"Invalid operator '{op}'. Supported: {', '.join(valid_ops)}"
            )

        # Validate structure based on operator
        if op in ["and", "or"]:
            if "conditions" not in d:
                raise ValueError(
                    f"For '{op}' operator, provide 'conditions' (list of dicts). "
                    f"Example: {{\"op\": \"{op}\", \"conditions\": [{{...}}, {{...}}]}}"
                )
            if not isinstance(d["conditions"], list):
                raise ValueError(f"'conditions' must be a list for '{op}' operator")
            # Recursively validate nested conditions
            for cond in d["conditions"]:
                self._validate_where_dict(cond)
        elif op in ["in", "nin"]:
            if "field" not in d:
                raise ValueError(f"Missing 'field' key for '{op}' operator")
            if "values" not in d:
                raise ValueError(
                    f"For '{op}' operator, use 'values' (list) not 'value'. "
                    f"Example: {{\"op\": \"{op}\", \"field\": \"region\", \"values\": [\"US\", \"GB\"]}}"
                )
        else:
            # Comparison operators: eq, neq, lt, lte, gt, gte, ilike, nilike
            if "field" not in d:
                raise ValueError(f"Missing 'field' key for '{op}' operator")
            if "value" not in d:
                raise ValueError(
                    f"Missing 'value' key for '{op}' operator. "
                    f"Example: {{\"op\": \"{op}\", \"field\": \"clicks\", \"value\": 100}}"
                )

    def _validate_time_range_dict(self, d: dict) -> None:
        """
        Validate time range dict structure.

        Args:
            d: Time range dict to validate

        Raises:
            ValueError: If dict structure is invalid
        """
        if not isinstance(d, dict):
            raise ValueError("Time range must be a dict")

        has_absolute = "start" in d or "end" in d
        has_duration = "iso_duration" in d
        has_expression = "expression" in d

        # Count how many time range types are specified
        specified_count = sum([has_absolute, has_duration, has_expression])

        if specified_count == 0:
            raise ValueError(
                "Time range requires one of: (start+end), iso_duration, or expression. "
                "Examples:\n"
                "  Absolute: {\"start\": \"2024-01-01\", \"end\": \"2024-01-31\"}\n"
                "  Relative: {\"iso_duration\": \"P7D\"}\n"
                "  Expression: {\"expression\": \"P7D\"}"
            )

        if specified_count > 1:
            raise ValueError(
                "Time range cannot combine multiple types. Use only one of: "
                "(start+end), iso_duration, or expression"
            )

        # Validate absolute range
        if has_absolute:
            if "start" not in d or "end" not in d:
                raise ValueError(
                    "Absolute time range requires both 'start' and 'end'. "
                    "Example: {\"start\": \"2024-01-01\", \"end\": \"2024-01-31\"}"
                )
            # Validate types
            for key in ["start", "end"]:
                value = d[key]
                if not isinstance(value, (str, datetime, date)):
                    raise ValueError(
                        f"'{key}' must be str, datetime.datetime, or datetime.date. "
                        f"Got: {type(value).__name__}"
                    )

        # Validate grain if present
        if "round_to_grain" in d:
            grain = d["round_to_grain"]
            valid_grains = ["millisecond", "second", "minute", "hour", "day", "week", "month", "quarter", "year"]
            if grain not in valid_grains:
                raise ValueError(
                    f"Invalid grain '{grain}'. Supported: {', '.join(valid_grains)}"
                )

    # ========================================================================
    # Conversion Methods
    # ========================================================================

    def _dict_to_expression(self, d: dict) -> Expression:
        """
        Convert filter dict to Expression.

        Args:
            d: Filter dict

        Returns:
            Expression object
        """
        op_str = d["op"]
        op = Operator(op_str)

        if op in [Operator.AND, Operator.OR]:
            # Logical operators with nested conditions
            conditions = d["conditions"]
            exprs = [self._dict_to_expression(cond) for cond in conditions]
            return Expression(cond=Condition(op=op, exprs=exprs))
        elif op in [Operator.IN, Operator.NIN]:
            # IN/NIN operators
            field = d["field"]
            values = d["values"]
            return Expression(
                cond=Condition(
                    op=op,
                    exprs=[
                        Expression(name=field),
                        Expression(val=values)
                    ]
                )
            )
        else:
            # Comparison operators: eq, neq, lt, lte, gt, gte, ilike, nilike
            field = d["field"]
            value = d["value"]
            return Expression(
                cond=Condition(
                    op=op,
                    exprs=[
                        Expression(name=field),
                        Expression(val=value)
                    ]
                )
            )

    def _dict_to_time_range(self, d: dict) -> TimeRange:
        """
        Convert time range dict to TimeRange.

        Automatically converts Python date/datetime objects to ISO strings.

        Args:
            d: Time range dict

        Returns:
            TimeRange object
        """
        # Make a copy to avoid modifying the input
        d = d.copy()

        # Convert datetime/date objects to ISO strings
        for key in ["start", "end"]:
            if key in d:
                value = d[key]
                if isinstance(value, datetime):
                    # Convert datetime to ISO format
                    d[key] = value.isoformat()
                elif isinstance(value, date):
                    # Convert date to datetime at midnight UTC, then to ISO format
                    dt = datetime.combine(value, datetime.min.time())
                    # Ensure UTC timezone
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    d[key] = dt.isoformat()

        # Convert grain string to TimeGrain enum if present
        if "round_to_grain" in d:
            d["round_to_grain"] = TimeGrain(d["round_to_grain"])

        return TimeRange(**d)

    def _dict_to_dimension(self, name: str, compute: dict) -> Dimension:
        """
        Convert dimension compute dict to Dimension object.

        Args:
            name: Dimension name
            compute: Compute specification dict

        Returns:
            Dimension object
        """
        if "time_floor" in compute:
            time_floor_dict = compute["time_floor"]
            dimension = time_floor_dict["dimension"]
            grain = TimeGrain(time_floor_dict["grain"])
            return Dimension(
                name=name,
                compute=DimensionCompute(
                    time_floor=DimensionComputeTimeFloor(
                        dimension=dimension,
                        grain=grain
                    )
                )
            )
        else:
            # Future: support other compute types
            raise ValueError(
                f"Unsupported dimension compute type. Supported: time_floor. "
                f"Got: {list(compute.keys())}"
            )

    def _dict_to_measure(self, name: str, compute: dict) -> Measure:
        """
        Convert measure compute dict to Measure object.

        Args:
            name: Measure name
            compute: Compute specification dict

        Returns:
            Measure object
        """
        if "count_distinct" in compute:
            count_distinct_dict = compute["count_distinct"]
            dimension = count_distinct_dict["dimension"]
            return Measure(
                name=name,
                compute=MeasureCompute(
                    count_distinct=MeasureComputeCountDistinct(dimension=dimension)
                )
            )
        else:
            # Future: support other compute types
            raise ValueError(
                f"Unsupported measure compute type. Supported: count_distinct. "
                f"Got: {list(compute.keys())}"
            )
