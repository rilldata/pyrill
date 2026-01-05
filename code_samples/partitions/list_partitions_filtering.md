---
title: List Model Partitions - Filtering
tags:
  - partitions
  - models
  - filtering
---

## USER PROMPT

Filter partitions to find pending or errored partitions for troubleshooting

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get only errored partitions for debugging
errored_partitions = client.partitions.list(
    "sales_model",
    errored=True
)

# Get pending partitions waiting to execute
pending_partitions = client.partitions.list(
    "sales_model",
    pending=True
)

# Override project to check a different environment
staging_errors = client.partitions.list(
    "sales_model",
    project="staging",
    errored=True
)
```

## TEST OUTPUT

```python
print(f"Found {len(errored_partitions)} errored partitions:")
for partition in errored_partitions:
    print(f"\n❌ Partition: {partition.key}")
    print(f"   Error: {partition.error}")
    if partition.executed_on:
        print(f"   Failed at: {partition.executed_on}")

print(f"\n⏳ {len(pending_partitions)} partitions pending execution")

print(f"\n🔧 Staging has {len(staging_errors)} errored partitions")
```

## EXPLANATORY DETAILS

**Filter Parameters:**

- `errored=True` - Returns only partitions with errors
  - All returned partitions will have `partition.error` populated
  - Useful for identifying failed partition executions

- `pending=True` - Returns only partitions waiting to execute
  - Mutually exclusive with `errored`
  - Shows partitions queued for processing

**Context Overrides:**

The new ergonomic pattern allows overriding defaults:
- `project="staging"` - Check different project (common when comparing environments)
- `org="other-org"` - Check different organization (rare)
- Both can be overridden together if needed

Filters are applied server-side, so only matching partitions are returned - no need for client-side filtering.
