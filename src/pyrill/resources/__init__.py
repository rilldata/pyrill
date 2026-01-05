"""
Resource classes for organizing RillClient methods
"""

from .base import BaseResource
from .auth import AuthResource
from .orgs import OrgsResource
from .projects import ProjectsResource
from .query import QueryResource
from .annotations import AnnotationsResource
from .reports import ReportsResource
from .alerts import AlertsResource
from .iframes import IFramesResource
from .partitions import PartitionsResource
from .users import UsersResource
from .usergroups import UsergroupsResource
from .publicurls import PublicUrlsResource

__all__ = [
    "BaseResource",
    "AuthResource",
    "OrgsResource",
    "ProjectsResource",
    "QueryResource",
    "AnnotationsResource",
    "ReportsResource",
    "AlertsResource",
    "IFramesResource",
    "PartitionsResource",
    "UsersResource",
    "UsergroupsResource",
    "PublicUrlsResource",
]
