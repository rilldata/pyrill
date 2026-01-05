"""
Sample data for tests - REST API format
"""

# Sample organization data (REST API format)
SAMPLE_ORGS = [
    {
        "id": "org-id-1",
        "name": "test-org-1",
        "displayName": "Test Organization 1",
        "description": "First test org",
        "createdOn": "2025-01-01T12:00:00Z",
        "updatedOn": "2025-01-01T12:00:00Z"
    },
    {
        "id": "org-id-2",
        "name": "test-org-2",
        "displayName": "Test Organization 2",
        "description": "Second test org",
        "createdOn": "2025-01-02T13:00:00Z",
        "updatedOn": "2025-01-02T13:00:00Z"
    }
]

# Sample project data (REST API format)
SAMPLE_PROJECTS = [
    {
        "id": "proj-id-1",
        "name": "test-project-1",
        "orgId": "org-id-1",
        "orgName": "test-org-1",
        "public": False,
        "gitRemote": "https://github.com/test/repo1",
        "description": "Test project 1",
        "createdOn": "2025-01-01T12:00:00Z",
        "updatedOn": "2025-01-01T12:00:00Z"
    },
    {
        "id": "proj-id-2",
        "name": "test-project-2",
        "orgId": "org-id-1",
        "orgName": "test-org-1",
        "public": True,
        "gitRemote": "",
        "description": "Test project 2",
        "createdOn": "2025-01-02T12:00:00Z",
        "updatedOn": "2025-01-02T12:00:00Z"
    },
    {
        "id": "proj-id-3",
        "name": "test-project-3",
        "orgId": "org-id-2",
        "orgName": "test-org-2",
        "public": False,
        "gitRemote": "https://github.com/test/repo3",
        "description": None,
        "createdOn": "2025-01-03T12:00:00Z",
        "updatedOn": "2025-01-03T12:00:00Z"
    }
]

# Sample token data (REST API format)
SAMPLE_TOKENS = [
    {
        "id": "token-id-1",
        "displayName": "Test Token 1",
        "prefix": "rill_usr_abc123",
        "authClientDisplayName": "Created manually",
        "createdOn": "2025-01-01T10:00:00Z",
        "expiresOn": None,
        "usedOn": "2025-01-15T14:30:00Z"
    },
    {
        "id": "token-id-2",
        "displayName": "Test Token 2",
        "prefix": "rill_usr_xyz789",
        "authClientDisplayName": "Created via API",
        "createdOn": "2025-01-10T09:00:00Z",
        "expiresOn": "2025-12-31T23:59:59Z",
        "usedOn": None
    }
]

# Sample whoami data (REST API format)
SAMPLE_WHOAMI = {
    "id": "user-id-1",
    "email": "test@example.com",
    "displayName": "Test User",
    "photoUrl": "https://example.com/photo.jpg",
    "createdOn": "2024-01-01T00:00:00Z",
    "updatedOn": "2025-01-15T10:00:00Z"
}

# Sample project with deployment data (for project_status)
SAMPLE_PROJECT_WITH_DEPLOYMENT = {
    "project": {
        "id": "proj-id-1",
        "name": "test-project-1",
        "orgId": "org-id-1",
        "orgName": "test-org-1",
        "public": False,
        "description": "Test project 1",
        "frontendUrl": "https://test-org-1.rilldata.com/test-project-1",
        "createdOn": "2025-01-01T12:00:00Z",
        "updatedOn": "2025-01-01T12:00:00Z"
    },
    "prodDeployment": {
        "id": "deploy-id-1",
        "projectId": "proj-id-1",
        "status": "DEPLOYMENT_STATUS_OK",
        "statusMessage": "Running successfully",
        "runtimeHost": "runtime.rilldata.com",
        "runtimeInstanceId": "instance-123",
        "branch": "main",
        "createdOn": "2025-01-01T12:00:00Z",
        "updatedOn": "2025-01-15T10:00:00Z"
    }
}

# Sample runtime resources data (based on actual Rill API structure)
SAMPLE_RUNTIME_RESOURCES = {
    "resources": [
        {
            "meta": {
                "name": {
                    "kind": "rill.runtime.v1.Source",
                    "name": "source_data"
                }
            },
            "source": {"spec": {"path": "/data/source.parquet"}}
        },
        {
            "meta": {
                "name": {
                    "kind": "rill.runtime.v1.Model",
                    "name": "model_results"
                }
            },
            "model": {"spec": {"path": "/models/results.sql"}}
        },
        {
            "meta": {
                "name": {
                    "kind": "rill.runtime.v1.Dashboard",
                    "name": "dashboard_main"
                }
            },
            "dashboard": {"spec": {"path": "/dashboards/main.yaml"}}
        }
    ]
}

# Sample API error responses
SAMPLE_API_ERROR_404 = {
    "status_code": 404,
    "body": '{"error": "Resource not found"}'
}

SAMPLE_API_ERROR_401 = {
    "status_code": 401,
    "body": '{"error": "Unauthorized"}'
}

SAMPLE_API_ERROR_500 = {
    "status_code": 500,
    "body": '{"error": "Internal server error"}'
}

# Sample query result data for metrics queries
SAMPLE_METRICS_RESULT = [
    {
        "advertiser_name": "Hyundai",
        "device_type": "mobile",
        "overall_spend": 12500.50,
        "total_bids": 45000,
        "win_rate": 0.35,
        "impressions": 15750
    },
    {
        "advertiser_name": "Nike",
        "device_type": "desktop",
        "overall_spend": 8700.25,
        "total_bids": 32000,
        "win_rate": 0.42,
        "impressions": 13440
    },
    {
        "advertiser_name": "Samsung",
        "device_type": "mobile",
        "overall_spend": 15200.75,
        "total_bids": 52000,
        "win_rate": 0.38,
        "impressions": 19760
    }
]

# Sample SQL query result data
SAMPLE_SQL_RESULT = [
    {"advertiser_name": "Hyundai", "total": 12500.50},
    {"advertiser_name": "Nike", "total": 8700.25},
    {"advertiser_name": "Samsung", "total": 15200.75}
]

# Sample alert data (Runtime API format)
SAMPLE_ALERTS_RESOURCES = {
    "resources": [
        {
            "meta": {
                "name": {
                    "kind": "rill.runtime.v1.Alert",
                    "name": "revenue-drop-alert"
                }
            },
            "alert": {
                "spec": {
                    "displayName": "Revenue Drop Alert",
                    "refreshSchedule": {
                        "cron": "0 * * * *",
                        "timeZone": "America/New_York"
                    },
                    "resolver": "metrics_threshold",
                    "metricsViewName": "revenue_metrics",
                    "notifiers": [
                        {
                            "connector": "email",
                            "properties": {
                                "recipients": ["team@example.com"]
                            }
                        }
                    ]
                },
                "state": {
                    "nextRunOn": "2025-01-20T10:00:00Z",
                    "executionCount": 15,
                    "executionHistory": [
                        {
                            "adhoc": False,
                            "sent": True,
                            "sentTime": "2025-01-19T09:02:00Z",
                            "startedOn": "2025-01-19T09:00:00Z",
                            "finishedOn": "2025-01-19T09:02:30Z"
                        }
                    ]
                }
            }
        },
        {
            "meta": {
                "name": {
                    "kind": "rill.runtime.v1.Alert",
                    "name": "high-spend-alert"
                }
            },
            "alert": {
                "spec": {
                    "displayName": "High Spend Alert",
                    "refreshSchedule": {
                        "cron": "0 0 * * *",
                        "timeZone": "UTC"
                    },
                    "resolver": "metrics_threshold",
                    "metricsViewName": "spend_metrics"
                },
                "state": {
                    "nextRunOn": "2025-01-21T00:00:00Z",
                    "executionCount": 30
                }
            }
        }
    ]
}

# Sample individual alert (for get operations)
SAMPLE_ALERT = {
    "name": "revenue-drop-alert",
    "spec": {
        "displayName": "Revenue Drop Alert",
        "refreshSchedule": {
            "cron": "0 * * * *",
            "timeZone": "America/New_York"
        },
        "resolver": "metrics_threshold",
        "metricsViewName": "revenue_metrics",
        "notifiers": [
            {
                "connector": "email",
                "properties": {
                    "recipients": ["team@example.com"]
                }
            }
        ]
    },
    "state": {
        "nextRunOn": "2025-01-20T10:00:00Z",
        "executionCount": 15
    }
}

# Sample create alert response
SAMPLE_CREATE_ALERT_RESPONSE = {
    "name": "new-alert"
}

# Sample edit alert response
SAMPLE_EDIT_ALERT_RESPONSE = {}

# Sample delete alert response
SAMPLE_DELETE_ALERT_RESPONSE = {}

# Sample unsubscribe alert response
SAMPLE_UNSUBSCRIBE_ALERT_RESPONSE = {}

# Sample alert YAML responses
SAMPLE_ALERT_YAML = """
type: alert
displayName: Revenue Drop Alert
refreshSchedule:
  cron: "0 * * * *"
  timeZone: America/New_York
resolver: metrics_threshold
metricsViewName: revenue_metrics
notifiers:
  - connector: email
    properties:
      recipients:
        - team@example.com
"""

SAMPLE_GET_ALERT_YAML_RESPONSE = {
    "yaml": SAMPLE_ALERT_YAML.strip()
}

SAMPLE_GENERATE_ALERT_YAML_RESPONSE = {
    "yaml": SAMPLE_ALERT_YAML.strip()
}

# Sample annotations query result
SAMPLE_ANNOTATIONS_RESULT = {
    "rows": [
        {
            "time": "2025-01-15T09:00:00Z",
            "description": "Product launch - New model released",
            "forMeasures": ["revenue", "orders"],
            "additionalFields": {
                "category": "product",
                "severity": "high"
            }
        },
        {
            "time": "2025-01-18T14:30:00Z",
            "timeEnd": "2025-01-18T16:30:00Z",
            "description": "System maintenance window",
            "duration": "PT2H",
            "forMeasures": ["revenue"]
        },
        {
            "time": "2025-01-19T12:00:00Z",
            "description": "Marketing campaign started",
            "forMeasures": ["impressions", "clicks", "conversions"]
        }
    ]
}
