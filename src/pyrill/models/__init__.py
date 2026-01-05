"""
Pydantic models for PyRill SDK.

This module re-exports all models for backward compatibility.
"""

# Core models (users, tokens)
from .core import (
    Token,
    User,
)

# Organization models
from .orgs import (
    Org,
)

# Project models (projects, deployments, resources)
from .projects import (
    Project,
    Deployment,
    Resource,
    ProjectResources,
    ProjectStatus,
    ProjectStatusInfo,
    DeploymentStatusInfo,
    ResourceName,
)

# Public URL models (magic auth tokens, public URLs)
from .publicurls import (
    MagicAuthToken,
    CreatePublicUrlResponse,
)

# Query models
from .query import (
    Operator,
    TimeGrain,
    Expression,
    Condition,
    Dimension,
    DimensionCompute,
    DimensionComputeTimeFloor,
    Measure,
    MeasureCompute,
    MeasureComputeCountDistinct,
    MeasureComputeComparisonValue,
    MeasureComputeComparisonDelta,
    MeasureComputeComparisonRatio,
    MeasureComputePercentOfTotal,
    MeasureComputeURI,
    Subquery,
    Sort,
    TimeRange,
    TimeSpine,
    WhereSpine,
    Spine,
    MetricsQuery,
    MetricsSqlQuery,
    SqlQuery,
    QueryResult,
)

# Annotation models
from .annotations import (
    Annotation,
    AnnotationsQuery,
    AnnotationsResponse,
)

# Navigation models (URL building)
from .navigation import RillUrl

# Report models
from .reports import (
    ExportFormat,
    Schedule,
    Notifier,
    ReportSpec,
    ReportExecution,
    ReportState,
    Report,
    ReportOptions,
    CreateReportResponse,
    EditReportResponse,
    DeleteReportResponse,
    TriggerReportResponse,
    UnsubscribeReportResponse,
    GenerateReportYAMLResponse,
)

# Partition models
from .partitions import (
    ModelPartition,
    PartitionsList,
)

# User and usergroup models
from .users import (
    OrganizationMemberUser,
    MemberUsergroup,
    Usergroup,
)

# Alert models
from .alerts import (
    Alert,
    AlertOptions,
    AlertSpec,
    AlertExecution,
    AlertState,
    CreateAlertResponse,
    EditAlertResponse,
    DeleteAlertResponse,
    UnsubscribeAlertResponse,
    GetAlertYAMLResponse,
    GenerateAlertYAMLResponse,
)

# Annotation models
from .annotations import (
    Annotation,
    AnnotationsQuery,
    AnnotationsResponse,
)

# IFrame models
from .iframe import (
    IFrameOptions,
    IFrameResponse,
)

__all__ = [
    # Core models
    "Org",
    "Project",
    "Token",
    "User",
    "Deployment",
    "Resource",
    "ProjectResources",
    "ProjectStatus",
    "ProjectStatusInfo",
    "DeploymentStatusInfo",
    "ResourceName",
    "MagicAuthToken",
    "CreatePublicUrlResponse",
    # Query models
    "Operator",
    "TimeGrain",
    "Expression",
    "Condition",
    "Dimension",
    "DimensionCompute",
    "DimensionComputeTimeFloor",
    "Measure",
    "MeasureCompute",
    "MeasureComputeCountDistinct",
    "MeasureComputeComparisonValue",
    "MeasureComputeComparisonDelta",
    "MeasureComputeComparisonRatio",
    "MeasureComputePercentOfTotal",
    "MeasureComputeURI",
    "Subquery",
    "Sort",
    "TimeRange",
    "TimeSpine",
    "WhereSpine",
    "Spine",
    "MetricsQuery",
    "MetricsSqlQuery",
    "SqlQuery",
    "QueryResult",
    # Annotation models
    "Annotation",
    "AnnotationsQuery",
    "AnnotationsResponse",
    # Navigation models
    "RillUrl",
    # Report models
    "ExportFormat",
    "Schedule",
    "Notifier",
    "ReportSpec",
    "ReportExecution",
    "ReportState",
    "Report",
    "ReportOptions",
    "CreateReportResponse",
    "EditReportResponse",
    "DeleteReportResponse",
    "TriggerReportResponse",
    "UnsubscribeReportResponse",
    "GenerateReportYAMLResponse",
    # Partition models
    "ModelPartition",
    "PartitionsList",
    # User and usergroup models
    "OrganizationMemberUser",
    "MemberUsergroup",
    "Usergroup",
    # Alert models
    "Alert",
    "AlertOptions",
    "AlertSpec",
    "AlertExecution",
    "AlertState",
    "CreateAlertResponse",
    "EditAlertResponse",
    "DeleteAlertResponse",
    "UnsubscribeAlertResponse",
    "GetAlertYAMLResponse",
    "GenerateAlertYAMLResponse",
    # Annotation models
    "Annotation",
    "AnnotationsQuery",
    "AnnotationsResponse",
    # IFrame models
    "IFrameOptions",
    "IFrameResponse",
]
