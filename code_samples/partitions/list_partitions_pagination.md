---
title: List Model Partitions - Pagination
tags:
  - partitions
  - models
  - pagination
---

## USER PROMPT

Retrieve large numbers of partitions using automatic pagination

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get up to 400 partitions with automatic pagination
# The SDK handles pagination transparently via nextPageToken
all_partitions = client.partitions.list(
    "large_model",
    limit=400
)

# Without limit, returns first page only (default 50)
first_page = client.partitions.list("large_model")

# Custom page size for API efficiency
# SDK makes multiple requests of 25 each until limit reached
partitions = client.partitions.list(
    "large_model",
    limit=100,
    page_size=25  # 4 API calls
)
```

## TEST OUTPUT

```python
print(f"Retrieved {len(all_partitions)} partitions")

# Analyze partition health
total = len(all_partitions)
errored = sum(1 for p in all_partitions if p.error)
success = total - errored

print(f"\nPartition Health:")
print(f"  ✓ Successful: {success} ({success/total*100:.1f}%)")
print(f"  ✗ Errored: {errored} ({errored/total*100:.1f}%)")

print(f"\nFirst page: {len(first_page)} partitions")

# Calculate average execution time
executed = [p for p in partitions if p.elapsed_ms]
if executed:
    avg_time = sum(p.elapsed_ms for p in executed) / len(executed)
    print(f"\nAverage execution time: {avg_time:.0f}ms")
```

## EXPLANATORY DETAILS

**Pagination Parameters:**

- `limit` - Maximum partitions to return (optional)
  - If not specified: Returns first page only (default 50)
  - If specified: SDK automatically paginates until limit reached
  - Maximum supported: 400 partitions
  - SDK handles `nextPageToken` internally

- `page_size` - Results per API request
  - Default: 50 (API maximum)
  - SDK caps at 50 even if higher value provided
  - Useful for controlling API call frequency

**Pagination Behavior:**

1. **No limit**: Single API call, returns first 50 (or page_size)
2. **With limit**: Multiple API calls until limit reached or no more data
3. **Transparent**: User sees flat list, SDK handles token management

**Performance Considerations:**

- Large limits (300-400) make 6-8 API requests
- No caching - every call fetches fresh data
- Pagination stops early if fewer partitions exist than limit
- Results are returned as a flat list for easy processing

The partition data is always fresh since models update frequently and caching would return stale execution states.
