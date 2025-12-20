---
description: how to set up and run the CID platform locally
---

### Prerequisites
- Node.js and npm
- Python 3.10+
- (Optional) Google Cloud SDK for Firestore/Secret Manager

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Setup (Local Development)
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. To run a specific Cloud Function locally (e.g., `analyze_syllabus`):
   ```bash
   # In separate terminals:
   functions-framework --target analyze_syllabus --port 8081 --source functions/analyze_syllabus/main.py
   functions-framework --target simulate_path --port 8082 --source functions/simulate_path/main.py
   functions-framework --target manage_path --port 8083 --source functions/manage_path/main.py
   ```

### Initializing Data
To populate your local Firestore (or mock) with pedagogical data:
```bash
python3 scripts/init_pedagogical_data.py
```
*Note: Ensure `GCP_PROJECT_ID` is set or it will use a mock project.*
