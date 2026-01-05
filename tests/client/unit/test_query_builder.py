"""
Unit tests for QueryBuilder
"""

import pytest
from datetime import datetime, date, timezone

from pyrill import QueryBuilder
from pyrill.models import (
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


class TestBasicQueryBuilding:
    """Test basic query construction with dimensions and measures."""

    def test_simple_query_with_lists(self):
        """Test basic query with dimensions and measures as lists."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name", "device_type"])
            .measures(["overall_spend", "total_bids"])
            .limit(20)
            .build()
        )

        assert isinstance(query, MetricsQuery)
        assert query.metrics_view == "bids_metrics"
        assert len(query.dimensions) == 2
        assert query.dimensions[0].name == "advertiser_name"
        assert query.dimensions[1].name == "device_type"
        assert len(query.measures) == 2
        assert query.measures[0].name == "overall_spend"
        assert query.measures[1].name == "total_bids"
        assert query.limit == 20

    def test_simple_query_with_strings(self):
        """Test that single strings work for dimensions and measures."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions("advertiser_name")
            .measures("overall_spend")
            .limit(10)
            .build()
        )

        assert len(query.dimensions) == 1
        assert query.dimensions[0].name == "advertiser_name"
        assert len(query.measures) == 1
        assert query.measures[0].name == "overall_spend"

    def test_accumulating_dimensions_and_measures(self):
        """Test that multiple calls accumulate dimensions and measures."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions("advertiser_name")
            .dimensions("device_type")
            .measures("overall_spend")
            .measures("total_bids")
            .build()
        )

        assert len(query.dimensions) == 2
        assert query.dimensions[0].name == "advertiser_name"
        assert query.dimensions[1].name == "device_type"
        assert len(query.measures) == 2
        assert query.measures[0].name == "overall_spend"
        assert query.measures[1].name == "total_bids"

    def test_mix_singular_and_plural_methods(self):
        """Test mixing .dimension() and .dimensions(), .measure() and .measures()."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension("advertiser_name")
            .dimension("device_type")
            .dimensions(["campaign_name", "creative_type"])
            .measure("overall_spend")
            .measures(["total_bids", "impressions"])
            .build()
        )

        assert len(query.dimensions) == 4
        assert query.dimensions[0].name == "advertiser_name"
        assert query.dimensions[1].name == "device_type"
        assert query.dimensions[2].name == "campaign_name"
        assert query.dimensions[3].name == "creative_type"
        assert len(query.measures) == 3
        assert query.measures[0].name == "overall_spend"
        assert query.measures[1].name == "total_bids"
        assert query.measures[2].name == "impressions"

    def test_method_chaining(self):
        """Test that all methods return self for chaining."""
        builder = QueryBuilder()
        result = builder.metrics_view("test")
        assert result is builder

        result = builder.dimensions(["dim1"])
        assert result is builder

        result = builder.measures(["measure1"])
        assert result is builder

        result = builder.limit(10)
        assert result is builder

    def test_missing_metrics_view_error(self):
        """Test that building without metrics_view raises error."""
        builder = QueryBuilder().dimensions(["dim1"])

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "metrics_view is required" in str(exc_info.value)


class TestDimensionWithCompute:
    """Test dimension() method with compute specifications."""

    def test_simple_dimension_no_compute(self):
        """Test .dimension() without compute - just adds simple dimension."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension("advertiser_name")
            .build()
        )

        assert len(query.dimensions) == 1
        assert query.dimensions[0].name == "advertiser_name"
        assert query.dimensions[0].compute is None

    def test_dimension_with_time_floor_day(self):
        """Test dimension with time_floor compute (day grain)."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension(
                "timestamp_day",
                {"time_floor": {"dimension": "__time", "grain": "day"}},
            )
            .build()
        )

        assert len(query.dimensions) == 1
        dim = query.dimensions[0]
        assert dim.name == "timestamp_day"
        assert dim.compute is not None
        assert dim.compute.time_floor is not None
        assert dim.compute.time_floor.dimension == "__time"
        assert dim.compute.time_floor.grain == TimeGrain.DAY

    def test_dimension_with_time_floor_hour(self):
        """Test dimension with time_floor compute (hour grain)."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension(
                "timestamp_hour",
                {"time_floor": {"dimension": "__time", "grain": "hour"}},
            )
            .build()
        )

        dim = query.dimensions[0]
        assert dim.compute.time_floor.grain == TimeGrain.HOUR

    def test_dimension_with_time_floor_month(self):
        """Test dimension with time_floor compute (month grain)."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension(
                "timestamp_month",
                {"time_floor": {"dimension": "__time", "grain": "month"}},
            )
            .build()
        )

        dim = query.dimensions[0]
        assert dim.compute.time_floor.grain == TimeGrain.MONTH

    def test_mix_simple_and_computed_dimensions(self):
        """Test mixing simple dimensions with time-floored dimensions."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension(
                "timestamp_day",
                {"time_floor": {"dimension": "__time", "grain": "day"}},
            )
            .dimension("advertiser_name")
            .dimensions(["device_type", "device_region"])
            .build()
        )

        assert len(query.dimensions) == 4
        assert query.dimensions[0].name == "timestamp_day"
        assert query.dimensions[0].compute is not None
        assert query.dimensions[1].name == "advertiser_name"
        assert query.dimensions[1].compute is None
        assert query.dimensions[2].name == "device_type"
        assert query.dimensions[3].name == "device_region"


class TestMeasureWithCompute:
    """Test measure() method with compute specifications."""

    def test_simple_measure_no_compute(self):
        """Test .measure() without compute - just adds simple measure."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .measure("overall_spend")
            .build()
        )

        assert len(query.measures) == 1
        assert query.measures[0].name == "overall_spend"
        assert query.measures[0].compute is None

    def test_measure_with_count_distinct(self):
        """Test measure with count_distinct compute."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .measure(
                "unique_users", {"count_distinct": {"dimension": "user_id"}}
            )
            .build()
        )

        assert len(query.measures) == 1
        meas = query.measures[0]
        assert meas.name == "unique_users"
        assert meas.compute is not None
        assert meas.compute.count_distinct is not None
        assert meas.compute.count_distinct.dimension == "user_id"

    def test_mix_simple_and_computed_measures(self):
        """Test mixing simple measures with computed measures."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .measure("overall_spend")
            .measure(
                "unique_users", {"count_distinct": {"dimension": "user_id"}}
            )
            .measures(["total_bids", "impressions"])
            .build()
        )

        assert len(query.measures) == 4
        assert query.measures[0].name == "overall_spend"
        assert query.measures[0].compute is None
        assert query.measures[1].name == "unique_users"
        assert query.measures[1].compute is not None
        assert query.measures[2].name == "total_bids"
        assert query.measures[3].name == "impressions"


class TestWhereFilters:
    """Test .where() with various filter structures."""

    def test_simple_equality_filter(self):
        """Test simple equality filter."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .where({"op": "eq", "field": "device_type", "value": "mobile"})
            .build()
        )

        assert query.where is not None
        assert query.where.cond is not None
        assert query.where.cond.op == Operator.EQ
        assert len(query.where.cond.exprs) == 2
        assert query.where.cond.exprs[0].name == "device_type"
        assert query.where.cond.exprs[1].val == "mobile"

    def test_in_operator_filter(self):
        """Test IN operator filter."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .where(
                {
                    "op": "in",
                    "field": "device_region",
                    "values": ["US", "GB", "CA"],
                }
            )
            .build()
        )

        assert query.where.cond.op == Operator.IN
        assert query.where.cond.exprs[0].name == "device_region"
        assert query.where.cond.exprs[1].val == ["US", "GB", "CA"]

    def test_greater_than_filter(self):
        """Test greater than comparison."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .where({"op": "gt", "field": "clicks", "value": 100})
            .build()
        )

        assert query.where.cond.op == Operator.GT
        assert query.where.cond.exprs[0].name == "clicks"
        assert query.where.cond.exprs[1].val == 100

    def test_and_filter(self):
        """Test AND filter with multiple conditions."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .where(
                {
                    "op": "and",
                    "conditions": [
                        {"op": "eq", "field": "device_type", "value": "mobile"},
                        {
                            "op": "in",
                            "field": "device_region",
                            "values": ["US", "GB"],
                        },
                    ],
                }
            )
            .build()
        )

        assert query.where.cond.op == Operator.AND
        assert len(query.where.cond.exprs) == 2
        # First condition: device_type = mobile
        assert query.where.cond.exprs[0].cond.op == Operator.EQ
        assert query.where.cond.exprs[0].cond.exprs[0].name == "device_type"
        assert query.where.cond.exprs[0].cond.exprs[1].val == "mobile"
        # Second condition: device_region IN [US, GB]
        assert query.where.cond.exprs[1].cond.op == Operator.IN
        assert query.where.cond.exprs[1].cond.exprs[0].name == "device_region"

    def test_or_filter(self):
        """Test OR filter with multiple conditions."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .where(
                {
                    "op": "or",
                    "conditions": [
                        {"op": "eq", "field": "device_type", "value": "mobile"},
                        {"op": "eq", "field": "device_type", "value": "tablet"},
                    ],
                }
            )
            .build()
        )

        assert query.where.cond.op == Operator.OR
        assert len(query.where.cond.exprs) == 2

    def test_nested_conditions(self):
        """Test nested AND/OR conditions."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .where(
                {
                    "op": "and",
                    "conditions": [
                        {
                            "op": "or",
                            "conditions": [
                                {
                                    "op": "eq",
                                    "field": "device_type",
                                    "value": "mobile",
                                },
                                {
                                    "op": "eq",
                                    "field": "device_type",
                                    "value": "tablet",
                                },
                            ],
                        },
                        {"op": "gt", "field": "clicks", "value": 100},
                    ],
                }
            )
            .build()
        )

        assert query.where.cond.op == Operator.AND
        # First condition is OR
        assert query.where.cond.exprs[0].cond.op == Operator.OR
        # Second condition is GT
        assert query.where.cond.exprs[1].cond.op == Operator.GT

    def test_where_validation_missing_op(self):
        """Test that missing 'op' raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.where({"field": "device_type", "value": "mobile"})

        assert "Missing required key 'op'" in str(exc_info.value)

    def test_where_validation_invalid_op(self):
        """Test that invalid operator raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.where(
                {"op": "invalid_op", "field": "device_type", "value": "mobile"}
            )

        assert "Invalid operator 'invalid_op'" in str(exc_info.value)

    def test_where_validation_in_without_values(self):
        """Test that IN operator without 'values' raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.where(
                {"op": "in", "field": "device_region", "value": "US"}
            )

        assert "use 'values' (list) not 'value'" in str(exc_info.value)

    def test_where_validation_and_without_conditions(self):
        """Test that AND operator without 'conditions' raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.where({"op": "and"})

        assert "provide 'conditions'" in str(exc_info.value)


class TestTimeRanges:
    """Test .time_range() with various formats."""

    def test_absolute_range_iso_strings_with_z(self):
        """Test absolute range with ISO strings (Z timezone)."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range(
                {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-31T23:59:59Z",
                }
            )
            .build()
        )

        assert query.time_range is not None
        assert query.time_range.start == "2024-01-01T00:00:00Z"
        assert query.time_range.end == "2024-01-31T23:59:59Z"

    def test_absolute_range_iso_strings_with_offset(self):
        """Test absolute range with ISO strings (offset timezone)."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range(
                {
                    "start": "2024-01-01T00:00:00+00:00",
                    "end": "2024-01-31T23:59:59+00:00",
                }
            )
            .build()
        )

        assert query.time_range.start == "2024-01-01T00:00:00+00:00"
        assert query.time_range.end == "2024-01-31T23:59:59+00:00"

    def test_absolute_range_iso_strings_no_timezone(self):
        """Test absolute range without timezone."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range(
                {
                    "start": "2024-01-01T00:00:00",
                    "end": "2024-01-31T23:59:59",
                }
            )
            .build()
        )

        assert query.time_range.start == "2024-01-01T00:00:00"
        assert query.time_range.end == "2024-01-31T23:59:59"

    def test_absolute_range_date_only_strings(self):
        """Test absolute range with date-only strings."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"start": "2024-01-01", "end": "2024-01-31"})
            .build()
        )

        assert query.time_range.start == "2024-01-01"
        assert query.time_range.end == "2024-01-31"

    def test_absolute_range_with_milliseconds(self):
        """Test absolute range with milliseconds."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range(
                {
                    "start": "2024-01-01T00:00:00.000Z",
                    "end": "2024-01-31T23:59:59.999Z",
                }
            )
            .build()
        )

        assert query.time_range.start == "2024-01-01T00:00:00.000Z"
        assert query.time_range.end == "2024-01-31T23:59:59.999Z"

    def test_absolute_range_with_datetime_objects(self):
        """Test absolute range with datetime objects."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 31, 23, 59, 59)

        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"start": start, "end": end})
            .build()
        )

        # Should convert to ISO format via .isoformat()
        assert query.time_range.start == start.isoformat()
        assert query.time_range.end == end.isoformat()

    def test_absolute_range_with_date_objects(self):
        """Test absolute range with date objects."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)

        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"start": start, "end": end})
            .build()
        )

        # Should convert to datetime at midnight UTC, then ISO format
        assert query.time_range.start is not None
        assert query.time_range.end is not None
        # Verify it's a valid ISO string
        assert "2024-01-01" in query.time_range.start
        assert "2024-01-31" in query.time_range.end

    def test_absolute_range_with_timezone_aware_datetime(self):
        """Test absolute range with timezone-aware datetime objects."""
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 31, 23, 59, 59, tzinfo=timezone.utc)

        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"start": start, "end": end})
            .build()
        )

        assert query.time_range.start == start.isoformat()
        assert query.time_range.end == end.isoformat()

    def test_mixing_string_and_datetime(self):
        """Test mixing string start with datetime end."""
        end = datetime(2024, 1, 31, 23, 59, 59)

        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"start": "2024-01-01", "end": end})
            .build()
        )

        assert query.time_range.start == "2024-01-01"
        assert query.time_range.end == end.isoformat()

    def test_iso_duration(self):
        """Test ISO duration format."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"iso_duration": "P7D"})
            .build()
        )

        assert query.time_range.iso_duration == "P7D"

    def test_expression(self):
        """Test expression format."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"expression": "P7D"})
            .build()
        )

        assert query.time_range.expression == "P7D"

    def test_iso_duration_with_grain(self):
        """Test ISO duration with round_to_grain."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"iso_duration": "P7D", "round_to_grain": "day"})
            .build()
        )

        assert query.time_range.iso_duration == "P7D"
        assert query.time_range.round_to_grain == TimeGrain.DAY

    def test_time_range_validation_empty_dict(self):
        """Test that empty dict raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.time_range({})

        assert "requires one of" in str(exc_info.value)

    def test_time_range_validation_mixing_types(self):
        """Test that mixing time range types raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.time_range(
                {
                    "start": "2024-01-01",
                    "end": "2024-01-31",
                    "iso_duration": "P7D",
                }
            )

        assert "cannot combine multiple types" in str(exc_info.value)

    def test_time_range_validation_missing_end(self):
        """Test that absolute range missing end raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.time_range({"start": "2024-01-01"})

        assert "requires both 'start' and 'end'" in str(exc_info.value)

    def test_time_range_validation_invalid_grain(self):
        """Test that invalid grain raises error."""
        builder = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
        )

        with pytest.raises(ValueError) as exc_info:
            builder.time_range(
                {"iso_duration": "P7D", "round_to_grain": "invalid_grain"}
            )

        assert "Invalid grain 'invalid_grain'" in str(exc_info.value)


class TestSorting:
    """Test .sort() and .sorts() methods."""

    def test_single_sort_ascending(self):
        """Test single ascending sort."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .sort("advertiser_name")
            .build()
        )

        assert len(query.sort) == 1
        assert query.sort[0].name == "advertiser_name"
        assert query.sort[0].desc is False

    def test_single_sort_descending(self):
        """Test single descending sort."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .sort("overall_spend", desc=True)
            .build()
        )

        assert len(query.sort) == 1
        assert query.sort[0].name == "overall_spend"
        assert query.sort[0].desc is True

    def test_multiple_sorts_via_sort_calls(self):
        """Test multiple sorts via multiple .sort() calls."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .sort("advertiser_name", desc=False)
            .sort("overall_spend", desc=True)
            .build()
        )

        assert len(query.sort) == 2
        assert query.sort[0].name == "advertiser_name"
        assert query.sort[0].desc is False
        assert query.sort[1].name == "overall_spend"
        assert query.sort[1].desc is True

    def test_multiple_sorts_via_sorts_list(self):
        """Test multiple sorts via .sorts() with list."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .sorts(
                [
                    {"name": "advertiser_name", "desc": False},
                    {"name": "overall_spend", "desc": True},
                ]
            )
            .build()
        )

        assert len(query.sort) == 2
        assert query.sort[0].name == "advertiser_name"
        assert query.sort[0].desc is False
        assert query.sort[1].name == "overall_spend"
        assert query.sort[1].desc is True

    def test_sorts_with_default_desc(self):
        """Test that desc defaults to False in sorts list."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .sorts([{"name": "advertiser_name"}])
            .build()
        )

        assert query.sort[0].desc is False


class TestComplexQueries:
    """Test complex queries combining multiple features."""

    def test_complex_query_with_all_features(self):
        """Test query combining dimensions, measures, filters, time range, sorts, and limit."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension(
                "timestamp_day",
                {"time_floor": {"dimension": "__time", "grain": "day"}},
            )
            .dimensions(["advertiser_name", "device_type"])
            .measure("overall_spend")
            .measure(
                "unique_users", {"count_distinct": {"dimension": "user_id"}}
            )
            .measures(["total_bids", "impressions"])
            .where(
                {
                    "op": "and",
                    "conditions": [
                        {"op": "eq", "field": "device_type", "value": "mobile"},
                        {
                            "op": "in",
                            "field": "device_region",
                            "values": ["US", "GB", "CA"],
                        },
                    ],
                }
            )
            .time_range(
                {
                    "start": datetime(2024, 1, 1),
                    "end": datetime(2024, 1, 31),
                }
            )
            .sorts(
                [
                    {"name": "timestamp_day", "desc": False},
                    {"name": "overall_spend", "desc": True},
                ]
            )
            .limit(100)
            .offset(0)
            .build()
        )

        assert query.metrics_view == "bids_metrics"
        assert len(query.dimensions) == 3
        assert len(query.measures) == 4
        assert query.where is not None
        assert query.time_range is not None
        assert len(query.sort) == 2
        assert query.limit == 100
        assert query.offset == 0

    def test_query_with_time_zone(self):
        """Test query with time zone."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_zone("America/New_York")
            .build()
        )

        assert query.time_zone == "America/New_York"

    def test_query_with_use_display_names(self):
        """Test query with use_display_names."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .use_display_names(True)
            .build()
        )

        assert query.use_display_names is True

    def test_query_with_pivot_on(self):
        """Test query with pivot_on."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name", "device_type"])
            .measures(["overall_spend"])
            .pivot_on(["device_type"])
            .build()
        )

        assert query.pivot_on == ["device_type"]

    def test_query_with_having(self):
        """Test query with having clause."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .having({"op": "gt", "field": "overall_spend", "value": 1000})
            .build()
        )

        assert query.having is not None
        assert query.having.cond.op == Operator.GT

    def test_query_with_comparison_time_range(self):
        """Test query with comparison time range."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .time_range({"iso_duration": "P7D"})
            .comparison_time_range(
                {"iso_duration": "P7D", "iso_offset": "P7D"}
            )
            .build()
        )

        assert query.time_range is not None
        assert query.comparison_time_range is not None
        assert query.comparison_time_range.iso_duration == "P7D"
        assert query.comparison_time_range.iso_offset == "P7D"


class TestQuerySerialization:
    """Test that built queries serialize correctly."""

    def test_query_serialization(self):
        """Test that query can be serialized to dict."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .measures(["overall_spend"])
            .limit(10)
            .build()
        )

        # Should be able to serialize to dict
        query_dict = query.model_dump(exclude_none=True)
        assert query_dict["metrics_view"] == "bids_metrics"
        assert len(query_dict["dimensions"]) == 1
        assert query_dict["dimensions"][0]["name"] == "advertiser_name"

    def test_query_serialization_with_complex_features(self):
        """Test serialization of complex query."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimension(
                "timestamp_day",
                {"time_floor": {"dimension": "__time", "grain": "day"}},
            )
            .measures(["overall_spend"])
            .where({"op": "eq", "field": "device_type", "value": "mobile"})
            .time_range({"iso_duration": "P7D"})
            .sort("overall_spend", desc=True)
            .build()
        )

        query_dict = query.model_dump(exclude_none=True)
        assert "where" in query_dict
        assert "time_range" in query_dict
        assert "sort" in query_dict


class TestErrorMessages:
    """Test that error messages are clear and actionable."""

    def test_helpful_error_for_missing_op(self):
        """Test helpful error message for missing 'op'."""
        builder = QueryBuilder().metrics_view("test")

        with pytest.raises(ValueError) as exc_info:
            builder.where({"field": "test"})

        error_msg = str(exc_info.value)
        assert "Missing required key 'op'" in error_msg
        assert "Example:" in error_msg

    def test_helpful_error_for_invalid_operator(self):
        """Test helpful error message for invalid operator."""
        builder = QueryBuilder().metrics_view("test")

        with pytest.raises(ValueError) as exc_info:
            builder.where({"op": "invalid", "field": "test", "value": "val"})

        error_msg = str(exc_info.value)
        assert "Invalid operator 'invalid'" in error_msg
        assert "Supported:" in error_msg

    def test_helpful_error_for_in_operator(self):
        """Test helpful error message for IN operator without values."""
        builder = QueryBuilder().metrics_view("test")

        with pytest.raises(ValueError) as exc_info:
            builder.where({"op": "in", "field": "test", "value": "val"})

        error_msg = str(exc_info.value)
        assert "use 'values' (list) not 'value'" in error_msg

    def test_helpful_error_for_empty_time_range(self):
        """Test helpful error message for empty time range."""
        builder = QueryBuilder().metrics_view("test")

        with pytest.raises(ValueError) as exc_info:
            builder.time_range({})

        error_msg = str(exc_info.value)
        assert "requires one of" in error_msg
        assert "Absolute:" in error_msg
        assert "Relative:" in error_msg


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dimensions_and_measures(self):
        """Test query with no dimensions or measures."""
        query = QueryBuilder().metrics_view("bids_metrics").build()

        assert query.dimensions is None
        assert query.measures is None

    def test_overwriting_where(self):
        """Test that calling where() multiple times replaces the filter."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .where({"op": "eq", "field": "device_type", "value": "mobile"})
            .where({"op": "eq", "field": "device_type", "value": "desktop"})
            .build()
        )

        # Should use the last where
        assert query.where.cond.exprs[1].val == "desktop"

    def test_limit_zero(self):
        """Test query with limit of 0."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .limit(0)
            .build()
        )

        assert query.limit == 0

    def test_large_limit(self):
        """Test query with large limit."""
        query = (
            QueryBuilder()
            .metrics_view("bids_metrics")
            .dimensions(["advertiser_name"])
            .limit(1000000)
            .build()
        )

        assert query.limit == 1000000
