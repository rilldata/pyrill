# PyRill SDK Test Suite

![Python](https://img.shields.io/badge/python-3.13-blue)
![Coverage](../coverage.svg)

Comprehensive test suite for the PyRill SDK client library. This repository contains unit tests, integration tests, and end-to-end tests for validating the PyRill SDK functionality.

## Table of Contents

- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Coverage Reports](#coverage-reports)
- [Development Workflow](#development-workflow)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd pyrill
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run tests**:
   ```bash
   uv run pytest
   ```

---

## Running Tests

### All Tests

Run all mocked tests (unit + integration):

```bash
uv run pytest
```

Run the complete test suite (unit + integration + e2e):

```bash
uv run pytest --run-e2e -v
```

### Unit Tests Only

Fast tests with mocked dependencies (no API calls):

```bash
uv run pytest tests/client/unit/ -v
```

### Integration Tests Only

Integration tests with realistic mocks:

```bash
uv run pytest tests/client/integration/ -v
```

### End-to-End Tests

E2E tests require a real Rill API token and make actual API calls:

```bash
# Set your Rill API token
export RILL_USER_TOKEN="rill_usr_..."

# Run E2E tests
uv run pytest tests/client/e2e/ --run-e2e -v
```

**Note**: E2E tests are skipped by default. Use `--run-e2e` flag to run them.

### Browser Validation Tests

Browser tests validate UrlBuilder-generated URLs by loading them in a real browser using Playwright:

```bash
# First-time setup: Install browser binaries
uv run playwright install chromium

# Basic validation (headless, no screenshots)
uv run pytest tests/client/browser/ -v

# With screenshots
uv run pytest tests/client/browser/ --capture-screenshots -v

# Headed mode for debugging
uv run pytest tests/client/browser/ --headed -v

# Test specific URLs
uv run pytest tests/client/browser/ -k "complex_filter" -v
```

**Features**:
- Automatically discovers and tests all URL fixtures
- Validates URLs load without 404 errors
- Captures screenshots on failures (always) and success (optional)
- Detects invalid explore names and malformed parameters

See [Browser Tests README](client/browser/README.md) for detailed documentation.

### Specific Tests

```bash
# Run specific test file
uv run pytest tests/client/unit/test_models.py -v

# Run specific test class
uv run pytest tests/client/unit/test_models.py::TestOrganizationModel -v

# Run specific test function
uv run pytest tests/client/unit/test_models.py::TestOrganizationModel::test_organization_valid -v
```

### With Coverage

```bash
# Generate coverage report
uv run pytest --run-e2e --cov=pyrill --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Test Organization

```
pyrill/
├── src/pyrill/               # SDK source code
├── tests/
│   ├── client/               # Client SDK tests
│   │   ├── unit/            # Unit tests (mocked dependencies)
│   │   │   ├── test_client_unit.py
│   │   │   ├── test_models.py
│   │   │   ├── test_exceptions.py
│   │   │   └── test_query_unit.py
│   │   ├── integration/     # Integration tests (realistic mocks)
│   │   │   └── test_client_integration.py
│   │   ├── e2e/             # End-to-end tests (real API)
│   │   │   ├── test_client_e2e.py
│   │   │   ├── test_query_e2e.py
│   │   │   ├── test_query_dict_e2e.py
│   │   │   └── test_url_builder_e2e.py
│   │   ├── browser/         # Browser validation tests (Playwright)
│   │   │   ├── test_url_validation.py
│   │   │   ├── conftest.py
│   │   │   └── README.md
│   │   └── conftest.py      # Client-specific fixtures
│   ├── fixtures/            # Shared test data
│   │   ├── sample_data.py   # Mock API responses
│   │   ├── query_results/   # Saved query result fixtures
│   │   └── screenshots/     # Browser test screenshots (gitignored)
│   └── conftest.py          # Global pytest configuration
├── pyproject.toml           # Project configuration
└── README.md                # Main README
```

---

## Test Categories

### Unit Tests (`tests/client/unit/`)

Unit tests verify individual components in complete isolation using mocked dependencies. These tests are fast, deterministic, and require no external services. They mock all HTTP requests, subprocess calls, and file I/O to test the internal logic of classes and functions. Unit tests validate edge cases, error handling, model validation, and business logic without touching any real APIs or the file system. Examples include testing `RillClient` initialization, Pydantic model validation, exception handling, and caching behavior.

**Coverage Goal**: 90%+ (Current: **92%** ✅)

### Integration Tests (`tests/client/integration/`)

Integration tests verify how multiple components work together using realistic mock responses that mirror actual API behavior. While dependencies are still mocked, the mocks return authentic response structures from the Rill API, allowing tests to verify request construction, response parsing, error handling, and the interaction between the client and its resources (auth, organizations, projects, query). These tests ensure the SDK correctly handles real-world API response formats and validates the integration between different parts of the SDK without requiring live credentials.

**Coverage Goal**: All public methods

### End-to-End Tests (`tests/client/e2e/`)

End-to-end tests make actual calls to the live Rill API using real credentials (via `RILL_USER_TOKEN`). These tests validate critical user workflows against production infrastructure, verifying that the SDK works correctly with the real API including authentication, data retrieval, query execution, and error scenarios. E2E tests are slower and require active credentials, so they must be explicitly enabled with `--run-e2e`. They serve as a final validation that the SDK integrates properly with Rill's production services.

**Coverage Goal**: Critical paths only

### Browser Validation Tests (`tests/client/browser/`)

Browser validation tests use Playwright to load UrlBuilder-generated URLs in a real Chromium browser and validate they work correctly. These tests automatically discover all URL fixture files, load each URL in an incognito browser context, check for 404 errors, and optionally capture screenshots for visual verification. Browser tests are particularly useful for catching invalid explore names, malformed query parameters, or URLs that don't match the expected Rill UI structure. They provide confidence that generated URLs will work for end users. Requires Playwright browser installation: `uv run playwright install chromium`.

**Coverage Goal**: All generated URLs

### Test Markers

Tests use the following pytest markers:
- `@pytest.mark.unit` - Unit tests (fast, fully mocked)
- `@pytest.mark.integration` - Integration tests (realistic mocks)
- `@pytest.mark.e2e` - End-to-end tests (requires real credentials)
- `@pytest.mark.browser` - Browser validation tests (requires Playwright)

---

## Writing Tests

### Using Fixtures

The test suite provides reusable fixtures in `conftest.py`:

```python
def test_list_organizations(rill_client_with_mocks):
    """rill_client_with_mocks is a pre-configured client with mocked API"""
    orgs = rill_client_with_mocks.organizations.list()
    assert len(orgs) > 0
```

**Available Fixtures**:

Global fixtures (`tests/conftest.py`):
- `mock_api_token` - Fake API token
- `mock_env_with_token` - Environment with token set
- `mock_env_without_token` - Environment without token

Client-specific fixtures (`tests/client/conftest.py`):
- `rill_client_with_mocks` - Fully mocked client instance
- `mock_subprocess_run` - Mocked CLI commands
- `mock_httpx_client` - Mocked HTTP client
- `sample_orgs`, `sample_projects`, `sample_tokens` - Sample data
- `mock_org_name`, `mock_project_name` - Test names

### Test Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

Example:

```python
def test_list_projects_with_org_name():
    """Test that list_projects filters by org name"""
    # Test implementation
    pass
```

### Using Test Markers

Categorize tests with markers:

```python
@pytest.mark.unit
def test_something_unit():
    pass

@pytest.mark.integration
def test_something_integration():
    pass

@pytest.mark.e2e
def test_something_e2e():
    pass

@pytest.mark.browser
def test_url_validation_browser():
    pass
```

---

## Coverage Reports

### Generate Coverage Report

```bash
uv run pytest --run-e2e --cov=pyrill --cov-report=html
```

### View Coverage Report

Open in browser:

```bash
open htmlcov/index.html
```

The report shows:
- Line coverage for each file
- Missing lines highlighted
- Branch coverage
- Overall coverage percentage

### Coverage Configuration

Coverage settings in `pyproject.toml`:
- Source: `pyrill` package (in `src/pyrill`)
- Excludes: Test files, type stubs
- Reports: Terminal summary + HTML report

---

## Development Workflow

### Making Changes to PyRill SDK

Since the tests are in the same repository as the SDK, changes are immediately testable:

1. **Make changes in SDK**:
   ```bash
   # Edit src/pyrill/*.py files
   ```

2. **Run tests to validate**:
   ```bash
   uv run pytest
   ```

3. **No reinstall needed** - changes are immediately available!

### Adding New Tests

1. **Choose test category** (unit/integration/e2e)

2. **Create test file** in appropriate directory:
   ```bash
   # Example: Adding unit test
   touch tests/client/unit/test_new_feature.py
   ```

3. **Write tests** using existing patterns:
   ```python
   from pyrill import RillClient

   def test_new_feature(rill_client_with_mocks):
       result = rill_client_with_mocks.new_feature()
       assert result is not None
   ```

4. **Run your tests**:
   ```bash
   uv run pytest tests/client/unit/test_new_feature.py -v
   ```

### Debugging Tests

Run with verbose output:

```bash
uv run pytest -vv
```

Show print statements:

```bash
uv run pytest -s
```

Stop on first failure:

```bash
uv run pytest -x
```

Run last failed tests:

```bash
uv run pytest --lf
```

---

## Contributing

### Guidelines

1. **Write tests for new features** - All new SDK functionality should have tests
2. **Maintain coverage** - Aim for >90% coverage on new code
3. **Use descriptive names** - Test names should describe what they validate
4. **Keep tests fast** - Mock external dependencies in unit tests
5. **Document fixtures** - Add docstrings to new fixtures

### Pull Request Checklist

Before submitting a PR:

- [ ] All tests pass: `uv run pytest`
- [ ] Coverage maintained: `uv run pytest --cov=pyrill`
- [ ] New features have tests
- [ ] Tests are properly categorized (unit/integration/e2e)
- [ ] Docstrings added for new fixtures/helpers

---

## Troubleshooting

### Tests fail with import errors

Make sure dependencies are installed:
```bash
uv sync
```

### E2E tests fail with authentication errors

Ensure `RILL_USER_TOKEN` is set:
```bash
export RILL_USER_TOKEN="rill_usr_..."
uv run pytest tests/client/e2e/ --run-e2e
```

### Coverage report not generated

Run pytest with coverage flags:
```bash
uv run pytest --cov=pyrill --cov-report=html
```

### Browser tests fail with "Browser not installed"

Install Chromium browser for Playwright:
```bash
uv run playwright install chromium
```

### Browser tests timing out

Increase the timeout:
```bash
uv run pytest tests/client/browser/ --browser-timeout=60000 -v
```

### Want to see browser tests running visually

Use headed mode:
```bash
uv run pytest tests/client/browser/ --headed -v
```

---

## CI/CD Integration

The test suite runs automatically on GitHub Actions for every push and pull request.

### GitHub Actions Workflow

See `.github/workflows/test.yml` for the complete CI/CD configuration.

**Workflow includes**:
- Running full test suite with coverage
- E2E tests with real API calls
- Coverage badge generation
- Test summary updates

### Required Secrets

Configure these in GitHub repository settings:

1. **RILL_USER_TOKEN** - Rill API token for E2E tests
   - Go to: Settings → Secrets and variables → Actions
   - Click: New repository secret
   - Name: `RILL_USER_TOKEN`
   - Value: Your Rill API token (e.g., `rill_usr_...`)

2. **Enable workflow write permissions**:
   - Go to: Settings → Actions → General
   - Scroll to: Workflow permissions
   - Select: Read and write permissions
   - Click: Save
