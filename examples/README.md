# PyRill SDK Quickstart Guide

Get started with the PyRill SDK in 5 minutes! This guide will walk you through setting up a new Python project and making your first API calls to Rill Data.

## Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager installed
- SSH access to GitHub (or use HTTPS alternative below)
- A Rill account at [ui.rilldata.com](https://ui.rilldata.com)
- Rill User Token (starts with (`rill_usr_`) as RILL_USER_TOKEN environment variable


## Step 1: Create a New Python Project

Create a new directory for your project and initialize it with uv:

```bash
mkdir my-rill-project
cd my-rill-project
uv init
```

## Step 2: Install PyRill SDK

Install the PyRill SDK directly from GitHub using uv:

```bash
uv add git+ssh://git@github.com/rilldata/pyrill.git
```

## Step 3: Copy the test script

Copy `test_pyrill.py` from [the SDK repo](https://github.com/rilldata/pyrill/blob/main/examples/test_pyrill.py)


## Step 4: Run Your Script

Execute the script using uv with the required environment variables:

```bash
RILL_DEFAULT_ORG=demo RILL_DEFAULT_PROJECT=rill-openrtb-prog-ads uv run python test_py.py
```

**Note:** The `RILL_DEFAULT_ORG` and `RILL_DEFAULT_PROJECT` variables are required by the SDK. We're using "demo" as the default org since that's what the script explores as a demo.

## Step 5 (Optional): Try the SDK in a Jupter Notebook

Copy `using_the_pyrill_client.ipynb` from [the SDK repo](https://github.com/rilldata/pyrill/blob/main/examples/using_the_pyrill_client.ipynb)

Add the Jupyter library and run the notebook:

```bash
uv add jupyter
uv run jupyter notebook
```
