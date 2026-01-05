---
title: Trigger Report Execution
tags:
  - reports
---

## USER PROMPT

Manually trigger a report to run immediately

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Trigger an ad-hoc execution
response = client.reports.trigger("weekly-summary")
```

## TEST OUTPUT

```python
print("Report triggered successfully")
print("The report will execute outside its normal schedule")
```

## EXPLANATORY DETAILS

The `trigger()` method initiates an immediate, ad-hoc execution of a report outside its normal schedule. This is useful when you need to:
- Send a report immediately without waiting for the scheduled time
- Test a newly created or modified report
- Provide on-demand reports to stakeholders
- Respond to urgent data requests

The method returns a `TriggerReportResponse` to confirm the execution was queued.

Important notes:
- The report executes asynchronously - the method returns immediately
- The ad-hoc execution does not affect the regular schedule
- Recipients will receive the report according to the configured delivery channels
- The execution count in the report state will increment

Common use cases:
- **Testing**: "I just created a report, let me verify it works"
- **On-demand**: "Can you send me the latest sales report right now?"
- **Debugging**: "The report failed yesterday, let me re-run it"
- **Demos**: "I need to show this report to executives in 10 minutes"

The report will use the current configuration including:
- The latest query results
- Configured export format
- Current recipient list
- Timezone settings for timestamp formatting
