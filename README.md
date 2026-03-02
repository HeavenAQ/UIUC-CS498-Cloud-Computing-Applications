# Cloud Computing Applications

This repository collects multiple AWS-focused mini-projects for cloud computing coursework. Each subdirectory is a mostly self-contained assignment with its own code, setup notes, and supporting artifacts.

## Repository Layout

### `MP1-V2/`

An EC2 and S3 exercise centered on CSV processing.

- `main.py` reads `orders.csv`, filters order data with `pandas`, and writes `results.csv`.
- AWS setup artifacts such as `iam-assume-role-policy.json`, `bucket-policy.json`, and `submit.py` support the assignment workflow.
- `README.md` documents the EC2 instance, IAM role, S3 bucket, and submission steps.

### `MP1_WordCount_Template/`

A small starter template from an earlier word count exercise.

- `MP1.py` is the starter script.
- `input.txt` is sample input data.

### `MP2/`

A load balancing and auto-scaling assignment built around FastAPI services on EC2.

- `1-serve.py` and `1-receive.py` implement a simple data access service and a forwarding service.
- `2-serve.py` exposes a CPU stress endpoint used for scaling experiments.
- `setup.sh`, `launch_template.sh`, `trust-policy.json`, and `submit.py` support EC2 provisioning and deployment.
- `README.md` walks through the AWS infrastructure steps for load balancers, networking, and scaling.

### `MP3/`

A serverless assignment using Lambda, API Gateway, Lex, and DynamoDB.

- `lambda_function.py` parses a graph string, computes shortest-path distances with BFS, and stores results in DynamoDB.
- `test_lambda_function.py` and `conftest.py` provide local test coverage for the Lambda logic.
- `bfs_lambda/`, `lex_lambda/`, and zip artifacts are packaged Lambda deployment outputs.
- `README.md` documents the end-to-end setup for Lambda, API Gateway, and Lex.

## Common Tooling

The Python-based subprojects use `pyproject.toml` and target Python 3.12+.

- `MP1-V2` depends on `pandas`
- `MP2` depends on `fastapi`, `httpx`, and `requests`
- `MP3` depends on `boto3`, DynamoDB type stubs, and `pytest`


## Working In This Repo

Because each assignment is self-contained, the usual workflow is:

1. Change into the relevant project directory.
2. Create or activate that project's virtual environment.
3. Install dependencies from `pyproject.toml` or `requirements.txt`.
4. Follow the project-specific `README.md` for AWS setup and execution steps.

> [!NOTE]
>
> - The subproject READMEs contain the detailed operational steps; this root README is intended as a map of the repository.
