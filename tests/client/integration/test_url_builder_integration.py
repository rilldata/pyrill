"""
Integration tests for UrlBuilder with QueryBuilder and real examples.
"""

import pytest
from pyrill import QueryBuilder, UrlBuilder


class TestQueryBuilderIntegration:
    """Test UrlBuilder integration with QueryBuilder."""

    def test_query_builder_to_url(self):
        """Test building query and generating URL."""
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .dimensions(['device_type', 'campaign_name'])
                 .measures(['overall_spend', 'total_bids'])
                 .time_range({'iso_duration': 'P7D'})
                 .time_zone('America/New_York')
                 .sort('overall_spend', desc=True)
                 .build())

        builder = UrlBuilder(org='demo', project='my-project')
        url = builder.build_url(query)

        url_str = str(url)
        assert 'demo/my-project/explore/bids_explore' in url_str
        assert 'tr=P7D' in url_str
        assert 'tz=America' in url_str
        assert 'overall_spend' in url_str

    def test_complex_query_to_url(self):
        """Test complex query with all features."""
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .dimensions(['campaign_name', 'device_type', 'advertiser_name'])
                 .measures(['overall_spend', 'total_bids', 'win_rate', 'ctr', 'impressions'])
                 .time_range({'iso_duration': 'P7D'})
                 .time_zone('Europe/London')
                 .sort('overall_spend', desc=False)
                 .build())

        builder = UrlBuilder(org='demo', project='rill-openrtb-prog-ads')
        url = builder.build_url(query, multi_leaderboard_measures=True)

        url_str = str(url)
        # Check all key components present
        assert 'rill-openrtb-prog-ads' in url_str
        assert 'bids_explore' in url_str  # page_name, not metrics_view
        assert 'tr=P7D' in url_str
        assert 'tz=Europe' in url_str
        assert 'sort_dir=ASC' in url_str
        assert 'sort_by=overall_spend' in url_str


class TestRealExampleValidation:
    """Test that generated URLs match real example patterns."""

    def test_matches_iso_duration_url(self):
        """Test generating URL matching P7D example."""
        builder = UrlBuilder(org='demo', project='rill-openrtb-prog-ads')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .time_range({'iso_duration': 'P7D'})
                 .time_zone('Europe/London')
                 .measures(['overall_spend', 'total_bids', 'win_rate', 'ctr', 'impressions'])
                 .dimensions(['app_or_site', 'auction_type', 'campaign_name', 'device_type'])
                 .sort('overall_spend', desc=False)
                 .build())

        url = builder.build_url(query, multi_leaderboard_measures=True)
        url_str = str(url)

        # Verify key components
        assert 'demo/rill-openrtb-prog-ads/explore/bids_explore' in url_str
        assert 'tr=P7D' in url_str
        assert 'tz=Europe' in url_str
        assert 'sort_dir=ASC' in url_str
        assert 'leaderboard_measures=' in url_str

    def test_matches_absolute_date_url(self):
        """Test generating URL with absolute dates."""
        builder = UrlBuilder(org='demo', project='rill-openrtb-prog-ads')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .time_range({
                     'start': '2025-11-12T00:00:00Z',
                     'end': '2025-11-15T23:59:59Z'
                 })
                 .time_zone('Europe/London')
                 .measures(['overall_spend', 'total_bids'])
                 .dimensions(['campaign_name'])
                 .sort('overall_spend', desc=False)
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        # Check absolute date format
        assert 'tr=2025-11-12+to+2025-11-15' in url_str or 'tr=2025-11-12%20to%202025-11-15' in url_str

    def test_matches_pivot_example(self):
        """Test generating pivot URL matching example."""
        builder = UrlBuilder(org='demo', project='rill-openrtb-prog-ads')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .time_range({'iso_duration': 'P7D'})
                 .time_zone('Europe/London')
                 .dimensions(['time.hour'])
                 .measures(['overall_spend', 'total_bids', 'win_rate', 'ctr', 'impressions'])
                 .build())

        url = builder.build_url(query, pivot=True)
        url_str = str(url)

        # Verify pivot structure
        assert 'view=pivot' in url_str
        assert 'rows=time.hour' in url_str
        assert 'cols=' in url_str and 'overall_spend' in url_str
        assert 'table_mode=nest' in url_str

    def test_matches_single_measure_sort_by(self):
        """Test generating URL with sort_by."""
        builder = UrlBuilder(org='demo', project='rill-openrtb-prog-ads')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .measures(['clicks'])
                 .dimensions(['campaign_name'])
                 .sort('clicks', desc=True)
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        assert 'sort_by=clicks' in url_str
        assert 'sort_dir=DESC' in url_str

    def test_leaderboard_subset(self):
        """Test leaderboard_measures logic."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .measures(['total_bids', 'overall_spend', 'impressions'])
                 .dimensions(['campaign_name'])
                 .build())

        # Test with multi=True (all measures)
        url_multi = builder.build_url(query, multi_leaderboard_measures=True)
        url_multi_str = str(url_multi)
        assert 'leaderboard_measures=total_bids' in url_multi_str
        assert 'overall_spend' in url_multi_str
        assert 'impressions' in url_multi_str

        # Test with multi=False (first only)
        url_single = builder.build_url(query, multi_leaderboard_measures=False)
        url_single_str = str(url_single)
        assert 'leaderboard_measures=total_bids' in url_single_str
        # Should not have other measures in leaderboard (hard to test precisely due to encoding)


class TestRoundTrip:
    """Test URL structure and parsing."""

    def test_url_structure_valid(self):
        """Test that generated URL has valid structure."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .measures(['clicks'])
                 .dimensions(['campaign_name'])
                 .time_range({'iso_duration': 'P7D'})
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        # Check URL structure
        assert url_str.startswith('https://')
        assert '/explore/' in url_str
        assert '?' in url_str

    def test_query_params_correct(self):
        """Test all expected params present."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .measures(['overall_spend', 'total_bids'])
                 .dimensions(['campaign_name', 'device_type'])
                 .time_range({'iso_duration': 'P7D'})
                 .time_zone('America/New_York')
                 .sort('overall_spend', desc=True)
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        # Verify all expected params
        params_to_check = [
            'tr=',
            'tz=',
            'measures=',
            'dims=',
            'sort_dir=',
            'sort_by=',
            'leaderboard_measures='
        ]

        for param in params_to_check:
            assert param in url_str, f"Expected param '{param}' not found in URL"


class TestComparisonParameter:
    """Test comparison parameter integration."""

    def test_comparison_enabled_in_url(self):
        """Test that enable_comparison adds compare_tr parameter."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .measures(['overall_spend'])
                 .dimensions(['campaign_name'])
                 .build())

        url = builder.build_url(query, enable_comparison=True)
        url_str = str(url)

        assert 'compare_tr=rill-PP' in url_str

    def test_comparison_disabled_by_default(self):
        """Test that comparison is not added by default."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .measures(['overall_spend'])
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        assert 'compare_tr' not in url_str


class TestGrainIntegration:
    """Test grain parameter in generated URLs."""

    def test_grain_set_for_week_duration(self):
        """Test grain='day' for P7D."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .time_range({'iso_duration': 'P7D'})
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        assert 'grain=day' in url_str

    def test_grain_set_for_single_day(self):
        """Test grain='hour' for P1D."""
        builder = UrlBuilder(org='demo', project='my-project')
        query = (QueryBuilder()
                 .metrics_view('bids_metrics')
                 .time_range({'iso_duration': 'P1D'})
                 .build())

        url = builder.build_url(query)
        url_str = str(url)

        assert 'grain=hour' in url_str
