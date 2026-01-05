---
title: Unsubscribe from Report
tags:
  - reports
---

## USER PROMPT

Remove the current user from a report's recipient list

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Unsubscribe from the report
response = client.reports.unsubscribe("daily-metrics")
```

## TEST OUTPUT

```python
print("Successfully unsubscribed from report")
print("You will no longer receive this report")
```

## EXPLANATORY DETAILS

The `unsubscribe()` method removes the currently authenticated user from a report's recipient list. This is useful for:
- Allowing users to self-manage their report subscriptions
- Reducing inbox clutter from reports users no longer need
- Implementing user preference management
- Building self-service report subscription interfaces

The method returns an `UnsubscribeReportResponse` to confirm the action.

Key behaviors:
- Only removes the **current user** (identified by the API token)
- Does not affect other recipients
- Does not modify the report's schedule or configuration
- The report continues to run and deliver to other recipients

This is particularly useful when:
- A team member changes roles and no longer needs certain reports
- Users want to temporarily pause report delivery without deleting the report
- Building a report subscription management UI
- Implementing "unsubscribe" links in report emails

Note: To add a user back to the recipient list, use the `edit()` method to update the `email_recipients` field in the report's configuration. There is no separate "subscribe" method - subscription is managed through the report's recipient list configuration.
