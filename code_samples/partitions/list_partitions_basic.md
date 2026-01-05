---
title: List Model Partitions - Basic
tags:
  - partitions
  - models
---

## USER PROMPT

List partitions for a partitioned model to inspect execution state and watermarks

## CODE SAMPLE

```python
from pyrill import RillClient

# Initialize client with defaults
client = RillClient(org="my-org", project="my-project")

# List partitions for a model (uses client defaults)
partitions = client.partitions.list("sales_model")
```

## TEST OUTPUT

```python
# Display partition information
for partition in partitions:
    status = "✓" if partition.error is None else "✗"
    print(f"{status} {partition.key}")
    if partition.watermark:
        print(f"  Watermark: {partition.watermark}")
    if partition.executed_on:
        print(f"  Executed: {partition.executed_on}")
    if partition.error:
        print(f"  Error: {partition.error}")
    if partition.elapsed_ms:
        print(f"  Duration: {partition.elapsed_ms}ms")
```

## EXPLANATORY DETAILS

The `partitions.list()` method retrieves partition information for partitioned models, including:

**Required:**
- `model` - Model name (can be positional or named parameter)

**Optional:**
- `project` - Override default project
- `org` - Override default organization
- `pending` - Filter for pending partitions only
- `errored` - Filter for errored partitions only
- `limit` - Maximum partitions to return (up to 400, with automatic pagination)
- `page_size` - Results per API request (default: 50)

**Partition Fields:**
- `key` - Partition identifier (always present)
- `watermark` - Partition watermark timestamp
- `executed_on` - When partition was last executed
- `error` - Error message if partition failed
- `elapsed_ms` - Execution duration in milliseconds
- `data` - Additional partition metadata

The method uses client defaults for org and project, making the most common case ultra-concise. No caching is used to ensure partition state is always current.
