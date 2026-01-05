"""
Unit tests for IFrame models and resource

These tests use mocks and do not require API credentials.
"""

import pytest
from pydantic import ValidationError

from pyrill.models import IFrameOptions, IFrameResponse


class TestIFrameOptionsModel:
    """Unit tests for IFrameOptions model validation"""

    def test_iframe_options_minimal(self):
        """Test IFrameOptions with minimal required fields"""
        options = IFrameOptions(
            user_email="test@example.com"
        )

        assert options.user_email == "test@example.com"
        assert options.resource is None
        assert options.type is None
        assert options.theme_mode is None

    def test_iframe_options_all_fields(self):
        """Test IFrameOptions with all fields populated"""
        options = IFrameOptions(
            branch="dev",
            ttl_seconds=7200,
            user_id="user_123",
            user_email="test@example.com",
            attributes={"role": "admin", "tenant": "acme"},
            type="explore",
            resource="auction_metrics",
            theme="custom_theme",
            theme_mode="dark",
            navigation=True,
            state="some_state_blob"
        )

        assert options.branch == "dev"
        assert options.ttl_seconds == 7200
        assert options.user_id == "user_123"
        assert options.user_email == "test@example.com"
        assert options.attributes == {"role": "admin", "tenant": "acme"}
        assert options.type == "explore"
        assert options.resource == "auction_metrics"
        assert options.theme == "custom_theme"
        assert options.theme_mode == "dark"
        assert options.navigation is True
        assert options.state == "some_state_blob"

    def test_iframe_options_type_literal_explore(self):
        """Test that type='explore' is accepted"""
        options = IFrameOptions(type="explore", user_email="test@example.com")
        assert options.type == "explore"

    def test_iframe_options_type_literal_canvas(self):
        """Test that type='canvas' is accepted"""
        options = IFrameOptions(type="canvas", user_email="test@example.com")
        assert options.type == "canvas"

    def test_iframe_options_type_literal_invalid(self):
        """Test that invalid type value raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            IFrameOptions(type="dashboard", user_email="test@example.com")

        error_msg = str(exc_info.value).lower()
        assert "literal" in error_msg or "input should be 'explore' or 'canvas'" in error_msg

    def test_iframe_options_theme_mode_literal_light(self):
        """Test that theme_mode='light' is accepted"""
        options = IFrameOptions(theme_mode="light", user_email="test@example.com")
        assert options.theme_mode == "light"

    def test_iframe_options_theme_mode_literal_dark(self):
        """Test that theme_mode='dark' is accepted"""
        options = IFrameOptions(theme_mode="dark", user_email="test@example.com")
        assert options.theme_mode == "dark"

    def test_iframe_options_theme_mode_literal_system(self):
        """Test that theme_mode='system' is accepted"""
        options = IFrameOptions(theme_mode="system", user_email="test@example.com")
        assert options.theme_mode == "system"

    def test_iframe_options_theme_mode_literal_invalid(self):
        """Test that invalid theme_mode value raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            IFrameOptions(theme_mode="auto", user_email="test@example.com")

        error_msg = str(exc_info.value).lower()
        assert "literal" in error_msg or "light" in error_msg or "dark" in error_msg or "system" in error_msg

    def test_iframe_options_model_dump_exclude_none(self):
        """Test that model_dump excludes None values"""
        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com"
        )

        data = options.model_dump(exclude_none=True)

        assert "resource" in data
        assert "user_email" in data or "userEmail" in data
        # None fields should not be present
        assert "branch" not in data
        assert "ttl_seconds" not in data
        assert "type" not in data

    def test_iframe_options_model_dump_with_aliases(self):
        """Test that model_dump uses camelCase aliases when by_alias=True"""
        options = IFrameOptions(
            ttl_seconds=3600,
            user_id="user_123",
            user_email="test@example.com",
            theme_mode="dark"
        )

        data = options.model_dump(by_alias=True, exclude_none=True)

        # Should use camelCase
        assert "ttlSeconds" in data
        assert "userId" in data
        assert "userEmail" in data
        assert "themeMode" in data

        # Should NOT use snake_case
        assert "ttl_seconds" not in data
        assert "user_id" not in data
        assert "user_email" not in data
        assert "theme_mode" not in data

    def test_iframe_options_accepts_snake_case_input(self):
        """Test that IFrameOptions accepts snake_case field names"""
        options = IFrameOptions(
            ttl_seconds=3600,
            user_email="test@example.com"
        )

        assert options.ttl_seconds == 3600
        assert options.user_email == "test@example.com"

    def test_iframe_options_accepts_camel_case_input(self):
        """Test that IFrameOptions accepts camelCase field names (populate_by_name)"""
        # This works because of model_config = {"populate_by_name": True}
        options = IFrameOptions(
            ttlSeconds=3600,
            userEmail="test@example.com"
        )

        assert options.ttl_seconds == 3600
        assert options.user_email == "test@example.com"

    def test_iframe_options_attributes_dict(self):
        """Test that attributes field accepts arbitrary dict"""
        options = IFrameOptions(
            attributes={
                "email": "test@example.com",
                "role": "viewer",
                "tenant_id": "tenant123",
                "custom_field": "custom_value",
                "nested": {"key": "value"}
            }
        )

        assert options.attributes["email"] == "test@example.com"
        assert options.attributes["role"] == "viewer"
        assert options.attributes["custom_field"] == "custom_value"
        assert options.attributes["nested"]["key"] == "value"


class TestIFrameResponseModel:
    """Unit tests for IFrameResponse model validation"""

    def test_iframe_response_all_fields(self):
        """Test IFrameResponse with all required fields"""
        response = IFrameResponse(
            iframe_src="https://ui.rilldata.com/-/embed?access_token=token123",
            runtime_host="https://runtime.rilldata.com",
            instance_id="inst_abc123",
            access_token="token123",
            ttl_seconds=86400
        )

        assert response.iframe_src == "https://ui.rilldata.com/-/embed?access_token=token123"
        assert response.runtime_host == "https://runtime.rilldata.com"
        assert response.instance_id == "inst_abc123"
        assert response.access_token == "token123"
        assert response.ttl_seconds == 86400

    def test_iframe_response_missing_required_field(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            IFrameResponse(
                iframe_src="https://ui.rilldata.com/-/embed",
                runtime_host="https://runtime.rilldata.com"
                # Missing instance_id, access_token, ttl_seconds
            )

    def test_iframe_response_accepts_camel_case(self):
        """Test IFrameResponse accepts camelCase field names from API"""
        api_response = {
            "iframeSrc": "https://ui.rilldata.com/-/embed?access_token=token123",
            "runtimeHost": "https://runtime.rilldata.com",
            "instanceId": "inst_abc123",
            "accessToken": "token123",
            "ttlSeconds": 86400
        }

        response = IFrameResponse(**api_response)

        assert response.iframe_src == "https://ui.rilldata.com/-/embed?access_token=token123"
        assert response.runtime_host == "https://runtime.rilldata.com"
        assert response.instance_id == "inst_abc123"
        assert response.access_token == "token123"
        assert response.ttl_seconds == 86400

    def test_iframe_response_accepts_snake_case(self):
        """Test IFrameResponse accepts snake_case field names"""
        response = IFrameResponse(
            iframe_src="https://ui.rilldata.com/-/embed?access_token=token123",
            runtime_host="https://runtime.rilldata.com",
            instance_id="inst_abc123",
            access_token="token123",
            ttl_seconds=86400
        )

        assert response.iframe_src == "https://ui.rilldata.com/-/embed?access_token=token123"
        assert response.runtime_host == "https://runtime.rilldata.com"

    def test_iframe_response_model_dump_uses_aliases(self):
        """Test that model_dump uses camelCase aliases when by_alias=True"""
        response = IFrameResponse(
            iframe_src="https://ui.rilldata.com/-/embed",
            runtime_host="https://runtime.rilldata.com",
            instance_id="inst_123",
            access_token="token123",
            ttl_seconds=86400
        )

        data = response.model_dump(by_alias=True)

        # Should use camelCase
        assert "iframeSrc" in data
        assert "runtimeHost" in data
        assert "instanceId" in data
        assert "accessToken" in data
        assert "ttlSeconds" in data

        # Should NOT use snake_case
        assert "iframe_src" not in data
        assert "runtime_host" not in data
        assert "instance_id" not in data
        assert "access_token" not in data
        assert "ttl_seconds" not in data

    def test_iframe_response_ttl_seconds_type(self):
        """Test that ttl_seconds must be an integer"""
        # Valid integer
        response = IFrameResponse(
            iframe_src="https://ui.rilldata.com/-/embed",
            runtime_host="https://runtime.rilldata.com",
            instance_id="inst_123",
            access_token="token123",
            ttl_seconds=3600
        )
        assert response.ttl_seconds == 3600

        # String that can be coerced to int should work (Pydantic coercion)
        response2 = IFrameResponse(
            iframe_src="https://ui.rilldata.com/-/embed",
            runtime_host="https://runtime.rilldata.com",
            instance_id="inst_123",
            access_token="token123",
            ttl_seconds="7200"  # String that can be converted
        )
        assert response2.ttl_seconds == 7200

        # Invalid string should raise ValidationError
        with pytest.raises(ValidationError):
            IFrameResponse(
                iframe_src="https://ui.rilldata.com/-/embed",
                runtime_host="https://runtime.rilldata.com",
                instance_id="inst_123",
                access_token="token123",
                ttl_seconds="invalid"
            )


class TestIFrameModelsIntegration:
    """Integration tests between IFrameOptions and IFrameResponse"""

    def test_options_serialization_for_api_request(self):
        """Test that IFrameOptions serializes properly for API request"""
        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com",
            ttl_seconds=3600,
            theme_mode="dark",
            navigation=True
        )

        # This is how it would be used in the actual API call
        json_data = options.model_dump(exclude_none=True, by_alias=True)

        # Verify it's a dict with proper field names
        assert isinstance(json_data, dict)
        assert json_data["resource"] == "auction_metrics"
        assert json_data["userEmail"] == "test@example.com"
        assert json_data["ttlSeconds"] == 3600
        assert json_data["themeMode"] == "dark"
        assert json_data["navigation"] is True

    def test_response_deserialization_from_api(self):
        """Test that IFrameResponse deserializes properly from API response"""
        # Simulate API response
        api_response = {
            "iframeSrc": "https://ui.rilldata.com/-/embed?access_token=xyz&instance_id=123",
            "runtimeHost": "https://runtime.rilldata.com",
            "instanceId": "inst_123",
            "accessToken": "xyz",
            "ttlSeconds": 86400
        }

        # This is how it would be used in the actual API response handling
        response = IFrameResponse(**api_response)

        # Verify proper deserialization
        assert response.iframe_src == api_response["iframeSrc"]
        assert response.runtime_host == api_response["runtimeHost"]
        assert response.instance_id == api_response["instanceId"]
        assert response.access_token == api_response["accessToken"]
        assert response.ttl_seconds == api_response["ttlSeconds"]

    def test_full_request_response_cycle(self):
        """Test simulated full request/response cycle"""
        # 1. Create request options
        options = IFrameOptions(
            resource="auction_metrics",
            user_email="user@example.com",
            theme_mode="dark"
        )

        # 2. Serialize for API request
        request_data = options.model_dump(exclude_none=True, by_alias=True)

        assert request_data == {
            "resource": "auction_metrics",
            "userEmail": "user@example.com",
            "themeMode": "dark"
        }

        # 3. Simulate API response
        api_response = {
            "iframeSrc": "https://ui.rilldata.com/-/embed?access_token=abc123",
            "runtimeHost": "https://runtime.rilldata.com",
            "instanceId": "inst_456",
            "accessToken": "abc123",
            "ttlSeconds": 86400
        }

        # 4. Deserialize response
        response = IFrameResponse(**api_response)

        assert response.iframe_src.startswith("https://")
        assert response.access_token == "abc123"
        assert response.ttl_seconds == 86400
