from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

# change ur path : "D:\AI Project Store"
PROJECT_ROOT = Path(r"C:\Users\hp\OneDrive\Desktop\web_scraping_folder\fraud_detection_ml_project")


# ============================================================
# DIRECTORY STRUCTURE
# ============================================================

directories = [

    # ---------------- ROOT ----------------
    "",

    # ---------------- FRONTEND ----------------
    "frontend",
    "frontend/public",
    "frontend/src",
    "frontend/src/api",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/charts",
    "frontend/src/hooks",
    "frontend/src/utils",

    # ---------------- BACKEND ----------------
    "backend",
    "backend/app",
    "backend/app/config",
    "backend/app/api",
    "backend/app/api/routes",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/database",
    "backend/app/ml",
    "backend/app/utils",
    "backend/tests",

    # ---------------- MACHINE LEARNING ----------------
    "ml",
    "ml/data",
    "ml/features",
    "ml/models",
    "ml/experiments",

    # ---------------- DATA ----------------
    "data",
    "data/raw",
    "data/processed",
    "data/reference",

    # ---------------- MODELS ----------------
    "models",
    "models/production",
    "models/candidates",

    # ---------------- MLOPS ----------------
    "mlops",
    "mlops/monitoring",
    "mlops/monitoring/reports",
    "mlops/retraining",

    # ---------------- NOTEBOOKS ----------------
    "notebooks",

    # ---------------- TESTS ----------------
    "tests",
    "tests/unit",
    "tests/integration",

    # ---------------- SCRIPTS ----------------
    "scripts",

    # ---------------- ARTIFACTS ----------------
    "artifacts",
    "artifacts/metrics",
    "artifacts/plots",
    "artifacts/reports",

    # ---------------- CONFIG ----------------
    "configs",

    # ---------------- GITHUB ACTIONS ----------------
    ".github",
    ".github/workflows",
]


# ============================================================
# CREATE DIRECTORIES
# ============================================================

for directory in directories:

    path = PROJECT_ROOT / directory

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    print(f"Created: {path}")


# ============================================================
# FILE STRUCTURE
# ============================================================

files = [

    # ---------------- ROOT ----------------
    "README.md",
    ".gitignore",
    ".env.example",
    "docker-compose.yml",
    "Dockerfile",
    "params.yaml",
    "dvc.yaml",

    # ---------------- FRONTEND ----------------
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/vite.config.js",
    "frontend/index.html",

    "frontend/src/main.jsx",
    "frontend/src/App.jsx",
    "frontend/src/index.css",

    # Frontend API
    "frontend/src/api/axios.js",
    "frontend/src/api/predictionApi.js",
    "frontend/src/api/transactionApi.js",
    "frontend/src/api/analyticsApi.js",
    "frontend/src/api/monitoringApi.js",
    "frontend/src/api/modelApi.js",

    # Frontend Components
    "frontend/src/components/Navbar.jsx",
    "frontend/src/components/Sidebar.jsx",
    "frontend/src/components/StatCard.jsx",
    "frontend/src/components/PredictionCard.jsx",
    "frontend/src/components/RiskBadge.jsx",
    "frontend/src/components/Loading.jsx",
    "frontend/src/components/ErrorMessage.jsx",

    # Frontend Pages
    "frontend/src/pages/Dashboard.jsx",
    "frontend/src/pages/PredictFraud.jsx",
    "frontend/src/pages/Transactions.jsx",
    "frontend/src/pages/Analytics.jsx",
    "frontend/src/pages/Monitoring.jsx",
    "frontend/src/pages/ModelManagement.jsx",

    # Frontend Charts
    "frontend/src/charts/FraudTrendChart.jsx",
    "frontend/src/charts/TransactionChart.jsx",
    "frontend/src/charts/ModelMetricsChart.jsx",
    "frontend/src/charts/DriftChart.jsx",

    # Frontend Hooks
    "frontend/src/hooks/usePrediction.js",
    "frontend/src/hooks/useTransactions.js",
    "frontend/src/hooks/useMonitoring.js",

    # Frontend Utils
    "frontend/src/utils/formatters.js",
    "frontend/src/utils/constants.js",

    # ---------------- BACKEND ----------------
    "backend/requirements.txt",
    "backend/Dockerfile",

    "backend/app/__init__.py",
    "backend/app/main.py",

    # Backend Config
    "backend/app/config/__init__.py",
    "backend/app/config/settings.py",

    # Backend API
    "backend/app/api/__init__.py",
    "backend/app/api/dependencies.py",

    # Backend Routes
    "backend/app/api/routes/__init__.py",
    "backend/app/api/routes/prediction.py",
    "backend/app/api/routes/transactions.py",
    "backend/app/api/routes/analytics.py",
    "backend/app/api/routes/monitoring.py",
    "backend/app/api/routes/model.py",

    # Backend Schemas
    "backend/app/schemas/__init__.py",
    "backend/app/schemas/prediction.py",
    "backend/app/schemas/transaction.py",
    "backend/app/schemas/analytics.py",
    "backend/app/schemas/monitoring.py",
    "backend/app/schemas/model.py",

    # Backend Services
    "backend/app/services/__init__.py",
    "backend/app/services/prediction_service.py",
    "backend/app/services/transaction_service.py",
    "backend/app/services/analytics_service.py",
    "backend/app/services/monitoring_service.py",
    "backend/app/services/model_service.py",

    # Backend Database
    "backend/app/database/__init__.py",
    "backend/app/database/database.py",
    "backend/app/database/models.py",
    "backend/app/database/crud.py",

    # Backend ML
    "backend/app/ml/__init__.py",
    "backend/app/ml/model_loader.py",
    "backend/app/ml/predictor.py",
    "backend/app/ml/preprocessor.py",

    # Backend Utils
    "backend/app/utils/__init__.py",
    "backend/app/utils/logger.py",
    "backend/app/utils/exceptions.py",

    # Backend Tests
    "backend/tests/test_prediction.py",
    "backend/tests/test_transactions.py",
    "backend/tests/test_api.py",

    # ---------------- ML ----------------
    "ml/data/ingestion.py",
    "ml/data/validation.py",
    "ml/data/preprocessing.py",

    "ml/features/feature_engineering.py",

    "ml/models/train.py",
    "ml/models/evaluate.py",
    "ml/models/tune.py",

    "ml/experiments/baseline.py",
    "ml/experiments/random_forest.py",
    "ml/experiments/xgboost.py",

    # ---------------- MLOPS ----------------
    "mlops/monitoring/data_drift.py",
    "mlops/monitoring/prediction_drift.py",
    "mlops/monitoring/performance.py",

    "mlops/retraining/trigger.py",
    "mlops/retraining/retrain.py",
    "mlops/retraining/validation.py",

    # ---------------- NOTEBOOKS ----------------
    "notebooks/01_eda.ipynb",
    "notebooks/02_feature_engineering.ipynb",
    "notebooks/03_imbalance.ipynb",
    "notebooks/04_training.ipynb",
    "notebooks/05_evaluation.ipynb",

    # ---------------- TESTS ----------------
    "tests/unit/test_ml_pipeline.py",
    "tests/integration/test_integration.py",

    # ---------------- SCRIPTS ----------------
    "scripts/train.py",
    "scripts/evaluate.py",
    "scripts/retrain.py",

    # ---------------- CONFIG ----------------
    "configs/model.yaml",
    "configs/features.yaml",
    "configs/monitoring.yaml",

    # ---------------- GITHUB ----------------
    ".github/workflows/ci.yml",
    ".github/workflows/training.yml",
]


# ============================================================
# CREATE FILES
# ============================================================

for file in files:

    path = PROJECT_ROOT / file

    # Create parent directory if required
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create empty file
    path.touch(
        exist_ok=True
    )

    print(f"Created file: {path}")


# ============================================================
# CREATE .GITKEEP FILES
# ============================================================

empty_directories = [
    "data/raw",
    "data/processed",
    "data/reference",
    "models/production",
    "models/candidates",
    "mlops/monitoring/reports",
    "artifacts/metrics",
    "artifacts/plots",
    "artifacts/reports",
]

for directory in empty_directories:

    gitkeep = PROJECT_ROOT / directory / ".gitkeep"

    gitkeep.touch(
        exist_ok=True
    )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("PROJECT CREATED SUCCESSFULLY")
print("=" * 70)

print(f"\nProject location:")
print(PROJECT_ROOT)

print("\nNext steps:")
print("1. cd into the project")
print("2. Create Python virtual environment")
print("3. Install backend requirements")
print("4. Create React/Vite frontend")
print("5. Add ML dataset")
print("6. Build training pipeline")
print("7. Start FastAPI")
print("8. Start React frontend")