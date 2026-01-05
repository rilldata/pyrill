"""
URL builder for generating Rill UI explore URLs from MetricsQuery objects.
"""

from typing import Optional, List, Tuple, Union
from datetime import datetime, timedelta
import re

from .models import MetricsQuery, TimeRange, RillUrl
from .logging import ClientLogger, NullLogger
from pydantic import ValidationError


class UrlBuilder:
    """
    Build Rill UI explore URLs from MetricsQuery objects.

    Example:
        >>> from pyrill import UrlBuilder, QueryBuilder
        >>>
        >>> # Build a query
        >>> query = (QueryBuilder()
        ...     .metrics_view('bids_explore')
        ...     .dimensions(['device_type', 'campaign_name'])
        ...     .measures(['overall_spend', 'total_bids'])
        ...     .time_range({'iso_duration': 'P7D'})
        ...     .time_zone('America/New_York')
        ...     .sort('overall_spend', desc=True)
        ...     .build())
        >>>
        >>> # Generate URL
        >>> builder = UrlBuilder(org='my-org', project='my-project')
        >>> url = builder.build_url(query)
        >>> print(url)
        'https://ui.rilldata.com/my-org/my-project/explore/bids_explore?...'
        >>>
        >>> # Generate pivot view URL
        >>> pivot_url = builder.build_url(query, pivot=True)
        >>>
        >>> # With single leaderboard measure
        >>> url = builder.build_url(query, multi_leaderboard_measures=False)
    """

    def __init__(
        self,
        base_url: str = "https://ui.rilldata.com",
        org: Optional[str] = None,
        project: Optional[str] = None,
        logger: Optional[ClientLogger] = None
    ):
        """
        Initialize URL builder.

        Args:
            base_url: Base URL for Rill UI (default: https://ui.rilldata.com)
            org: Default organization name
            project: Default project name
            logger: Optional logger for warnings about unsupported features
        """
        self.base_url = base_url.rstrip('/')
        self.default_org = org
        self.default_project = project
        self.logger = logger or NullLogger()

    def build_url(
        self,
        query: Union[MetricsQuery, dict],
        org: Optional[str] = None,
        project: Optional[str] = None,
        pivot: bool = False,
        multi_leaderboard_measures: bool = True,
        enable_comparison: bool = False
    ) -> RillUrl:
        """
        Generate Rill UI explore URL from metrics query.

        Args:
            query: MetricsQuery object or dict (will be validated)
            org: Organization name (overrides default if provided)
            project: Project name (overrides default if provided)
            pivot: If True, generate pivot table view URL
            multi_leaderboard_measures: If True, include all measures in leaderboard.
                                       If False, only include first measure in leaderboard.
                                       Default: True (all measures in leaderboard)
            enable_comparison: If True, add compare_tr=rill-PP to enable period comparison.
                             Default: False (no comparison)

        Returns:
            RillUrl object that can be converted to string via str()

        Raises:
            ValueError: If query is invalid or missing required fields
            ValueError: If metrics_view not in query
            ValueError: If org or project not provided and no defaults

        Warnings:
            Logs warning if query contains unsupported features (where/having filters).
            URL is generated without these features.
            Note: If query.comparison_time_range is set, it will be ignored and a
            warning logged. Use enable_comparison parameter instead.

        Example:
            >>> builder = UrlBuilder(org='demo', project='my-proj')
            >>> rill_url = builder.build_url(query_dict)
            >>> print(str(rill_url))  # Convert to string
            >>> # With comparison enabled
            >>> rill_url = builder.build_url(query, enable_comparison=True)
            >>> # compare_tr=rill-PP will be added to URL
        """
        # Validate and convert query
        validated_query = self._validate_query(query)

        # Check for unsupported features
        self._warn_unsupported_features(validated_query, enable_comparison)

        # Resolve org and project
        resolved_org, resolved_project = self._resolve_org_project(org, project)

        # Build the URL
        return self._build_rill_url(
            validated_query,
            resolved_org,
            resolved_project,
            pivot,
            multi_leaderboard_measures,
            enable_comparison
        )

    def _validate_query(self, query: Union[MetricsQuery, dict]) -> MetricsQuery:
        """Convert dict to MetricsQuery and validate."""
        if isinstance(query, dict):
            try:
                return MetricsQuery(**query)
            except ValidationError as e:
                raise ValueError(f"Invalid query dict: {e}")
        elif isinstance(query, MetricsQuery):
            return query
        else:
            raise ValueError(f"Query must be MetricsQuery or dict, got {type(query)}")

    def _warn_unsupported_features(
        self,
        query: MetricsQuery,
        enable_comparison: bool
    ) -> None:
        """Log warnings for any unsupported features in the query."""
        if query.where is not None:
            self.logger.warning(
                "Query contains 'where' clause which cannot be encoded in URL. "
                "Filter will not be included."
            )

        if query.having is not None:
            self.logger.warning(
                "Query contains 'having' clause which cannot be encoded in URL. "
                "Filter will not be included."
            )

        if query.comparison_time_range is not None:
            self.logger.warning(
                "Query contains 'comparison_time_range' which is ignored. "
                "Use enable_comparison parameter instead."
            )

    def _resolve_org_project(
        self,
        org: Optional[str],
        project: Optional[str]
    ) -> Tuple[str, str]:
        """Resolve org and project from parameters or defaults."""
        # Resolve org
        resolved_org = org or self.default_org
        if not resolved_org:
            raise ValueError(
                "Organization required. Provide org parameter or "
                "set in UrlBuilder(..., org='name')"
            )

        # Resolve project
        resolved_project = project or self.default_project
        if not resolved_project:
            raise ValueError(
                "Project required. Provide project parameter or "
                "set in UrlBuilder(..., project='name')"
            )

        return resolved_org, resolved_project

    def _build_time_range_param(
        self,
        time_range: Optional[TimeRange]
    ) -> Optional[str]:
        """
        Convert TimeRange to URL parameter value.

        Formats:
        - iso_duration: 'P7D'
        - start + end: '2025-11-12 to 2025-11-15' (space-separated)
        - expression: pass through as-is
        """
        if time_range is None:
            return None

        # Priority 1: iso_duration
        if time_range.iso_duration:
            return time_range.iso_duration

        # Priority 2: start + end as absolute range
        if time_range.start and time_range.end:
            # Extract date portion from ISO timestamps
            start_date = time_range.start.split('T')[0]
            end_date = time_range.end.split('T')[0]
            return f"{start_date} to {end_date}"

        # Priority 3: expression (pass through as-is)
        if time_range.expression:
            return time_range.expression

        return None

    def _calculate_grain(self, time_range: Optional[TimeRange]) -> Optional[str]:
        """
        Calculate appropriate grain parameter based on time range.

        Logic:
        - If time range spans > 2 days: grain = 'day'
        - If time range spans ≤ 2 days: grain = 'hour'
        - If no time range or can't determine: grain = None

        TODO: Consider more sophisticated logic based on:
        - Actual data granularity in metrics view
        - Number of expected data points
        - User preferences

        Args:
            time_range: TimeRange object from query

        Returns:
            'day', 'hour', or None
        """
        if time_range is None:
            return None

        # Try to parse iso_duration
        if time_range.iso_duration:
            days = self._parse_iso_duration_days(time_range.iso_duration)
            if days is not None:
                return 'day' if days > 2 else 'hour'

        # Try to calculate from start/end
        if time_range.start and time_range.end:
            try:
                start = datetime.fromisoformat(time_range.start.replace('Z', '+00:00'))
                end = datetime.fromisoformat(time_range.end.replace('Z', '+00:00'))
                delta = end - start
                days = delta.total_seconds() / 86400
                return 'day' if days > 2 else 'hour'
            except (ValueError, AttributeError):
                pass

        # Can't determine - return None
        return None

    def _parse_iso_duration_days(self, iso_duration: str) -> Optional[int]:
        """
        Parse ISO 8601 duration to approximate days.

        Simple parser for common formats like 'P7D', 'P1M', 'P1Y'.
        Returns None if can't parse.
        """
        # Match patterns like P7D, P1W, P1M, P1Y
        match = re.match(r'P(\d+)([DWMY])', iso_duration)
        if match:
            value = int(match.group(1))
            unit = match.group(2)

            # Convert to days
            if unit == 'D':
                return value
            elif unit == 'W':
                return value * 7
            elif unit == 'M':
                return value * 30  # Approximate
            elif unit == 'Y':
                return value * 365  # Approximate

        return None

    def _build_comparison_param(self, enable_comparison: bool) -> Optional[str]:
        """
        Build compare_tr parameter.

        If enable_comparison is True, return 'rill-PP' (prior period comparison).

        TODO: Refine this logic. Consider:
        - Different comparison types (week-over-week, year-over-year, etc.)
        - Custom comparison periods
        - Integration with query.comparison_time_range (currently ignored with warning)

        Args:
            enable_comparison: Boolean flag from build_url()

        Returns:
            'rill-PP' if enabled, None otherwise
        """
        if enable_comparison:
            return 'rill-PP'
        return None

    def _get_sort_params(
        self,
        query: MetricsQuery
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract sort parameters from first sort only.

        Returns:
            Tuple of (sort_dir, sort_by)
            - sort_dir: 'ASC' if not desc, 'DESC' if desc
            - sort_by: field name from sort[0].name

        Both parameters are optional. If query has a sort:
        - Set both sort_by and sort_dir
        If no sort:
        - Return (None, None)
        """
        if query.sort and len(query.sort) > 0:
            first_sort = query.sort[0]
            sort_dir = 'DESC' if first_sort.desc else 'ASC'
            sort_by = first_sort.name
            return (sort_dir, sort_by)
        return (None, None)

    def _build_leaderboard_measures(
        self,
        measures: List[str],
        multi: bool
    ) -> Optional[List[str]]:
        """
        Build leaderboard_measures parameter.

        Args:
            measures: List of measure names
            multi: If True, return all measures. If False, return only first.

        Returns:
            List of measure names for leaderboard, or None if no measures
        """
        if not measures:
            return None

        if multi:
            return measures
        else:
            return [measures[0]] if measures else None

    def _metrics_view_to_page_name(self, metrics_view: str) -> str:
        """
        Map a metrics_view name to an explore or canvas page name.

        This is a hardcoded mapping for known metrics views.
        In the future, this could be enhanced to:
        - Query the Rill API for the actual page mapping
        - Use a configuration file
        - Support custom mappings

        Args:
            metrics_view: The metrics view name from the query

        Returns:
            The page name for the URL

        Raises:
            ValueError: If the metrics_view cannot be mapped to a page
        """
        # Hardcoded mappings
        mappings = {
            "bids_metrics": "bids_explore",
            "auction_metrics": "auction_explore",
        }

        page_name = mappings.get(metrics_view)
        if page_name is None:
            raise ValueError(
                f"Page Could Not Be Found: metrics_view '{metrics_view}' does not have a known page mapping. "
                f"Known mappings: {list(mappings.keys())}"
            )

        return page_name

    def _build_rill_url(
        self,
        query: MetricsQuery,
        org: str,
        project: str,
        pivot: bool,
        multi_leaderboard_measures: bool,
        enable_comparison: bool
    ) -> RillUrl:
        """
        Build RillUrl object from validated query and parameters.

        This is the main internal method that constructs the RillUrl model.
        """
        # Validate metrics_view
        if not query.metrics_view:
            raise ValueError("MetricsQuery must have metrics_view field")

        # Map metrics_view to page_name
        page_name = self._metrics_view_to_page_name(query.metrics_view)

        # Extract basic parameters
        time_range_param = self._build_time_range_param(query.time_range)
        sort_dir, sort_by = self._get_sort_params(query)
        grain = self._calculate_grain(query.time_range)
        compare_tr = self._build_comparison_param(enable_comparison)

        # Extract dimension and measure names
        dimension_names = [d.name for d in query.dimensions] if query.dimensions else None
        measure_names = [m.name for m in query.measures] if query.measures else None

        # Build leaderboard measures
        leaderboard_measures = None
        if measure_names and not pivot:
            leaderboard_measures = self._build_leaderboard_measures(
                measure_names,
                multi_leaderboard_measures
            )

        # Pivot mode
        if pivot:
            return RillUrl(
                base_url=self.base_url,
                org=org,
                project=project,
                page_type='explore',
                page_name=page_name,
                time_range=time_range_param,
                timezone=query.time_zone,
                view='pivot',
                rows=dimension_names,
                cols=measure_names,
                table_mode='nest',
                sort_by=sort_by if sort_by else '',  # Empty string for pivot
                grain=grain,
                compare_time_range=compare_tr
            )
        else:
            # Standard view
            return RillUrl(
                base_url=self.base_url,
                org=org,
                project=project,
                page_type='explore',
                page_name=page_name,
                time_range=time_range_param,
                timezone=query.time_zone,
                measures=measure_names,
                dimensions=dimension_names,
                sort_dir=sort_dir,
                sort_by=sort_by,
                leaderboard_measures=leaderboard_measures,
                grain=grain,
                compare_time_range=compare_tr
            )
