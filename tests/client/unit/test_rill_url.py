"""
Tests for RillUrl model.
"""

import pytest
from pyrill.models import RillUrl


class TestRillUrlModel:
    """Test RillUrl Pydantic model."""

    def test_rill_url_creation_minimal(self):
        """Test creating RillUrl with minimal required fields."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore'
        )

        assert url.base_url == 'https://ui.rilldata.com'
        assert url.org == 'demo'
        assert url.project == 'my-project'
        assert url.page_type == 'explore'
        assert url.page_name == 'bids_explore'

    def test_rill_url_creation_full(self):
        """Test creating RillUrl with all fields."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            time_range='P7D',
            timezone='Europe/London',
            measures=['overall_spend', 'total_bids'],
            dimensions=['campaign_name', 'device_type'],
            sort_dir='DESC',
            sort_by='overall_spend',
            leaderboard_measures=['overall_spend']
        )

        assert url.time_range == 'P7D'
        assert url.timezone == 'Europe/London'
        assert url.measures == ['overall_spend', 'total_bids']
        assert url.dimensions == ['campaign_name', 'device_type']
        assert url.sort_dir == 'DESC'
        assert url.sort_by == 'overall_spend'
        assert url.leaderboard_measures == ['overall_spend']

    def test_rill_url_with_aliases(self):
        """Test that field aliases work correctly."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            tr='P7D',  # Using alias
            tz='America/New_York',  # Using alias
            dims=['campaign_name']  # Using alias
        )

        assert url.time_range == 'P7D'
        assert url.timezone == 'America/New_York'
        assert url.dimensions == ['campaign_name']

    def test_rill_url_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(Exception):  # ValidationError
            RillUrl(
                org='demo',
                project='my-project',
                # Missing base_url and page_name
            )

    def test_rill_url_pivot_mode(self):
        """Test RillUrl with pivot mode parameters."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            view='pivot',
            rows=['time.hour', 'campaign_name'],
            cols=['overall_spend', 'total_bids'],
            table_mode='nest'
        )

        assert url.view == 'pivot'
        assert url.rows == ['time.hour', 'campaign_name']
        assert url.cols == ['overall_spend', 'total_bids']
        assert url.table_mode == 'nest'


class TestRillUrlStringConversion:
    """Test RillUrl __str__() method."""

    def test_str_minimal_url(self):
        """Test converting minimal RillUrl to string."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore'
        )

        url_str = str(url)
        assert url_str == 'https://ui.rilldata.com/demo/my-project/explore/bids_explore'

    def test_str_with_query_params(self):
        """Test converting RillUrl with query params to string."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            time_range='P7D',
            timezone='Europe/London',
            measures=['overall_spend', 'total_bids'],
            dimensions=['campaign_name']
        )

        url_str = str(url)
        assert 'https://ui.rilldata.com/demo/my-project/explore/bids_explore?' in url_str
        assert 'tr=P7D' in url_str
        assert 'tz=Europe' in url_str
        assert 'measures=overall_spend%2Ctotal_bids' in url_str or 'measures=overall_spend,total_bids' in url_str
        assert 'dims=campaign_name' in url_str

    def test_str_with_sort_params(self):
        """Test converting RillUrl with sort params to string."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            sort_dir='DESC',
            sort_by='overall_spend'
        )

        url_str = str(url)
        assert 'sort_dir=DESC' in url_str
        assert 'sort_by=overall_spend' in url_str

    def test_str_pivot_mode(self):
        """Test converting pivot mode RillUrl to string."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            view='pivot',
            rows=['time.hour'],
            cols=['overall_spend'],
            table_mode='nest'
        )

        url_str = str(url)
        assert 'view=pivot' in url_str
        assert 'rows=time.hour' in url_str
        assert 'cols=overall_spend' in url_str
        assert 'table_mode=nest' in url_str

    def test_str_with_leaderboard_measures(self):
        """Test converting RillUrl with leaderboard measures to string."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            measures=['m1', 'm2', 'm3'],
            leaderboard_measures=['m1', 'm2']
        )

        url_str = str(url)
        assert 'leaderboard_measures=m1%2Cm2' in url_str or 'leaderboard_measures=m1,m2' in url_str


class TestRillUrlEncoding:
    """Test URL encoding in RillUrl."""

    def test_timezone_encoding(self):
        """Test that timezone with slashes is properly encoded."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            timezone='America/New_York'
        )

        url_str = str(url)
        # URL encoding converts / to %2F
        assert 'tz=America%2FNew_York' in url_str

    def test_comma_separated_lists(self):
        """Test that lists are comma-separated."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            measures=['m1', 'm2', 'm3']
        )

        url_str = str(url)
        # Commas may be encoded as %2C
        assert 'measures=m1' in url_str
        assert 'm2' in url_str
        assert 'm3' in url_str

    def test_space_encoding_in_time_range(self):
        """Test that spaces in time_range are encoded."""
        url = RillUrl(
            base_url='https://ui.rilldata.com',
            org='demo',
            project='my-project',
            page_type='explore',
            page_name='bids_explore',
            time_range='2025-11-12 to 2025-11-15'
        )

        url_str = str(url)
        # Spaces encoded as +
        assert 'tr=2025-11-12+to+2025-11-15' in url_str or 'tr=2025-11-12%20to%202025-11-15' in url_str
