# PyRill SDK Code Examples

This directory contains comprehensive code examples for the PyRill SDK.

## Format

### YAML Front Matter
```yaml
---
title: Example Title
tags:
  - resource_type
---
```

### Sections

1. **USER PROMPT** - A concise user request or question
2. **CODE SAMPLE** - The essential, concise code example showing the core functionality
3. **TEST OUTPUT** (optional) - Debug, validation, or demonstration code that shows how to test or verify the code sample, including print statements and output examples
4. **EXPLANATORY DETAILS** - Additional context explaining the code, when to use it, and important considerations

The key distinction:
- **CODE SAMPLE** contains the actual code you'd use in production
- **TEST OUTPUT** contains code you'd use to validate, debug, or demonstrate the code sample (not typically in production code)


## Tags

Examples are tagged by resource type:
- `client` - Client initialization and configuration
- `auth` - Authentication operations
- `orgs` - Organization management
- `projects` - Project management
- `queries` - Data querying (metrics, SQL)
- `urls` - URL generation for Rill UI
