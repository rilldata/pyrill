"""
Integration tests for RillClient methods

These tests use mocked CLI and API responses but test the full client logic.
"""

import pytest
from unittest.mock import Mock

from pyrill import RillClient
from pyrill.models import Org, Project, Token, ProjectResources
from pyrill.exceptions import RillAPIError


@pytest.mark.integration
class TestOrgOperations:
    """Integration tests for org operations"""

    def test_list_orgs(self, rill_client_with_mocks, sample_orgs):
        """Test listing orgs"""
        orgs = rill_client_with_mocks.orgs.list()

        assert len(orgs) == len(sample_orgs)
        assert all(isinstance(org, Org) for org in orgs)
        assert orgs[0].name == sample_orgs[0]["name"]

    def test_get_org_success(self, rill_client_with_mocks):
        """Test getting a specific org"""
        org = rill_client_with_mocks.orgs.get("test-org-1")

        assert isinstance(org, Org)
        assert org.name == "test-org-1"

    def test_get_org_not_found(self, rill_client_with_mocks):
        """Test getting non-existent org raises error"""
        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.orgs.get("nonexistent-org")

        assert "not found" in str(exc_info.value).lower()


@pytest.mark.integration
class TestProjectOperations:
    """Integration tests for project operations"""

    def test_list_all_projects(self, rill_client_with_mocks, sample_projects):
        """Test listing all projects"""
        projects = rill_client_with_mocks.projects.list()

        assert len(projects) == len(sample_projects)
        assert all(isinstance(proj, Project) for proj in projects)

    def test_list_projects_filtered_by_org(self, rill_client_with_mocks):
        """Test listing projects filtered by organization"""
        projects = rill_client_with_mocks.projects.list(org_name="test-org-1")

        assert len(projects) == 2  # test-org-1 has 2 projects in sample data
        assert all(proj.org_name == "test-org-1" for proj in projects)

    def test_list_projects_no_matches(self, rill_client_with_mocks):
        """Test listing projects for org with no projects"""
        projects = rill_client_with_mocks.projects.list(org_name="empty-org")

        assert len(projects) == 0

    def test_get_project_success(self, rill_client_with_mocks):
        """Test getting a specific project"""
        project = rill_client_with_mocks.projects.get("test-project-1")

        assert isinstance(project, Project)
        assert project.name == "test-project-1"

    def test_get_project_with_org_filter(self, rill_client_with_mocks):
        """Test getting project with organization filter"""
        project = rill_client_with_mocks.projects.get(
            "test-project-1",
            org_name="test-org-1"
        )

        assert isinstance(project, Project)
        assert project.name == "test-project-1"
        assert project.org_name == "test-org-1"

    def test_get_project_not_found(self, rill_client_with_mocks):
        """Test getting non-existent project raises error"""
        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.projects.get("nonexistent-project")

        assert "not found" in str(exc_info.value).lower()


@pytest.mark.integration
class TestTokenOperations:
    """Integration tests for token operations"""

    def test_list_tokens(self, rill_client_with_mocks, sample_tokens):
        """Test listing tokens"""
        tokens = rill_client_with_mocks.auth.list_tokens()

        assert len(tokens) == len(sample_tokens)
        assert all(isinstance(token, Token) for token in tokens)
        assert tokens[0].prefix.startswith("rill_usr_")


@pytest.mark.integration
class TestRuntimeResourceOperations:
    """Integration tests for runtime resource operations"""

    def test_get_project_resources(
        self,
        rill_client_with_mocks,
        mock_org_name,
        mock_project_name
    ):
        """Test getting runtime resources"""
        resources = rill_client_with_mocks.projects.get_resources(
            mock_project_name,
            org=mock_org_name
        )

        assert isinstance(resources, ProjectResources)
        assert len(resources.resources) > 0


@pytest.mark.integration
class TestUserOperations:
    """Integration tests for user operations"""

    def test_whoami(self, rill_client_with_mocks, sample_whoami):
        """Test whoami command"""
        from pyrill.models import User

        user = rill_client_with_mocks.auth.whoami()

        assert isinstance(user, User)
        assert user.email == "test@example.com"


@pytest.mark.integration
class TestErrorScenarios:
    """Integration tests for error handling scenarios"""

    def test_api_request_failure(self, rill_client_with_mocks, monkeypatch):
        """Test handling of API request failure"""
        from unittest.mock import MagicMock

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(*args, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 500
                mock_response.reason_phrase = "Internal Server Error"
                mock_response.text = "Server error"
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.projects.get_resources("test-project", org="test-org")

        assert exc_info.value.status_code == 500
