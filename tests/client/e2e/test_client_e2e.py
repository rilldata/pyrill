"""
End-to-end tests for RillClient

These tests require real credentials and make actual API/CLI calls.
Run with: pytest tests/e2e/ --run-e2e
"""

import os
import pytest

from pyrill import RillClient
from pyrill.models import Org, Project, Token, ProjectResources, ProjectStatus
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT


@pytest.mark.e2e
class TestE2EClientBasics:
    """E2E tests for basic client operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        # Ensure RILL_USER_TOKEN is set
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        # Use configured test org/project as defaults
        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    def test_whoami(self, client):
        """Test whoami returns user information"""
        from pyrill.models import User

        user = client.auth.whoami()

        assert isinstance(user, User)
        assert user.id is not None
        # At least one of email or name should be present
        assert user.email or user.name or user.display_name

    def test_list_orgs(self, client):
        """Test listing orgs"""
        orgs = client.orgs.list()

        assert isinstance(orgs, list)
        assert all(isinstance(org, Org) for org in orgs)

        if orgs:
            assert orgs[0].name is not None

    def test_get_org(self, client):
        """Test getting a specific org"""
        # First get the list of orgs to get a valid org name
        orgs = client.orgs.list()

        if not orgs:
            pytest.skip("No orgs available for testing")

        org_name = orgs[0].name
        org = client.orgs.get(org_name)

        assert isinstance(org, Org)
        assert org.name == org_name

    def test_list_projects(self, client):
        """Test listing projects"""
        projects = client.projects.list()

        assert isinstance(projects, list)
        assert all(isinstance(proj, Project) for proj in projects)

    def test_get_project(self, client):
        """Test getting a specific project"""
        # First get the list of projects to get a valid project and org
        projects = client.projects.list()

        if not projects:
            pytest.skip("No projects available for testing")

        project = projects[0]
        org_name = project.org_name
        project_name = project.name

        # Get the specific project
        fetched_project = client.projects.get(project_name, org_name)

        assert isinstance(fetched_project, Project)
        assert fetched_project.name == project_name
        assert fetched_project.org_name == org_name

    def test_list_tokens(self, client):
        """Test listing tokens"""
        tokens = client.auth.list_tokens()

        assert isinstance(tokens, list)
        assert all(isinstance(token, Token) for token in tokens)

        if tokens:
            assert tokens[0].prefix.startswith("rill_")


@pytest.mark.e2e
class TestE2ERuntimeResources:
    """E2E tests for runtime resources"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        # Use configured test org/project as defaults
        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def test_org_and_project(self):
        """Return configured test organization and project"""
        # Use configured constants instead of dynamically picking from list
        return TEST_ORG, TEST_PROJECT

    def test_get_project_resources(self, client, test_org_and_project):
        """Test getting runtime resources for a real project"""
        org_name, project_name = test_org_and_project

        if not org_name or not project_name:
            pytest.skip("No valid org/project for testing")

        resources = client.projects.get_resources(project_name, org=org_name)

        assert isinstance(resources, ProjectResources)
        # Resources list might be empty, that's ok
        assert isinstance(resources.resources, list)

    def test_project_status(self, client, test_org_and_project):
        """Test getting project status"""
        org_name, project_name = test_org_and_project

        if not org_name or not project_name:
            pytest.skip("No valid org/project for testing")

        status = client.projects.status(project_name, org=org_name)

        assert isinstance(status, ProjectStatus)
        assert status.project is not None
        assert status.deployment is not None
        assert status.project.name == project_name
        assert status.project.org == org_name


@pytest.mark.e2e
class TestE2EErrorHandling:
    """E2E tests for error handling with real API"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        # Use configured test org/project as defaults
        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    def test_get_nonexistent_org(self, client):
        """Test getting a non-existent org"""
        with pytest.raises(RillError):
            client.orgs.get("nonexistent-org-12345")

    def test_get_nonexistent_project(self, client):
        """Test getting a non-existent project"""
        with pytest.raises(RillError):
            client.projects.get("nonexistent-project-12345")

    def test_get_resources_for_invalid_project(self, client):
        """Test getting resources for invalid project"""
        with pytest.raises(RillError):
            client.projects.get_resources(
                "nonexistent-project",
                org="nonexistent-org"
            )
