"""
End-to-end tests for Alerts resource

These tests require real credentials and make actual API calls.
Run with: pytest tests/client/e2e/test_alerts.py --run-e2e -v
"""

import os
import json
import pytest
from pathlib import Path

from pyrill import RillClient
from pyrill.models.alerts import Alert
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT

# Debug output directory
DEBUG_DIR = Path(__file__).parent.parent.parent / "debug" / "alerts"


def save_debug_output(test_name: str, data: dict):
    """Save debug output for inspection"""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DEBUG_DIR / f"{test_name}.json"
    filepath.write_text(json.dumps(data, indent=2, default=str))
    print(f"\n📝 Debug output saved to: {filepath}")


@pytest.mark.e2e
class TestE2EAlertsRead:
    """E2E tests for read-only alert operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def debug_dir(self):
        """Create debug directory for saving API responses"""
        # Ensure debug directory exists
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Debug directory created at: {DEBUG_DIR.absolute()}")
        return DEBUG_DIR

    def test_list_alerts(self, client, debug_dir):
        """Test listing all alerts for a project"""
        print("\n" + "="*80)
        print("TEST: List Alerts")
        print("="*80)

        alerts = client.alerts.list()

        assert isinstance(alerts, list), f"Expected list, got {type(alerts)}"
        assert all(isinstance(alert, Alert) for alert in alerts), "Not all items are Alert instances"

        print(f"✅ Found {len(alerts)} alerts")

        # Save debug output
        alerts_data = []
        for alert in alerts:
            alert_dict = {
                "name": alert.name,
                "spec": {
                    "display_name": alert.spec.display_name if alert.spec else None,
                    "resolver": alert.spec.resolver if alert.spec else None,
                    "metrics_view_name": alert.spec.metrics_view_name if alert.spec else None,
                    "refresh_schedule": {
                        "cron": alert.spec.refresh_schedule.cron if alert.spec and alert.spec.refresh_schedule else None,
                        "time_zone": alert.spec.refresh_schedule.time_zone if alert.spec and alert.spec.refresh_schedule else None,
                    } if alert.spec and alert.spec.refresh_schedule else None,
                } if alert.spec else None,
                "state": {
                    "next_run_on": alert.state.next_run_on if alert.state else None,
                    "execution_count": alert.state.execution_count if alert.state else None,
                } if alert.state else None
            }
            alerts_data.append(alert_dict)
            print(f"  • {alert.name}")
            if alert.spec:
                print(f"    Display Name: {alert.spec.display_name}")
                if alert.spec.refresh_schedule:
                    print(f"    Schedule: {alert.spec.refresh_schedule.cron}")

        save_debug_output("test_list_alerts", {
            "test": "list_alerts",
            "count": len(alerts),
            "alerts": alerts_data
        })

        # Verify structure
        assert len(alerts) > 0, "Expected at least one alert in demo project"

        # Verify first alert structure
        if alerts:
            alert = alerts[0]
            assert alert.name is not None, "Alert should have a name"
            # Alert should have spec or state (or both)
            assert alert.spec is not None or alert.state is not None, "Alert should have spec or state"

    def test_get_alert(self, client, debug_dir):
        """Test getting a specific alert by name"""
        print("\n" + "="*80)
        print("TEST: Get Alert")
        print("="*80)

        # First list all alerts to find one that exists
        alerts = client.alerts.list()

        if not alerts:
            pytest.skip("No alerts available for testing")

        # Get the first alert by name
        alert_name = alerts[0].name
        print(f"Getting alert: {alert_name}")

        alert = client.alerts.get(alert_name)

        assert isinstance(alert, Alert), f"Expected Alert, got {type(alert)}"
        assert alert.name == alert_name, f"Expected name {alert_name}, got {alert.name}"

        print(f"✅ Got alert: {alert.name}")

        # Save debug output
        alert_data = {
            "name": alert.name,
            "spec": {
                "display_name": alert.spec.display_name if alert.spec else None,
                "resolver": alert.spec.resolver if alert.spec else None,
                "resolver_properties": alert.spec.resolver_properties if alert.spec else None,
                "metrics_view_name": alert.spec.metrics_view_name if alert.spec else None,
                "renotify": alert.spec.renotify if alert.spec else None,
                "renotify_after_seconds": alert.spec.renotify_after_seconds if alert.spec else None,
                "refresh_schedule": {
                    "cron": alert.spec.refresh_schedule.cron if alert.spec and alert.spec.refresh_schedule else None,
                    "time_zone": alert.spec.refresh_schedule.time_zone if alert.spec and alert.spec.refresh_schedule else None,
                    "disable": alert.spec.refresh_schedule.disable if alert.spec and alert.spec.refresh_schedule else None,
                } if alert.spec and alert.spec.refresh_schedule else None,
                "notifiers": [
                    {
                        "connector": n.connector,
                        "properties": n.properties
                    } for n in alert.spec.notifiers
                ] if alert.spec and alert.spec.notifiers else None,
            } if alert.spec else None,
            "state": {
                "next_run_on": alert.state.next_run_on if alert.state else None,
                "execution_count": alert.state.execution_count if alert.state else None,
                "current_execution": {
                    "started_on": alert.state.current_execution.started_on if alert.state.current_execution else None,
                    "finished_on": alert.state.current_execution.finished_on if alert.state.current_execution else None,
                    "sent": alert.state.current_execution.sent if alert.state.current_execution else None,
                } if alert.state and alert.state.current_execution else None,
            } if alert.state else None
        }

        if alert.spec:
            print(f"  Display Name: {alert.spec.display_name}")
            print(f"  Resolver: {alert.spec.resolver}")
            if alert.spec.refresh_schedule:
                print(f"  Schedule: {alert.spec.refresh_schedule.cron}")
        if alert.state:
            print(f"  Next Run: {alert.state.next_run_on}")
            print(f"  Execution Count: {alert.state.execution_count}")

        save_debug_output("test_get_alert", {
            "test": "get_alert",
            "alert_name": alert_name,
            "alert": alert_data
        })

        # Verify alert has expected structure
        if alert.spec:
            assert hasattr(alert.spec, "display_name")
        if alert.state:
            assert hasattr(alert.state, "next_run_on")

    def test_get_alert_nonexistent(self, client, debug_dir):
        """Test getting a non-existent alert raises error"""
        print("\n" + "="*80)
        print("TEST: Get Nonexistent Alert")
        print("="*80)

        nonexistent_name = "nonexistent-alert-12345-test"
        print(f"Attempting to get nonexistent alert: {nonexistent_name}")

        with pytest.raises(RillError) as exc_info:
            client.alerts.get(nonexistent_name)

        error_msg = str(exc_info.value)
        print(f"✅ Got expected error: {error_msg}")

        assert "not found" in error_msg.lower(), f"Expected 'not found' in error message, got: {error_msg}"

        save_debug_output("test_get_alert_nonexistent", {
            "test": "get_alert_nonexistent",
            "alert_name": nonexistent_name,
            "error": error_msg
        })
