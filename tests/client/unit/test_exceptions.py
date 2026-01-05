"""
Unit tests for custom exceptions
"""

import pytest

from pyrill.exceptions import RillError, RillAuthError, RillAPIError, RillCLIError


@pytest.mark.unit
class TestRillError:
    """Tests for base RillError exception"""

    def test_rill_error_creation(self):
        """Test creating RillError"""
        error = RillError("Test error message")
        assert str(error) == "Test error message"

    def test_rill_error_inheritance(self):
        """Test that RillError inherits from Exception"""
        error = RillError("Test error")
        assert isinstance(error, Exception)

    def test_rill_error_raise(self):
        """Test raising RillError"""
        with pytest.raises(RillError) as exc_info:
            raise RillError("Test error")
        assert str(exc_info.value) == "Test error"


@pytest.mark.unit
class TestRillAuthError:
    """Tests for RillAuthError exception"""

    def test_auth_error_creation(self):
        """Test creating RillAuthError"""
        error = RillAuthError("Authentication failed")
        assert str(error) == "Authentication failed"

    def test_auth_error_inheritance(self):
        """Test that RillAuthError inherits from RillError"""
        error = RillAuthError("Auth error")
        assert isinstance(error, RillError)
        assert isinstance(error, Exception)

    def test_auth_error_catch_as_rill_error(self):
        """Test catching RillAuthError as RillError"""
        with pytest.raises(RillError):
            raise RillAuthError("Auth failed")


@pytest.mark.unit
class TestRillAPIError:
    """Tests for RillAPIError exception"""

    def test_api_error_basic(self):
        """Test creating RillAPIError with just message"""
        error = RillAPIError("API request failed")
        assert str(error) == "API request failed"
        assert error.status_code is None
        assert error.response_body is None

    def test_api_error_with_status_code(self):
        """Test creating RillAPIError with status code"""
        error = RillAPIError("API error", status_code=404)
        assert str(error) == "API error"
        assert error.status_code == 404

    def test_api_error_with_response_body(self):
        """Test creating RillAPIError with response body"""
        error = RillAPIError(
            "API error",
            status_code=500,
            response_body='{"error": "Internal server error"}'
        )
        assert error.status_code == 500
        assert error.response_body == '{"error": "Internal server error"}'

    def test_api_error_inheritance(self):
        """Test that RillAPIError inherits from RillError"""
        error = RillAPIError("API error")
        assert isinstance(error, RillError)

    def test_api_error_attributes_accessible(self):
        """Test accessing custom attributes"""
        error = RillAPIError("Not found", status_code=404, response_body="Not found")
        assert hasattr(error, "status_code")
        assert hasattr(error, "response_body")
        assert error.status_code == 404
        assert error.response_body == "Not found"


@pytest.mark.unit
class TestRillCLIError:
    """Tests for RillCLIError exception"""

    def test_cli_error_basic(self):
        """Test creating RillCLIError with just message"""
        error = RillCLIError("CLI command failed")
        assert str(error) == "CLI command failed"
        assert error.return_code is None
        assert error.stderr is None

    def test_cli_error_with_return_code(self):
        """Test creating RillCLIError with return code"""
        error = RillCLIError("Command failed", return_code=1)
        assert str(error) == "Command failed"
        assert error.return_code == 1

    def test_cli_error_with_stderr(self):
        """Test creating RillCLIError with stderr output"""
        error = RillCLIError(
            "Command failed",
            return_code=1,
            stderr="Error: invalid argument"
        )
        assert error.return_code == 1
        assert error.stderr == "Error: invalid argument"

    def test_cli_error_inheritance(self):
        """Test that RillCLIError inherits from RillError"""
        error = RillCLIError("CLI error")
        assert isinstance(error, RillError)

    def test_cli_error_attributes_accessible(self):
        """Test accessing custom attributes"""
        error = RillCLIError("Failed", return_code=2, stderr="error output")
        assert hasattr(error, "return_code")
        assert hasattr(error, "stderr")
        assert error.return_code == 2
        assert error.stderr == "error output"


@pytest.mark.unit
class TestExceptionCatching:
    """Tests for exception catching and handling"""

    def test_catch_all_rill_errors(self):
        """Test catching all RillError types with base exception"""
        errors = [
            RillError("Generic error"),
            RillAuthError("Auth error"),
            RillAPIError("API error"),
            RillCLIError("CLI error")
        ]

        for error in errors:
            with pytest.raises(RillError):
                raise error

    def test_specific_exception_catching(self):
        """Test catching specific exception types"""
        with pytest.raises(RillAuthError):
            raise RillAuthError("Auth failed")

        with pytest.raises(RillAPIError):
            raise RillAPIError("API failed")

        with pytest.raises(RillCLIError):
            raise RillCLIError("CLI failed")
