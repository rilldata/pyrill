"""E2E tests for users resource (read-only operations only)"""

import os
import json
import pytest
from pathlib import Path
from pyrill import RillClient
from pyrill.models import OrganizationMemberUser
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT


@pytest.mark.e2e
class TestE2EUsers:
    """E2E tests for users resource"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")
        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def debug_dir(self):
        """Create debug directory for saving API responses"""
        # Path is relative to the test file location
        debug_path = Path(__file__).parent.parent.parent / "debug" / "users"
        debug_path.mkdir(parents=True, exist_ok=True)
        print(f"Debug directory created at: {debug_path.absolute()}")
        return debug_path

    def test_list_users_uses_defaults(self, client, debug_dir):
        """Test listing users using client default org"""
        users = client.users.list()

        assert isinstance(users, list)
        assert all(isinstance(u, OrganizationMemberUser) for u in users)

        if users:
            assert users[0].user_email is not None or users[0].user_name is not None

        # Save response for manual review
        (debug_dir / "list_users_defaults.json").write_text(
            json.dumps([u.model_dump() for u in users], indent=2)
        )

    @pytest.mark.xfail(reason="May fail with 403 if no permissions to access other org")
    def test_list_users_override_org(self, client, debug_dir):
        """Test listing users with explicit org override"""
        # Get first available org
        orgs = client.organizations.list()
        if not orgs:
            pytest.skip("No organizations available")

        test_org = orgs[0].name

        try:
            users = client.users.list(org=test_org)

            assert isinstance(users, list)
            assert all(isinstance(u, OrganizationMemberUser) for u in users)

            # Save response for manual review
            (debug_dir / "list_users_override_org.json").write_text(
                json.dumps([u.model_dump() for u in users], indent=2)
            )
        except RillError as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "test_org": test_org,
                "available_orgs": [o.name for o in orgs]
            }
            # Save error for manual review
            (debug_dir / "list_users_override_org_error.json").write_text(
                json.dumps(error_info, indent=2)
            )
            raise

    def test_get_user_uses_defaults(self, client, debug_dir):
        """Test getting a specific user by email using client defaults"""
        users = client.users.list()

        if not users:
            pytest.skip("No users available for testing")

        # Get first user's email
        test_email = users[0].user_email
        if not test_email:
            pytest.skip("User has no email address")

        user = client.users.get(test_email)

        assert isinstance(user, OrganizationMemberUser)
        assert user.user_email == test_email

        # Save response for manual review
        (debug_dir / "get_user_defaults.json").write_text(
            json.dumps(user.model_dump(), indent=2)
        )

    @pytest.mark.xfail(reason="May fail with 403 if no permissions to access other org")
    def test_get_user_override_org(self, client, debug_dir):
        """Test getting a specific user with explicit org override"""
        # Get first available org
        orgs = client.organizations.list()
        if not orgs:
            pytest.skip("No organizations available")

        test_org = orgs[0].name

        try:
            users = client.users.list(org=test_org)

            if not users:
                pytest.skip("No users available for testing")

            test_email = users[0].user_email
            if not test_email:
                pytest.skip("User has no email address")

            user = client.users.get(test_email, org=test_org)

            assert isinstance(user, OrganizationMemberUser)
            assert user.user_email == test_email

            # Save response for manual review
            (debug_dir / "get_user_override_org.json").write_text(
                json.dumps(user.model_dump(), indent=2)
            )
        except RillError as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "test_org": test_org,
                "available_orgs": [o.name for o in orgs]
            }
            # Save error for manual review
            (debug_dir / "get_user_override_org_error.json").write_text(
                json.dumps(error_info, indent=2)
            )
            raise

    def test_get_user_positional_vs_named(self, client, debug_dir):
        """Test both positional and named parameter styles for get()"""
        users = client.users.list()

        if not users:
            pytest.skip("No users available for testing")

        test_email = users[0].user_email
        if not test_email:
            pytest.skip("User has no email address")

        # Positional
        user1 = client.users.get(test_email)

        # Named
        user2 = client.users.get(email=test_email)

        assert isinstance(user1, OrganizationMemberUser)
        assert isinstance(user2, OrganizationMemberUser)
        assert user1.user_email == user2.user_email

        # Save response for manual review
        (debug_dir / "get_user_positional_vs_named.json").write_text(
            json.dumps({
                "positional": user1.model_dump(),
                "named": user2.model_dump()
            }, indent=2)
        )

    def test_get_nonexistent_user(self, client, debug_dir):
        """Test error handling for non-existent user"""
        with pytest.raises(RillError) as exc_info:
            client.users.get("nonexistent-user@example.com")

        # Save error for manual review
        error_info = {
            "error_type": type(exc_info.value).__name__,
            "error_message": str(exc_info.value),
            "test_email": "nonexistent-user@example.com"
        }
        (debug_dir / "get_nonexistent_user_error.json").write_text(
            json.dumps(error_info, indent=2)
        )

    def test_show_user_alias(self, client, debug_dir):
        """Test that show() is an alias for get()"""
        users = client.users.list()

        if not users:
            pytest.skip("No users available for testing")

        test_email = users[0].user_email
        if not test_email:
            pytest.skip("User has no email address")

        # Both methods should return the same result
        user_get = client.users.get(test_email)
        user_show = client.users.show(test_email)

        assert isinstance(user_get, OrganizationMemberUser)
        assert isinstance(user_show, OrganizationMemberUser)
        assert user_get.user_email == user_show.user_email

        # Save response for manual review
        (debug_dir / "show_user_alias.json").write_text(
            json.dumps({
                "get_result": user_get.model_dump(),
                "show_result": user_show.model_dump()
            }, indent=2)
        )
