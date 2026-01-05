"""
Tests for backward compatibility of model imports after refactoring.

Ensures that imports still work after moving models.py to models/ directory.
"""

import pytest


class TestModelsBackwardCompatibility:
    """Test that model imports work correctly after refactoring."""

    def test_import_from_pyrill_package(self):
        """Test that models can be imported from pyrill package."""
        from pyrill import (
            Org,
            Project,
            Token,
            User,
            Deployment,
            Resource,
            ProjectResources,
            ProjectStatus,
            MetricsQuery,
            RillUrl,
        )

        # Verify they're actually classes/types
        assert Org is not None
        assert Project is not None
        assert Token is not None
        assert User is not None
        assert Deployment is not None
        assert Resource is not None
        assert ProjectResources is not None
        assert ProjectStatus is not None
        assert MetricsQuery is not None
        assert RillUrl is not None

    def test_import_from_models_module(self):
        """Test that models can be imported from pyrill.models module."""
        from pyrill.models import (
            Org,
            Project,
            MetricsQuery,
            RillUrl,
        )

        # Verify they're actually classes/types
        assert Org is not None
        assert Project is not None
        assert MetricsQuery is not None
        assert RillUrl is not None

    def test_navigation_model_in_all(self):
        """Test that RillUrl is properly exported in __all__."""
        import pyrill.models

        # Check that RillUrl is in __all__
        assert 'RillUrl' in pyrill.models.__all__

        # Verify it can be accessed
        assert hasattr(pyrill.models, 'RillUrl')
        assert pyrill.models.RillUrl is not None
