"""
Pytest configuration and fixtures for client tests
"""

import json
from unittest.mock import Mock, MagicMock
import pytest
import httpx

from tests.fixtures.sample_data import (
    SAMPLE_ORGS,
    SAMPLE_PROJECTS,
    SAMPLE_TOKENS,
    SAMPLE_WHOAMI,
    SAMPLE_PROJECT_WITH_DEPLOYMENT,
    SAMPLE_RUNTIME_RESOURCES,
)


@pytest.fixture
def mock_org_name():
    """Provide a test org name"""
    return "test-org-1"


@pytest.fixture
def mock_project_name():
    """Provide a test project name"""
    return "test-project-1"


@pytest.fixture
def sample_orgs():
    """Provide sample org data"""
    return SAMPLE_ORGS.copy()


@pytest.fixture
def sample_projects():
    """Provide sample project data"""
    return SAMPLE_PROJECTS.copy()


@pytest.fixture
def sample_tokens():
    """Provide sample token data"""
    return SAMPLE_TOKENS.copy()


@pytest.fixture
def sample_whoami():
    """Provide sample whoami data"""
    return SAMPLE_WHOAMI.copy()


@pytest.fixture
def sample_runtime_resources():
    """Provide sample runtime resources data"""
    return SAMPLE_RUNTIME_RESOURCES.copy()


@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Mock httpx.Client for REST API requests"""
    def _create_response(data, status_code=200):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.reason_phrase = "OK" if status_code == 200 else "Error"
        mock_response.text = json.dumps(data)
        mock_response.json.return_value = data
        return mock_response

    def _mock_request(method, url, **kwargs):
        """Route requests to appropriate mock responses"""
        # Parse the endpoint from the URL
        endpoint = url.replace("https://api.rilldata.com/v1/", "")

        # Orgs
        if endpoint == "orgs":
            return _create_response({"organizations": SAMPLE_ORGS})
        elif endpoint.startswith("orgs/") and "/projects" not in endpoint:
            org_name = endpoint.split("/")[1]
            org = next((o for o in SAMPLE_ORGS if o["name"] == org_name), None)
            if org:
                return _create_response({"organization": org})
            return _create_response({"error": "Not found"}, 404)

        # Projects
        elif endpoint.endswith("/projects"):
            org_name = endpoint.split("/")[1]
            projects = [p for p in SAMPLE_PROJECTS if p["orgName"] == org_name]
            return _create_response({"projects": projects})
        elif "/projects/" in endpoint and "/runtime/resources" not in endpoint:
            parts = endpoint.split("/")
            org_name = parts[1]
            project_name = parts[3]
            project = next((p for p in SAMPLE_PROJECTS if p["name"] == project_name and p["orgName"] == org_name), None)
            if project:
                return _create_response(SAMPLE_PROJECT_WITH_DEPLOYMENT)
            return _create_response({"error": "Not found"}, 404)

        # Tokens
        elif endpoint == "users/current/tokens":
            return _create_response({"tokens": SAMPLE_TOKENS})

        # Whoami
        elif endpoint == "users/current":
            return _create_response({"user": SAMPLE_WHOAMI})

        # Runtime resources
        elif "/runtime/resources" in endpoint:
            return _create_response(SAMPLE_RUNTIME_RESOURCES)

        # Default fallback
        return _create_response({"error": "Not found"}, 404)

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None
    mock_client_instance.request.side_effect = _mock_request

    mock_client_class = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(httpx, "Client", mock_client_class)

    return mock_client_instance


@pytest.fixture
def rill_client_with_mocks(mock_env_with_token, mock_httpx_client, monkeypatch):
    """
    Create a RillClient with all external dependencies mocked.

    This fixture provides a fully functional client for testing without
    making real API calls.
    """
    from pyrill import RillClient
    monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org-1")
    monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project-1")
    return RillClient()
