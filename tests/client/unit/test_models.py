"""
Unit tests for Pydantic models
"""

import pytest
from pydantic import ValidationError

from pyrill.models import Org, Project, Token, ProjectResources, Resource


@pytest.mark.unit
class TestOrgModel:
    """Tests for Org model"""

    def test_org_valid(self):
        """Test creating Org with valid data"""
        org = Org(name="test-org", createdOn="2025-01-01T12:00:00Z")
        assert org.name == "test-org"
        assert org.created_on == "2025-01-01T12:00:00Z"

    def test_org_minimal(self):
        """Test creating Org with minimal data"""
        org = Org(name="test-org")
        assert org.name == "test-org"
        assert org.created_on is None

    def test_org_missing_name(self):
        """Test that missing name raises validation error"""
        with pytest.raises(ValidationError):
            Org(created_on="2025-01-01T12:00:00Z")

    def test_org_model_dump(self):
        """Test model_dump() method"""
        org = Org(name="test-org", displayName="Test Org")
        data = org.model_dump()
        assert data["name"] == "test-org"
        assert data["display_name"] == "Test Org"


@pytest.mark.unit
class TestProjectModel:
    """Tests for Project model"""

    def test_project_valid_full(self):
        """Test creating Project with all fields"""
        project = Project(
            name="test-project",
            orgName="test-org",
            public=True,
            gitRemote="https://github.com/test/repo",
            description="Test project"
        )
        assert project.name == "test-project"
        assert project.org_name == "test-org"
        assert project.public is True
        assert project.git_remote == "https://github.com/test/repo"
        assert project.description == "Test project"

    def test_project_minimal(self):
        """Test creating Project with minimal data"""
        project = Project(name="test-project")
        assert project.name == "test-project"
        assert project.org_name is None
        assert project.public is False
        assert project.git_remote is None

    def test_project_public_default(self):
        """Test that public defaults to False"""
        project = Project(name="test-project")
        assert project.public is False

    def test_project_missing_name(self):
        """Test that missing name raises validation error"""
        with pytest.raises(ValidationError):
            Project(org_name="test-org")


@pytest.mark.unit
class TestTokenModel:
    """Tests for Token model"""

    def test_token_valid_full(self):
        """Test creating Token with all fields"""
        token = Token(
            id="token-123",
            displayName="Test Token",
            prefix="rill_usr_abc",
            authClientDisplayName="Created manually",
            createdOn="2025-01-01T10:00:00Z",
            expiresOn="2025-12-31T23:59:59Z",
            usedOn="2025-01-15T14:00:00Z"
        )
        assert token.id == "token-123"
        assert token.display_name == "Test Token"
        assert token.prefix == "rill_usr_abc"
        assert token.auth_client_display_name == "Created manually"

    def test_token_minimal(self):
        """Test creating Token with minimal data"""
        token = Token(id="token-123", prefix="rill_usr_abc")
        assert token.id == "token-123"
        assert token.prefix == "rill_usr_abc"
        assert token.display_name is None

    def test_token_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            Token(display_name="Test Token")


@pytest.mark.unit
class TestResourceModel:
    """Tests for Resource model"""

    def test_resource_valid(self):
        """Test creating Resource with valid data"""
        resource = Resource(name="test-resource", type="source")
        assert resource.name == "test-resource"
        assert resource.type == "source"

    def test_resource_minimal(self):
        """Test creating Resource with minimal/no data"""
        resource = Resource()
        assert resource.name is None
        assert resource.type is None

    def test_resource_extra_fields(self):
        """Test that Resource allows extra fields"""
        resource = Resource(
            name="test-resource",
            type="source",
            custom_field="custom_value",
            another_field=123
        )
        assert resource.name == "test-resource"
        # Extra fields should be accessible
        assert hasattr(resource, "custom_field")


@pytest.mark.unit
class TestProjectResourcesModel:
    """Tests for ProjectResources model"""

    def test_project_resources_valid(self):
        """Test creating ProjectResources with valid data"""
        resources = ProjectResources(
            resources=[
                Resource(name="source1", type="source"),
                Resource(name="model1", type="model")
            ]
        )
        assert len(resources.resources) == 2
        assert resources.resources[0].name == "source1"
        assert resources.resources[1].name == "model1"

    def test_project_resources_empty(self):
        """Test creating ProjectResources with no resources"""
        resources = ProjectResources()
        assert resources.resources == []

    def test_project_resources_from_dict(self):
        """Test creating ProjectResources from dict"""
        data = {
            "resources": [
                {"name": "source1", "type": "source"},
                {"name": "model1", "type": "model"}
            ]
        }
        resources = ProjectResources(**data)
        assert len(resources.resources) == 2

    def test_project_resources_extra_fields(self):
        """Test that ProjectResources allows extra fields"""
        resources = ProjectResources(
            resources=[],
            metadata={"version": "1.0"},
            custom_field="value"
        )
        assert resources.resources == []
        assert hasattr(resources, "metadata")


@pytest.mark.unit
class TestUserModel:
    """Tests for User model"""

    def test_user_allows_any_fields(self):
        """Test that User model allows arbitrary fields"""
        from pyrill.models import User

        user = User(email="test@example.com", name="Test User")
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_user_empty(self):
        """Test creating User with no data"""
        from pyrill.models import User

        user = User()
        # Should not raise an error
        assert user is not None
