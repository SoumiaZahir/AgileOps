# 🎓 Smart Platform for University Success

## 🚀 Overview
Welcome to the core repository for the **Student Pass/Fail Prediction Platform**[cite: 1]. This platform is designed to predict student outcomes and help the university perform early interventions[cite: 1]. 

As the **DevOps/MLOps Infrastructure**, the initial repository structure, automation pipelines (CI), and containerized baseline environments have been established[cite: 1, 2].

---

## 📂 Repository Structure & Ownership
The repository is structured as a modular MLOps ecosystem[cite: 1]. Here is the breakdown of the directories and who owns each part[cite: 1]:

*   **`.github/workflows/`**: Holds the automated CI/CD pipelines (**Soumia**)[cite: 1].
*   **`infra/docker/`**: Contains the Docker Compose and multi-container infrastructure setup (**Soumia**)[cite: 1].
*   **`pipelines/`**: Data engineering workflows[cite: 1].
    *   `ingestion/`: Raw data pulling scripts (**Aymen**)[cite: 1].
    *   `transformation/`: `dbt` models for clean feature stores (**Marouane**)[cite: 1].
    *   `orchestration/`: Dagster jobs pipeline coordination (**Maroua**)[cite: 1].
*   **`data_quality/`**: Automated Great Expectations rules (**Imane**)[cite: 1].
*   **`ml/`**: Machine Learning experiment tracking and model training (**Abderahman**)[cite: 1].
*   **`api/`**: FastAPI implementation to serve the production models (**Houssame**)[cite: 1].
*   **`monitoring/`**: Prometheus, Grafana, and Evidently AI for health and drift tracking (**Hanane**)[cite: 1].
*   **`dashboards/`**: Power BI / Metabase analytics solutions (**Brahim**)[cite: 1].
*   **`docs/`**: Central documentation workspace (**Marwan**)[cite: 1].
*   **`tests/`**: Integration and unit test testing suites (**Marwan + All**)[cite: 1].

---

## 🛠️ Infrastructure Core Components (What's Configured)

### 1. Automated Quality Gate (CI Pipeline)
Located at `.github/workflows/ci.yml`[cite: 1]. This pipeline triggers automatically on every **Push** or **Pull Request** to the `main` or `develop` branches[cite: 2].
*   **Code Linting (`ruff`):** Ensures everyone's code stays clean and adheres to standard styling constraints by checking for errors automatically[cite: 2].
*   **Code Formatting (`black`):** Enforces a unified bracket, spacing, and formatting style across the whole team[cite: 2].
*   *Future Placeholders:* Pre-arranged empty hooks are waiting to catch your code for automated testing (`dbt test`, `Great Expectations`, and `pytest`) before any merge[cite: 2].

### 2. Foundational Container Ecosystem
Located at `infra/docker/docker-compose.yml`[cite: 1]. It provides a single-command baseline to launch the core MLOps servers locally[cite: 1]:
*   **MLflow Server**: Central hub for Abderahman to track models, logs, metrics, and register artifact stages[cite: 1].
*   **Dagster Core**: The baseline daemon engine and web UI interface for Maroua to coordinate asset synchronization[cite: 1].

---

## 🏁 How to Run Locally (For the Team)
Once you have **Docker Desktop** installed on your machine, you can spin up the entire foundation by opening your terminal and running[cite: 1]:

```bash
# Navigate to the infrastructure folder
cd infra/docker

# Boot up the core MLOps ecosystem
docker-compose up -d
=======
# Data Ingestion Pipeline

## Description

This project implements the raw data ingestion pipeline for the OULAD dataset.

The pipeline:

- Reads raw CSV files
- Loads data into DuckDB
- Generates ingestion logs
- Updates ingestion metadata

## Project Structure

```
DATA_INGESTION/
│
├── data/
│   ├── sources/
│   └── raw/
│
├── docs/
│
├── pipelines/
│   └── ingestion/
```

## Requirements

- Python 3.13+
- pandas
- duckdb

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run the pipeline

```bash
python pipelines/ingestion/run_all.py
```

## Output

The pipeline creates:

- data/raw/university.duckdb
- data/raw/metadata.json
- data/raw/ingestion_log.jsonl
## Dataset

The dataset is stored on Google Drive because some files exceed GitHub's size limit.

Download the dataset from:

https://drive.google.com/drive/folders/1v6GwNzzAiyG5FJPWtSeCYtMMamGrz9bu

Extract the files and place them in:

data/sources/

Then run:

```bash
python pipelines/ingestion/run_all.py
```
