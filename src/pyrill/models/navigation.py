"""
Navigation models for URL building.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from urllib.parse import urlencode


class RillUrl(BaseModel):
    """
    Structured representation of a Rill explore or canvas URL.

    This model is constructed by UrlBuilder and can be converted to a string URL.
    It provides validation and type safety for URL components.

    Example:
        >>> rill_url = RillUrl(
        ...     base_url='https://ui.rilldata.com',
        ...     org='demo',
        ...     project='rill-openrtb-prog-ads',
        ...     page_type='explore',
        ...     page_name='bids_explore',
        ...     time_range='P7D',
        ...     timezone='Europe/London',
        ...     measures=['overall_spend', 'total_bids'],
        ...     dimensions=['campaign_name', 'device_type'],
        ...     sort_dir='DESC',
        ...     sort_by='overall_spend'
        ... )
        >>> str(rill_url)
        'https://ui.rilldata.com/demo/rill-openrtb-prog-ads/explore/bids_explore?...'
    """
    # Required fields
    base_url: str
    org: str
    project: str
    page_type: Literal['explore', 'canvas'] = 'explore'
    page_name: str

    # Optional query parameters
    time_range: Optional[str] = Field(None, alias='tr')
    timezone: Optional[str] = Field(None, alias='tz')
    measures: Optional[List[str]] = None
    dimensions: Optional[List[str]] = Field(None, alias='dims')
    sort_dir: Optional[str] = None  # 'ASC' or 'DESC'
    sort_by: Optional[str] = None
    leaderboard_measures: Optional[List[str]] = None

    # Pivot mode
    view: Optional[str] = None  # 'pivot' for pivot view
    rows: Optional[List[str]] = None  # Pivot rows (dimensions)
    cols: Optional[List[str]] = None  # Pivot columns (measures)
    table_mode: Optional[str] = None  # 'nest' for pivot

    # Optional parameters
    filter_expr: Optional[str] = Field(None, alias='f')
    grain: Optional[str] = None
    compare_time_range: Optional[str] = Field(None, alias='compare_tr')

    model_config = {"populate_by_name": True, "extra": "forbid"}

    def __str__(self) -> str:
        """Convert RillUrl to URL string."""
        # Build base path
        path = f"{self.base_url}/{self.org}/{self.project}/{self.page_type}/{self.page_name}"

        # Build query parameters
        params = {}

        if self.time_range:
            params['tr'] = self.time_range
        if self.timezone:
            params['tz'] = self.timezone
        if self.measures:
            params['measures'] = ','.join(self.measures)
        if self.dimensions:
            params['dims'] = ','.join(self.dimensions)
        if self.sort_dir:
            params['sort_dir'] = self.sort_dir
        if self.sort_by:
            params['sort_by'] = self.sort_by
        if self.leaderboard_measures:
            params['leaderboard_measures'] = ','.join(self.leaderboard_measures)

        # Pivot mode parameters
        if self.view:
            params['view'] = self.view
        if self.rows:
            params['rows'] = ','.join(self.rows)
        if self.cols:
            params['cols'] = ','.join(self.cols)
        if self.table_mode:
            params['table_mode'] = self.table_mode

        # Optional parameters
        if self.filter_expr:
            params['f'] = self.filter_expr
        if self.grain:
            params['grain'] = self.grain
        if self.compare_time_range:
            params['compare_tr'] = self.compare_time_range

        # Build URL with proper encoding
        if params:
            query_string = urlencode(params, safe=',')
            return f"{path}?{query_string}"
        return path
