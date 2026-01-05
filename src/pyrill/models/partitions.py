"""
Pydantic models for partition operations
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ModelPartition(BaseModel):
    """
    Model partition details.

    Represents a single partition of a partitioned model with its execution state.
    """
    key: str  # Partition key/identifier
    data: Optional[Dict[str, Any]] = None  # Partition data payload
    watermark: Optional[str] = None  # Watermark timestamp
    executed_on: Optional[str] = Field(None, alias="executedOn")  # Execution timestamp
    error: Optional[str] = None  # Error message if partition failed
    elapsed_ms: Optional[int] = Field(None, alias="elapsedMs")  # Execution duration

    model_config = {"populate_by_name": True}


class PartitionsList(BaseModel):
    """
    Response from list partitions endpoint.

    Contains partitions and pagination token for fetching additional results.
    """
    partitions: List[ModelPartition] = Field(default_factory=list)
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")

    model_config = {"populate_by_name": True}
