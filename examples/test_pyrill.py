#!/usr/bin/env python3
"""
PyRill SDK Test Script

This script demonstrates basic PyRill SDK functionality:
- Authentication check (whoami)
- Listing organizations
- Listing projects in an organization
- Listing reports for a specific project
"""

from pyrill import RillClient, RillAuthError, RillAPIError


def main():
    """Run a series of PyRill SDK operations and print results."""

    try:
        # Initialize the client (uses RILL_USER_TOKEN from environment)
        print("Initializing PyRill client...")
        client = RillClient()
        print("✓ Client initialized successfully\n")

        # 1. Who am I?
        print("=" * 60)
        print("1. AUTHENTICATION CHECK (whoami)")
        print("=" * 60)
        user = client.auth.whoami()
        print(f"Logged in as: {user.email}")
        print(f"Display name: {user.display_name}")
        print(f"User ID: {user.id}")
        print()

        # 2. List all organizations
        print("=" * 60)
        print("2. LIST ORGANIZATIONS")
        print("=" * 60)
        orgs = client.organizations.list()
        print(f"Found {len(orgs)} organization(s):\n")
        for org in orgs:
            print(f"  • {org.name}")
            if org.description:
                print(f"    Description: {org.description}")
            print(f"    Plan: {org.billing_plan_name}")
            print()

        # 3. List projects in the 'demo' organization
        print("=" * 60)
        print("3. LIST PROJECTS IN 'demo' ORGANIZATION")
        print("=" * 60)
        try:
            projects = client.projects.list(org_name="demo")
            print(f"Found {len(projects)} project(s) in 'demo' org:\n")
            for project in projects:
                print(f"  • {project.name}")
                if project.description:
                    print(f"    Description: {project.description}")
                print(f"    Public: {project.public}")
                print(f"    URL: {project.frontend_url}")
                print()
        except RillAPIError as e:
            print(f"Error listing projects in 'demo' org: {e}")
            print("(You may not have access to the 'demo' organization)")
            print()

        # 4. List reports for the 'rill-openrtb-prog-ads' project
        print("=" * 60)
        print("4. LIST REPORTS FOR 'demo/rill-openrtb-prog-ads' PROJECT")
        print("=" * 60)
        try:
            reports = client.reports.list(
                org_name="demo",
                project_name="rill-openrtb-prog-ads"
            )
            print(f"Found {len(reports)} report(s):\n")
            for report in reports:
                print(f"  • {report.name}")
                if report.spec and report.spec.display_name:
                    print(f"    Display Name: {report.spec.display_name}")
                if report.spec and report.spec.refresh_schedule:
                    schedule = report.spec.refresh_schedule
                    if schedule.cron:
                        print(f"    Schedule: {schedule.cron}")
                if report.state and report.state.next_run_on:
                    print(f"    Next Run: {report.state.next_run_on}")
                print()
        except RillAPIError as e:
            print(f"Error listing reports: {e}")
            print("(You may not have access to this project)")
            print()

        print("=" * 60)
        print("✓ Quickstart test completed successfully!")
        print("=" * 60)

    except RillAuthError as e:
        print(f"\n❌ Authentication Error: {e}")
        print("\nMake sure you have:")
        print("1. Set the RILL_USER_TOKEN environment variable")
        print("2. Used a valid token from https://ui.rilldata.com/settings/tokens")
        return 1

    except RillAPIError as e:
        print(f"\n❌ API Error: {e}")
        print(f"Status code: {e.status_code}")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())