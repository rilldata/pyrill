"""
Pydantic models for Rill Annotations.

These models represent annotation queries and responses for metrics views.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .query import TimeRange, TimeGrain


class Annotation(BaseModel):
    """
    Single annotation from a metrics view.

    Example:
        >>> annotation = Annotation(
        ...     time="2024-01-15T09:00:00Z",
        ...     description="Promotion started",
        ...     for_measures=["revenue", "orders"]
        ... )
    """
    time: Optional[str] = None
    time_end: Optional[str] = Field(None, alias="timeEnd")
    description: Optional[str] = None
    duration: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = Field(None, alias="additionalFields")
    for_measures: Optional[List[str]] = Field(None, alias="forMeasures")

    model_config = {"populate_by_name": True, "extra": "allow"}


class AnnotationsQuery(BaseModel):
    """
    Query parameters for querying annotations from a metrics view.

    Example:
        >>> from pyrill.models import TimeRange, TimeGrain
        >>> query = AnnotationsQuery(
        ...     measures=["revenue"],
        ...     time_range=TimeRange(expression="LAST_30_DAYS"),
        ...     time_grain=TimeGrain.DAY,
        ...     limit=100
        ... )
    """
    measures: Optional[List[str]] = None
    priority: Optional[int] = None
    time_range: Optional[TimeRange] = Field(None, alias="timeRange")
    time_grain: Optional[TimeGrain] = Field(None, alias="timeGrain")
    time_zone: Optional[str] = Field(None, alias="timeZone")
    limit: Optional[int] = None
    offset: Optional[int] = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class AnnotationsResponse(BaseModel):
    """
    Response from querying annotations.

    Example:
        >>> response = AnnotationsResponse(rows=[...])
        >>> for annotation in response.rows:
        ...     print(annotation.time, annotation.description)
    """
    rows: Optional[List[Annotation]] = None

    model_config = {"extra": "allow"}
