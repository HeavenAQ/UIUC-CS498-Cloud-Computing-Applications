# Cloud Computing Applications

This repository collects multiple AWS-focused mini-projects for cloud computing coursework. Each subdirectory is a mostly self-contained assignment with its own code, setup notes, and supporting artifacts.

## Repository Layout

### `MP1-V2/`

An EC2 and S3 exercise centered on CSV processing.

- `main.py` reads `orders.csv`, filters order data with `pandas`, and writes `results.csv`.
- AWS setup artifacts such as `iam-assume-role-policy.json`, `bucket-policy.json`, and `submit.py` support the assignment workflow.
- `README.md` documents the EC2 instance, IAM role, S3 bucket, and submission steps.

### `MP1_WordCount_Template/`

A word count solution that reads lines from stdin, filters stop words, and reports the top-20 most frequent words.

- `MP1.py` reads stdin, applies stop-word filtering and delimiter normalization, samples 10 000 random line indexes seeded by a caller-supplied user ID, counts word frequencies with `collections.Counter`, and prints the top-20 words sorted by frequency then alphabetically.
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

### `MP4/`

A full-stack deployment assignment using S3, Elastic Beanstalk, and CodeBuild.

- `bucket-policy.json` is a template S3 bucket policy granting public read access to the static frontend.
- `submit.py` records the frontend S3 URL, Elastic Beanstalk backend URL, and CI/CD log URLs for the autograder.
- `README.md` walks through creating the S3 bucket, configuring public access, wiring the CodeBuild pipeline, and deploying the backend to Elastic Beanstalk.

### `MP6/`

A real-time streaming pipeline built on AWS MSK (managed Kafka), Lambda, and EC2.

- `section1_producer.py` and `section1_consumer.py` implement a Lambda-driven load-test pair: the producer invokes a Flask-based consumer endpoint that simulates CPU/memory work.
- `section2_producer.py` and `section2_consumer.py` implement an MSK Kafka producer/consumer pair using IAM SASL authentication; the consumer integrates with HBase.
- `traffic_generator_lambda.py` is a Lambda function for stress-testing the pipeline.
- Supporting artifacts (`kafka_consumer_bootstrap.sh`, `ec2-service.json`, `msk-cluster-config.json`, `prometheus.yml`, etc.) handle MSK cluster setup and monitoring.
- `README.md` covers the end-to-end MSK, Lambda, and EC2 setup.

### `MP7/`

An Apache Spark MapReduce assignment that analyzes Wikipedia-style link and title data.

- `PythonTemplate/OrphanPagesSpark.py` – finds pages with no incoming links.
- `PythonTemplate/PopularityLeagueSpark.py` – ranks pages from a league list by incoming-link count.
- `PythonTemplate/TitleCountSpark.py` – counts word frequency across page titles (top 10, stop-words excluded).
- `PythonTemplate/TopPopularLinksSpark.py` – finds the 10 most-linked pages across the dataset.
- `PythonTemplate/TopTitleStatisticsSpark.py` – computes mean, sum, min, max, and variance of per-title word counts.
- Sample data lives in `PythonTemplate/dataset/links/` and `PythonTemplate/dataset/titles/`.
- `Docker/` provides a Dockerfile for running PySpark jobs locally.
- `README.md` covers EMR cluster setup and job submission.

### `MP8/`

A PySpark SQL and DataFrame assignment that analyzes Google Books ngram data.

- `python/MP8_PartA.py` – loads the dataset as both an RDD and a DataFrame.
- `python/MP8_PartB.py` – counts total records via RDD and SQL.
- `python/MP8_PartC.py` – filters records to count occurrences of a specific word.
- `python/MP8_PartD.py` – aggregates to find top words ranked by total yearly count.
- `python/MP8_PartE.py` – performs a self-join to find word pairs.
- `python/MP8_PartF.py` – uses window functions (lag/lead) to identify words with the greatest frequency increase.
- `python/gbooks` is the ngram dataset (word, year, frequency, book-count columns).
- `Docker/` provides a Dockerfile for the Spark environment.
- `README.md` covers EMR setup and submission steps.

### `MP9/`

A flight data deduplication assignment (data only; implementation not yet present).

- `flights-1-with-duplicates.csv` through `flights-5-with-duplicates.csv` are the input datasets containing duplicate flight records.

### `RAG/`

A RAG-based customer support ticket system built on Google Cloud Platform.

- **Knowledge base pipeline (batch):** `functions/upload_kb/` uploads Markdown documents to GCS; `functions/process_kb/` chunks them, generates embeddings with Vertex AI `text-embedding-004`, and stores vectors in BigQuery.
- **Ticket processing pipeline (streaming):** `functions/publish_ticket/` enqueues tickets to Pub/Sub; `dataflow/ticket_processor.py` is an Apache Beam streaming job that performs vector similarity search and calls Gemini `gemini-2.5-flash` to generate grounded solutions, writing results to BigQuery.
- `functions/retrieve_kb/` and `functions/get_ticket_resolutions/` expose HTTP endpoints for querying the knowledge base and resolved tickets.
- `submit.py`, `self_check.sh`, and `gcloud_init.sh` support submission and GCP environment setup.
- `README.md` covers the full GCP infrastructure setup and pipeline deployment.

## Common Tooling

The Python-based subprojects use `pyproject.toml` and target Python 3.12+.

- `MP1-V2` depends on `pandas`
- `MP2` depends on `fastapi`, `httpx`, and `requests`
- `MP3` depends on `boto3`, DynamoDB type stubs, and `pytest`
- `MP4` depends on `requests`
- `MP6` depends on `confluent-kafka`, `kafka-python`, `flask`, `flask-pydantic`, `aws-msk-iam-sasl-signer-python`, and `boto3`
- `MP7` uses PySpark via the provided Docker image (no `pyproject.toml` dependencies)
- `MP8` depends on `pyspark`
- `RAG` depends on `apache-beam[gcp]`, `google-genai`, `google-cloud-bigquery`, `google-cloud-aiplatform`, `google-cloud-storage`, and `functions-framework`


## Working In This Repo

Because each assignment is self-contained, the usual workflow is:

1. Change into the relevant project directory.
2. Create or activate that project's virtual environment.
3. Install dependencies from `pyproject.toml` or `requirements.txt`.
4. Follow the project-specific `README.md` for AWS setup and execution steps.

> [!NOTE]
>
> - The subproject READMEs contain the detailed operational steps; this root README is intended as a map of the repository.
