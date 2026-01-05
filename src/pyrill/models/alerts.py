"""
Pydantic models for Rill Alert resources.

These models represent alert configurations, schedules, and execution state
for alerts in Rill.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Schedule(BaseModel):
    """
    Schedule configuration for alert execution.

    Example:
        >>> schedule = Schedule(
        ...     cron="0 * * * *",
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
    Notification configuration for alert delivery.

    Example:
        >>> notifier = Notifier(
        ...     connector="email",
        ...     properties={"recipients": ["user@example.com"]}
        ... )
    """
    connector: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class AlertSpec(BaseModel):
    """
    Alert specification containing configuration and scheduling details.

    Example:
        >>> spec = AlertSpec(
        ...     display_name="Revenue Drop Alert",
        ...     refresh_schedule=Schedule(cron="0 * * * *"),
        ...     resolver="metrics_threshold",
        ...     metrics_view_name="revenue_metrics"
        ... )
    """
    display_name: Optional[str] = Field(None, alias="displayName")
    trigger: Optional[bool] = None
    refresh_schedule: Optional[Schedule] = Field(None, alias="refreshSchedule")
    timeout_seconds: Optional[int] = Field(None, alias="timeoutSeconds")
    resolver: Optional[str] = None
    resolver_properties: Optional[Dict[str, Any]] = Field(None, alias="resolverProperties")
    query_name: Optional[str] = Field(None, alias="queryName")
    query_args_json: Optional[str] = Field(None, alias="queryArgsJson")
    metrics_view_name: Optional[str] = Field(None, alias="metricsViewName")
    renotify: Optional[bool] = None
    renotify_after_seconds: Optional[int] = Field(None, alias="renotifyAfterSeconds")
    notifiers: Optional[List[Notifier]] = None
    annotations: Optional[Dict[str, str]] = None
    watermark_inherit: Optional[bool] = Field(None, alias="watermarkInherit")
    intervals_iso_duration: Optional[str] = Field(None, alias="intervalsIsoDuration")
    intervals_limit: Optional[int] = Field(None, alias="intervalsLimit")
    intervals_check_unclosed: Optional[bool] = Field(None, alias="intervalsCheckUnclosed")

    model_config = {"populate_by_name": True, "extra": "allow"}


class AlertExecution(BaseModel):
    """
    Single execution record for an alert run.

    Example:
        >>> execution = AlertExecution(
        ...     adhoc=False,
        ...     started_on="2024-01-15T09:00:00Z",
        ...     finished_on="2024-01-15T09:02:30Z"
        ... )
    """
    adhoc: Optional[bool] = None
    error_message: Optional[str] = Field(None, alias="errorMessage")
    sent: Optional[bool] = None
    sent_time: Optional[str] = Field(None, alias="sentTime")
    result_time: Optional[str] = Field(None, alias="resultTime")
    execution_time: Optional[str] = Field(None, alias="executionTime")
    started_on: Optional[str] = Field(None, alias="startedOn")
    finished_on: Optional[str] = Field(None, alias="finishedOn")

    model_config = {"populate_by_name": True, "extra": "allow"}


class AlertState(BaseModel):
    """
    Alert state containing execution status and history.

    Example:
        >>> state = AlertState(
        ...     next_run_on="2024-01-22T09:00:00Z",
        ...     execution_count=10,
        ...     execution_history=[...]
        ... )
    """
    next_run_on: Optional[str] = Field(None, alias="nextRunOn")
    current_execution: Optional[AlertExecution] = Field(None, alias="currentExecution")
    execution_history: Optional[List[AlertExecution]] = Field(None, alias="executionHistory")
    execution_count: Optional[int] = Field(None, alias="executionCount")

    model_config = {"populate_by_name": True, "extra": "allow"}


class Alert(BaseModel):
    """
    Complete alert resource with spec and state.

    Example:
        >>> alert = Alert(
        ...     name="revenue-drop",
        ...     spec=AlertSpec(...),
        ...     state=AlertState(...)
        ... )
    """
    name: Optional[str] = None
    spec: Optional[AlertSpec] = None
    state: Optional[AlertState] = None

    model_config = {"extra": "allow"}


class AlertOptions(BaseModel):
    """
    Options for creating or editing an alert via the Admin API.

    This matches the AlertOptions message from the Rill Admin API.

    Example:
        >>> options = AlertOptions(
        ...     display_name="Revenue Drop Alert",
        ...     refresh_cron="0 * * * *",
        ...     refresh_time_zone="America/New_York",
        ...     resolver="metrics_threshold",
        ...     metrics_view_name="revenue_metrics",
        ...     email_recipients=["team@example.com"]
        ... )
    """
    display_name: Optional[str] = Field(None, alias="displayName")
    refresh_cron: Optional[str] = Field(None, alias="refreshCron")
    refresh_time_zone: Optional[str] = Field(None, alias="refreshTimeZone")
    interval_duration: Optional[str] = Field(None, alias="intervalDuration")
    resolver: Optional[str] = None
    resolver_properties: Optional[Dict[str, Any]] = Field(None, alias="resolverProperties")
    query_name: Optional[str] = Field(None, alias="queryName")
    query_args_json: Optional[str] = Field(None, alias="queryArgsJson")
    metrics_view_name: Optional[str] = Field(None, alias="metricsViewName")
    renotify: Optional[bool] = None
    renotify_after_seconds: Optional[int] = Field(None, alias="renotifyAfterSeconds")
    email_recipients: Optional[List[str]] = Field(None, alias="emailRecipients")
    slack_users: Optional[List[str]] = Field(None, alias="slackUsers")
    slack_channels: Optional[List[str]] = Field(None, alias="slackChannels")
    slack_webhooks: Optional[List[str]] = Field(None, alias="slackWebhooks")
    web_open_path: Optional[str] = Field(None, alias="webOpenPath")
    web_open_state: Optional[str] = Field(None, alias="webOpenState")

    model_config = {"populate_by_name": True, "extra": "allow"}


# Response models for API operations
class CreateAlertResponse(BaseModel):
    """Response from creating an alert."""
    name: str

    model_config = {"extra": "allow"}


class EditAlertResponse(BaseModel):
    """Response from editing an alert."""
    model_config = {"extra": "allow"}


class DeleteAlertResponse(BaseModel):
    """Response from deleting an alert."""
    model_config = {"extra": "allow"}


class UnsubscribeAlertResponse(BaseModel):
    """Response from unsubscribing from an alert."""
    model_config = {"extra": "allow"}


class GetAlertYAMLResponse(BaseModel):
    """Response from getting alert YAML."""
    yaml: str

    model_config = {"extra": "allow"}


class GenerateAlertYAMLResponse(BaseModel):
    """Response from generating alert YAML."""
    yaml: str

    model_config = {"extra": "allow"}
