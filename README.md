# Fraud Detection ML Project

## Run the project

### 1. Backend

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend

From the project root in a second terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Then open:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Notes

- Alerts are stored in SQLite at `fraud_detection.db` and persist across backend restarts.
- Transaction history and alerts are kept separate: deleting a transaction removes that prediction record, but saved alert history remains as a security audit trail unless the alert itself is deleted.
- The unread alert badge is loaded from the backend unread-count endpoint and updates as alerts are created, marked as read, or deleted.
