# uv run --with git+ssh://git@github.com/rilldata/pyrill.git quicktest.py

from pyrill import RillClient

client = RillClient(org='demo', project='rill-openrtb-prog-ads')

# Auth check
user = client.auth.whoami()
print(f"✓ Authenticated as: {user.email}")

# List orgs
orgs = client.orgs.list()
print(f"✓ Organizations: {len(orgs)}")

# List projects
try:
    projects = client.projects.list(org_name="demo")
    print(f"✓ Projects in demo: {len(projects)}")

    # Get project
    if projects:
        project = client.projects.get(org_name="demo", project_name="rill-openrtb-prog-ads")
        print(f"✓ Project details: {project.org_name}/{project.name}")

        # List explores in the project
        resources = client.projects.get_resources("rill-openrtb-prog-ads", org="demo")
        explores = [r for r in resources.resources if r.type and "Explore" in r.type]
        print(f"\n✓ Explores in project: {len(explores)}")
        for explore in explores:
            print(f"  - {explore.name}")

        # List public URLs without an expiry date
        public_urls = client.publicurls.list(org="demo", project="rill-openrtb-prog-ads")
        urls_without_expiry = [url for url in public_urls if url.expires_on is None]
        # Sort by label (display_name)
        urls_without_expiry.sort(key=lambda url: (url.display_name or "Unlabeled").lower())
        print(f"\n✓ Public URLs without expiry: {len(urls_without_expiry)}")
        for url in urls_without_expiry:
            label = url.display_name or "Unlabeled"
            created_by = url.created_by_user_email or "Unknown"
            print(f"  - {label} (created by: {created_by})")

except Exception as e:
    print(f"⚠ Could not access demo org (may not have permissions): {e}")
