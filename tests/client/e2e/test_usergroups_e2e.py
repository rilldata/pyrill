"""E2E tests for usergroups resource (read-only operations only)"""

import os
import json
import pytest
from pathlib import Path
from pyrill import RillClient
from pyrill.models import MemberUsergroup, Usergroup
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT


@pytest.mark.e2e
class TestE2EUsergroups:
    """E2E tests for usergroups resource"""

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
        debug_path = Path(__file__).parent.parent.parent / "debug" / "usergroups"
        debug_path.mkdir(parents=True, exist_ok=True)
        print(f"Debug directory created at: {debug_path.absolute()}")
        return debug_path

    def test_list_usergroups_uses_defaults(self, client, debug_dir):
        """Test listing usergroups using client default org"""
        groups = client.usergroups.list()

        assert isinstance(groups, list)
        assert all(isinstance(g, MemberUsergroup) for g in groups)

        if groups:
            assert groups[0].group_name is not None

        # Save response for manual review
        (debug_dir / "list_usergroups_defaults.json").write_text(
            json.dumps([g.model_dump() for g in groups], indent=2)
        )

    @pytest.mark.xfail(reason="May fail with 403 if no permissions to access other org")
    def test_list_usergroups_override_org(self, client, debug_dir):
        """Test listing usergroups with explicit org override"""
        # Get first available org
        orgs = client.organizations.list()
        if not orgs:
            pytest.skip("No organizations available")

        test_org = orgs[0].name

        try:
            groups = client.usergroups.list(org=test_org)

            assert isinstance(groups, list)
            assert all(isinstance(g, MemberUsergroup) for g in groups)

            # Save response for manual review
            (debug_dir / "list_usergroups_override_org.json").write_text(
                json.dumps([g.model_dump() for g in groups], indent=2)
            )
        except RillError as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "test_org": test_org,
                "available_orgs": [o.name for o in orgs]
            }
            # Save error for manual review
            (debug_dir / "list_usergroups_override_org_error.json").write_text(
                json.dumps(error_info, indent=2)
            )
            raise

    def test_get_usergroup_uses_defaults(self, client, debug_dir):
        """Test getting a specific usergroup using client defaults"""
        groups = client.usergroups.list()

        if not groups:
            pytest.skip("No usergroups available for testing")

        # Get first group's name
        test_group_name = groups[0].group_name
        if not test_group_name:
            pytest.skip("Group has no name")

        group = client.usergroups.get(test_group_name)

        assert isinstance(group, Usergroup)
        assert group.group_name == test_group_name

        # Save response for manual review
        (debug_dir / "get_usergroup_defaults.json").write_text(
            json.dumps(group.model_dump(), indent=2)
        )

    @pytest.mark.xfail(reason="May fail with 403 if no permissions to access other org")
    def test_get_usergroup_override_org(self, client, debug_dir):
        """Test getting a specific usergroup with explicit org override"""
        # Get first available org
        orgs = client.organizations.list()
        if not orgs:
            pytest.skip("No organizations available")

        test_org = orgs[0].name

        try:
            groups = client.usergroups.list(org=test_org)

            if not groups:
                pytest.skip("No usergroups available for testing")

            test_group_name = groups[0].group_name
            if not test_group_name:
                pytest.skip("Group has no name")

            group = client.usergroups.get(test_group_name, org=test_org)

            assert isinstance(group, Usergroup)
            assert group.group_name == test_group_name

            # Save response for manual review
            (debug_dir / "get_usergroup_override_org.json").write_text(
                json.dumps(group.model_dump(), indent=2)
            )
        except RillError as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "test_org": test_org,
                "available_orgs": [o.name for o in orgs]
            }
            # Save error for manual review
            (debug_dir / "get_usergroup_override_org_error.json").write_text(
                json.dumps(error_info, indent=2)
            )
            raise

    def test_get_usergroup_positional_vs_named(self, client, debug_dir):
        """Test both positional and named parameter styles for get()"""
        groups = client.usergroups.list()

        if not groups:
            pytest.skip("No usergroups available for testing")

        test_group_name = groups[0].group_name
        if not test_group_name:
            pytest.skip("Group has no name")

        # Positional
        group1 = client.usergroups.get(test_group_name)

        # Named
        group2 = client.usergroups.get(usergroup=test_group_name)

        assert isinstance(group1, Usergroup)
        assert isinstance(group2, Usergroup)
        assert group1.group_name == group2.group_name

        # Save response for manual review
        (debug_dir / "get_usergroup_positional_vs_named.json").write_text(
            json.dumps({
                "positional": group1.model_dump(),
                "named": group2.model_dump()
            }, indent=2)
        )

    def test_get_nonexistent_usergroup(self, client, debug_dir):
        """Test error handling for non-existent usergroup"""
        with pytest.raises(RillError) as exc_info:
            client.usergroups.get("nonexistent-group-12345")

        # Save error for manual review
        error_info = {
            "error_type": type(exc_info.value).__name__,
            "error_message": str(exc_info.value),
            "test_usergroup": "nonexistent-group-12345"
        }
        (debug_dir / "get_nonexistent_usergroup_error.json").write_text(
            json.dumps(error_info, indent=2)
        )

    def test_show_usergroup_alias(self, client, debug_dir):
        """Test that show() is an alias for get()"""
        groups = client.usergroups.list()

        if not groups:
            pytest.skip("No usergroups available for testing")

        test_group_name = groups[0].group_name
        if not test_group_name:
            pytest.skip("Group has no name")

        # Both methods should return the same result
        group_get = client.usergroups.get(test_group_name)
        group_show = client.usergroups.show(test_group_name)

        assert isinstance(group_get, Usergroup)
        assert isinstance(group_show, Usergroup)
        assert group_get.group_name == group_show.group_name

        # Save response for manual review
        (debug_dir / "show_usergroup_alias.json").write_text(
            json.dumps({
                "get_result": group_get.model_dump(),
                "show_result": group_show.model_dump()
            }, indent=2)
        )
