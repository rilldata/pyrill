"""
Tests for UrlBuilder class.
"""

import pytest
from pyrill import UrlBuilder, MetricsQuery, RillUrl
from pyrill.models import Dimension, Measure, Sort, TimeRange
from pyrill.logging import NullLogger


# Test with bids_metrics (metrics view) which maps to bids_explore (page name)
TEST_METRICS_VIEW = 'bids_metrics'
TEST_PAGE_NAME = 'bids_explore'


class TestBasicFunctionality:
    """Test basic UrlBuilder functionality."""

    def test_simple_url_generation(self):
        """Test generating a simple URL with minimal parameters."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='overall_spend')],
            dimensions=[Dimension(name='campaign_name')]
        )

        url = builder.build_url(query)

        assert isinstance(url, RillUrl)
        assert url.org == 'demo'
        assert url.project == 'my-project'
        assert url.page_name == TEST_PAGE_NAME
        assert url.measures == ['overall_spend']
        assert url.dimensions == ['campaign_name']

    def test_url_with_all_parameters(self):
        """Test generating URL with all supported parameters."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='overall_spend'), Measure(name='total_bids')],
            dimensions=[Dimension(name='campaign_name'), Dimension(name='device_type')],
            time_range=TimeRange(iso_duration='P7D'),
            time_zone='America/New_York',
            sort=[Sort(name='overall_spend', desc=True)]
        )

        url = builder.build_url(query)

        assert url.measures == ['overall_spend', 'total_bids']
        assert url.dimensions == ['campaign_name', 'device_type']
        assert url.time_range == 'P7D'
        assert url.timezone == 'America/New_York'
        assert url.sort_dir == 'DESC'
        assert url.sort_by == 'overall_spend'

    def test_pivot_mode_url(self):
        """Test generating pivot view URL."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='overall_spend')],
            dimensions=[Dimension(name='time.hour')],
            time_range=TimeRange(iso_duration='P7D'),
            time_zone='Europe/London'
        )

        url = builder.build_url(query, pivot=True)

        assert url.view == 'pivot'
        assert url.rows == ['time.hour']
        assert url.cols == ['overall_spend']
        assert url.table_mode == 'nest'

    def test_dict_input_validation(self):
        """Test that dict input is converted to MetricsQuery."""
        builder = UrlBuilder(org='demo', project='my-project')
        query_dict = {
            'metrics_view': TEST_METRICS_VIEW,
            'measures': [{'name': 'overall_spend'}],
            'dimensions': [{'name': 'campaign_name'}]
        }

        url = builder.build_url(query_dict)

        assert isinstance(url, RillUrl)
        assert url.page_name == TEST_PAGE_NAME


class TestTimeRangeVariations:
    """Test different time range formats."""

    def test_time_range_iso_duration(self):
        """Test P7D format."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(iso_duration='P7D')
        )

        url = builder.build_url(query)

        assert url.time_range == 'P7D'

    def test_time_range_absolute_dates(self):
        """Test '2025-11-12 to 2025-11-15' format."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(
                start='2025-11-12T00:00:00Z',
                end='2025-11-15T23:59:59Z'
            )
        )

        url = builder.build_url(query)

        assert url.time_range == '2025-11-12 to 2025-11-15'

    def test_time_range_expression(self):
        """Test expression format."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(expression='LAST_7_DAYS')
        )

        url = builder.build_url(query)

        assert url.time_range == 'LAST_7_DAYS'

    def test_missing_time_range(self):
        """Test that missing time_range works."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='clicks')]
        )

        url = builder.build_url(query)

        assert url.time_range is None


class TestDimensionMeasureLists:
    """Test dimension and measure list handling."""

    def test_single_dimension_measure(self):
        """Test with one dimension and one measure."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='clicks')],
            dimensions=[Dimension(name='campaign_name')]
        )

        url = builder.build_url(query)

        assert url.measures == ['clicks']
        assert url.dimensions == ['campaign_name']

    def test_multiple_dimensions_measures(self):
        """Test with multiple dimensions and measures."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='m1'), Measure(name='m2'), Measure(name='m3')],
            dimensions=[Dimension(name='d1'), Dimension(name='d2')]
        )

        url = builder.build_url(query)

        assert url.measures == ['m1', 'm2', 'm3']
        assert url.dimensions == ['d1', 'd2']

    def test_empty_dimensions_measures(self):
        """Test with no dimensions or measures."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW
        )

        url = builder.build_url(query)

        assert url.measures is None
        assert url.dimensions is None


class TestSorting:
    """Test sort parameter handling."""

    def test_sort_ascending(self):
        """Test sort_dir=ASC."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            sort=[Sort(name='clicks', desc=False)]
        )

        url = builder.build_url(query)

        assert url.sort_dir == 'ASC'
        assert url.sort_by == 'clicks'

    def test_sort_descending(self):
        """Test sort_dir=DESC."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            sort=[Sort(name='overall_spend', desc=True)]
        )

        url = builder.build_url(query)

        assert url.sort_dir == 'DESC'
        assert url.sort_by == 'overall_spend'

    def test_no_sort(self):
        """Test with no sort specified."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW
        )

        url = builder.build_url(query)

        assert url.sort_dir is None
        assert url.sort_by is None

    def test_multiple_sorts_uses_first(self):
        """Test that only first sort is used."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            sort=[
                Sort(name='clicks', desc=True),
                Sort(name='impressions', desc=False)
            ]
        )

        url = builder.build_url(query)

        # Should use first sort only
        assert url.sort_dir == 'DESC'
        assert url.sort_by == 'clicks'


class TestTimezone:
    """Test timezone parameter handling."""

    def test_timezone_present(self):
        """Test that timezone is included."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_zone='America/New_York'
        )

        url = builder.build_url(query)

        assert url.timezone == 'America/New_York'

    def test_missing_timezone(self):
        """Test that missing timezone works."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW
        )

        url = builder.build_url(query)

        assert url.timezone is None


class TestLeaderboardMeasures:
    """Test leaderboard_measures parameter."""

    def test_multi_leaderboard_measures_true(self):
        """Test all measures in leaderboard."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='m1'), Measure(name='m2'), Measure(name='m3')]
        )

        url = builder.build_url(query, multi_leaderboard_measures=True)

        assert url.leaderboard_measures == ['m1', 'm2', 'm3']

    def test_multi_leaderboard_measures_false(self):
        """Test only first measure in leaderboard."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='m1'), Measure(name='m2'), Measure(name='m3')]
        )

        url = builder.build_url(query, multi_leaderboard_measures=False)

        assert url.leaderboard_measures == ['m1']

    def test_leaderboard_with_no_measures(self):
        """Test no leaderboard param if no measures."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW
        )

        url = builder.build_url(query, multi_leaderboard_measures=True)

        assert url.leaderboard_measures is None

    def test_leaderboard_not_in_pivot_mode(self):
        """Test leaderboard not set in pivot mode."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            measures=[Measure(name='m1'), Measure(name='m2')]
        )

        url = builder.build_url(query, pivot=True)

        assert url.leaderboard_measures is None


class TestOrgProjectResolution:
    """Test org and project parameter resolution."""

    def test_defaults_from_init(self):
        """Test using defaults from __init__."""
        builder = UrlBuilder(org='default-org', project='default-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query)

        assert url.org == 'default-org'
        assert url.project == 'default-project'

    def test_parameter_override(self):
        """Test parameters override defaults."""
        builder = UrlBuilder(org='default-org', project='default-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query, org='override-org', project='override-project')

        assert url.org == 'override-org'
        assert url.project == 'override-project'

    def test_missing_org_raises_error(self):
        """Test error if no org provided."""
        builder = UrlBuilder(project='my-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        with pytest.raises(ValueError, match="Organization required"):
            builder.build_url(query)

    def test_missing_project_raises_error(self):
        """Test error if no project provided."""
        builder = UrlBuilder(org='my-org')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        with pytest.raises(ValueError, match="Project required"):
            builder.build_url(query)


class TestValidation:
    """Test query validation."""

    def test_missing_metrics_view_raises(self):
        """Test error if no metrics_view."""
        builder = UrlBuilder(org='demo', project='my-project')
        # Create query without metrics_view (should fail validation)
        with pytest.raises(Exception):  # ValidationError or ValueError
            MetricsQuery()

    def test_invalid_query_dict_raises(self):
        """Test invalid dict raises validation error."""
        builder = UrlBuilder(org='demo', project='my-project')
        query_dict = {
            'invalid_field': 'value'
            # Missing metrics_view
        }

        with pytest.raises(ValueError, match="Invalid query dict"):
            builder.build_url(query_dict)

    def test_valid_metrics_query_object(self):
        """Test accepts MetricsQuery directly."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query)

        assert isinstance(url, RillUrl)


class TestUnsupportedFeaturesWarning:
    """Test warning behavior for unsupported features."""

    def test_where_clause_logs_warning(self, caplog):
        """Test warns if where clause present."""
        from pyrill.models import Expression, Condition, Operator

        logger = NullLogger()  # Use NullLogger to avoid actual logging
        builder = UrlBuilder(org='demo', project='my-project', logger=logger)
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            where=Expression(
                cond=Condition(
                    op=Operator.EQ,
                    exprs=[Expression(name='campaign'), Expression(val='test')]
                )
            )
        )

        # Should not raise, should generate URL without filter
        url = builder.build_url(query)

        assert isinstance(url, RillUrl)
        # Filter not included in URL
        assert url.filter_expr is None

    def test_having_clause_logs_warning(self):
        """Test warns if having clause present."""
        from pyrill.models import Expression, Condition, Operator

        logger = NullLogger()
        builder = UrlBuilder(org='demo', project='my-project', logger=logger)
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            having=Expression(
                cond=Condition(
                    op=Operator.GT,
                    exprs=[Expression(name='clicks'), Expression(val=100)]
                )
            )
        )

        # Should not raise, should generate URL without filter
        url = builder.build_url(query)

        assert isinstance(url, RillUrl)
        assert url.filter_expr is None

    def test_comparison_time_range_logs_warning(self):
        """Test warns if comparison_time_range present."""
        logger = NullLogger()
        builder = UrlBuilder(org='demo', project='my-project', logger=logger)
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            comparison_time_range=TimeRange(iso_duration='P7D')
        )

        # Should not raise, should generate URL
        url = builder.build_url(query)

        assert isinstance(url, RillUrl)
        # comparison_time_range from query is ignored
        assert url.compare_time_range is None


class TestBaseUrl:
    """Test base URL handling."""

    def test_default_base_url(self):
        """Test uses default base URL."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query)

        assert url.base_url == 'https://ui.rilldata.com'

    def test_custom_base_url(self):
        """Test accepts custom base URL."""
        builder = UrlBuilder(
            base_url='https://custom.rilldata.com',
            org='demo',
            project='my-project'
        )
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query)

        assert url.base_url == 'https://custom.rilldata.com'

    def test_base_url_trailing_slash(self):
        """Test handles trailing slash in base URL."""
        builder = UrlBuilder(
            base_url='https://ui.rilldata.com/',
            org='demo',
            project='my-project'
        )
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query)

        # Trailing slash should be removed
        assert url.base_url == 'https://ui.rilldata.com'


class TestGrainCalculation:
    """Test grain parameter calculation."""

    def test_grain_for_long_duration(self):
        """Test grain='day' for > 2 days."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(iso_duration='P7D')
        )

        url = builder.build_url(query)

        assert url.grain == 'day'

    def test_grain_for_short_duration(self):
        """Test grain='hour' for <= 2 days."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(iso_duration='P1D')
        )

        url = builder.build_url(query)

        assert url.grain == 'hour'

    def test_grain_for_absolute_time_range(self):
        """Test grain calculation for absolute dates."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(
                start='2025-11-12T00:00:00Z',
                end='2025-11-15T23:59:59Z'  # 3 days
            )
        )

        url = builder.build_url(query)

        assert url.grain == 'day'

    def test_grain_none_for_expression(self):
        """Test grain=None for expression-based time range."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            time_range=TimeRange(expression='LAST_7_DAYS')
        )

        url = builder.build_url(query)

        # Can't determine span for expression
        assert url.grain is None


class TestComparisonParameter:
    """Test enable_comparison parameter."""

    def test_comparison_disabled_by_default(self):
        """Test compare_tr not set by default."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query)

        assert url.compare_time_range is None

    def test_comparison_enabled(self):
        """Test compare_tr='rill-PP' when enabled."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = MetricsQuery(metrics_view=TEST_METRICS_VIEW)

        url = builder.build_url(query, enable_comparison=True)

        assert url.compare_time_range == 'rill-PP'
