"""
Pydantic models for Rill Report resources.

These models represent report configurations, schedules, and execution state
for scheduled reports in Rill.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Export format for report files."""
    UNSPECIFIED = "EXPORT_FORMAT_UNSPECIFIED"
    CSV = "EXPORT_FORMAT_CSV"
    XLSX = "EXPORT_FORMAT_XLSX"
    PARQUET = "EXPORT_FORMAT_PARQUET"


class Schedule(BaseModel):
    """
    Schedule configuration for report execution.

    Example:
        >>> schedule = Schedule(
        ...     cron="0 9 * * 1",
        ...     time_zone="America/New_York"
        ... )
    """
    ref_update: Optional[bool] = Field(None, alias="refUpdate")
    disable: Optional[bool] = None
    cron: Optional[str] = None
    ticker_seconds: Optional[int] = Field(None, alias="tickerSeconds")
    time_zone: Optional[str] = Field(None, alias="timeZone")

    model_config = {"populate_by_name": True, "extra": "allow"}


class Notifier(BaseModel):
    """
    Notification configuration for report delivery.

    Example:
        >>> notifier = Notifier(
        ...     connector="email",
        ...     properties={"recipients": ["user@example.com"]}
        ... )
    """
    connector: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class ReportSpec(BaseModel):
    """
    Report specification containing configuration and scheduling details.

    Example:
        >>> spec = ReportSpec(
        ...     display_name="Weekly Report",
        ...     refresh_schedule=Schedule(cron="0 9 * * 1"),
        ...     query_name="revenue_metrics",
        ...     export_format=ExportFormat.XLSX
        ... )
    """
    display_name: Optional[str] = Field(None, alias="displayName")
    trigger: Optional[bool] = None
    refresh_schedule: Optional[Schedule] = Field(None, alias="refreshSchedule")
    timeout_seconds: Optional[int] = Field(None, alias="timeoutSeconds")
    query_name: Optional[str] = Field(None, alias="queryName")
    query_args_json: Optional[str] = Field(None, alias="queryArgsJson")
    export_limit: Optional[int] = Field(None, alias="exportLimit")
    export_format: Optional[ExportFormat] = Field(None, alias="exportFormat")
    export_include_header: Optional[bool] = Field(None, alias="exportIncludeHeader")
    notifiers: Optional[List[Notifier]] = None
    annotations: Optional[Dict[str, str]] = None
    watermark_inherit: Optional[bool] = Field(None, alias="watermarkInherit")
    intervals_iso_duration: Optional[str] = Field(None, alias="intervalsIsoDuration")
    intervals_limit: Optional[int] = Field(None, alias="intervalsLimit")
    intervals_check_unclosed: Optional[bool] = Field(None, alias="intervalsCheckUnclosed")

    model_config = {"populate_by_name": True, "extra": "allow"}


class ReportExecution(BaseModel):
    """
    Single execution record for a report run.

    Example:
        >>> execution = ReportExecution(
        ...     adhoc=False,
        ...     started_on="2024-01-15T09:00:00Z",
        ...     finished_on="2024-01-15T09:02:30Z"
        ... )
    """
    adhoc: Optional[bool] = None
    error_message: Optional[str] = Field(None, alias="errorMessage")
    report_time: Optional[str] = Field(None, alias="reportTime")
    started_on: Optional[str] = Field(None, alias="startedOn")
    finished_on: Optional[str] = Field(None, alias="finishedOn")

    model_config = {"populate_by_name": True, "extra": "allow"}


class ReportState(BaseModel):
    """
    Report state containing execution status and history.

    Example:
        >>> state = ReportState(
        ...     next_run_on="2024-01-22T09:00:00Z",
        ...     execution_count=10,
        ...     execution_history=[...]
        ... )
    """
    next_run_on: Optional[str] = Field(None, alias="nextRunOn")
    current_execution: Optional[ReportExecution] = Field(None, alias="currentExecution")
    execution_history: Optional[List[ReportExecution]] = Field(None, alias="executionHistory")
    execution_count: Optional[int] = Field(None, alias="executionCount")

    model_config = {"populate_by_name": True, "extra": "allow"}


class Report(BaseModel):
    """
    Complete report resource with spec and state.

    Example:
        >>> report = Report(
        ...     name="weekly-summary",
        ...     spec=ReportSpec(...),
        ...     state=ReportState(...)
        ... )
    """
    name: Optional[str] = None
    spec: Optional[ReportSpec] = None
    state: Optional[ReportState] = None

    model_config = {"extra": "allow"}


class ReportOptions(BaseModel):
    """
    Options for creating or editing a report via the Admin API.

    This matches the ReportOptions message from the Rill Admin API.

    Example:
        >>> options = ReportOptions(
        ...     display_name="Weekly Report",
        ...     refresh_cron="0 9 * * 1",
        ...     refresh_time_zone="America/New_York",
        ...     query_name="revenue_metrics",
        ...     export_format=ExportFormat.XLSX,
        ...     email_recipients=["team@example.com"]
        ... )
    """
    display_name: Optional[str] = Field(None, alias="displayName")
    refresh_cron: Optional[str] = Field(None, alias="refreshCron")
    refresh_time_zone: Optional[str] = Field(None, alias="refreshTimeZone")
    interval_duration: Optional[str] = Field(None, alias="intervalDuration")
    query_name: Optional[str] = Field(None, alias="queryName")
    query_args_json: Optional[str] = Field(None, alias="queryArgsJson")
    export_limit: Optional[int] = Field(None, alias="exportLimit")
    export_format: Optional[ExportFormat] = Field(None, alias="exportFormat")
    export_include_header: Optional[bool] = Field(None, alias="exportIncludeHeader")
    email_recipients: Optional[List[str]] = Field(None, alias="emailRecipients")
    slack_users: Optional[List[str]] = Field(None, alias="slackUsers")
    slack_channels: Optional[List[str]] = Field(None, alias="slackChannels")
    slack_webhooks: Optional[List[str]] = Field(None, alias="slackWebhooks")
    web_open_path: Optional[str] = Field(None, alias="webOpenPath")
    web_open_state: Optional[str] = Field(None, alias="webOpenState")
    explore: Optional[str] = None
    canvas: Optional[str] = None
    web_open_mode: Optional[str] = Field(None, alias="webOpenMode")
    filter: Optional[Any] = None  # rill.runtime.v1.Expression

    model_config = {"populate_by_name": True, "extra": "allow"}


# Response models for API operations
class CreateReportResponse(BaseModel):
    """Response from creating a report."""
    name: str

    model_config = {"extra": "allow"}


class EditReportResponse(BaseModel):
    """Response from editing a report."""
    model_config = {"extra": "allow"}


class DeleteReportResponse(BaseModel):
    """Response from deleting a report."""
    model_config = {"extra": "allow"}


class TriggerReportResponse(BaseModel):
    """Response from triggering a report."""
    model_config = {"extra": "allow"}


class UnsubscribeReportResponse(BaseModel):
    """Response from unsubscribing from a report."""
    model_config = {"extra": "allow"}


class GenerateReportYAMLResponse(BaseModel):
    """Response from generating report YAML."""
    yaml: str

    model_config = {"extra": "allow"}
