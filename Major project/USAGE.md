# Application Usage Guide

This project includes a FastAPI backend and a React + Vite frontend.
The frontend sends input feature values to the backend for credit risk prediction and SHAP-based explainability.

---

## 1. Prerequisites

- Python 3.11+ (or compatible Python 3.x)
- Node.js and npm
- Git or filesystem access to the project folder

---

## 2. Install dependencies

### Backend

Open a terminal in the project root and run:

```powershell
cd "C:\Users\chinm\Desktop\Major project\backend"
pip install -r requirements.txt
```

### Frontend

Open a separate terminal and run:

```powershell
cd "C:\Users\chinm\Desktop\Major project\frontend"
npm install
```

---

## 3. Build the frontend

The application uses a static production build in `frontend/dist`.

From the `frontend` folder:

```powershell
npm run build
```

If you already have a `frontend/dist` folder (this project currently includes one), you can skip this step.

---

## 4. Start the backend and frontend together

The project root includes `run_all.bat`, which now launches:

- the FastAPI backend at `http://127.0.0.1:8000`
- the static frontend from `frontend/dist` using `npx serve`

From the project root:

```powershell
.\
un_all.bat
```

### What this does

- starts the backend server with `python backend\app.py`
- serves the frontend build with `npx serve -s frontend\dist`

If the frontend does not appear, make sure `frontend/dist` exists and is up to date.

---

## 5. Open the app in your browser

Once `run_all.bat` is running, open:

```text
http://localhost:3000
```

If the browser does not connect, check the terminal output from `serve` for the exact port and URL.

---

## 6. How the frontend uses the backend

The frontend loads metadata and makes prediction requests via the backend API at `http://localhost:8000`.

### Backend API endpoints used by the frontend

- `GET /features`
  - returns feature metadata for the input form
- `GET /model-info`
  - returns model metadata and evaluation metrics
- `POST /explain`
  - accepts applicant input data and returns
    - prediction result
    - default probability
    - confidence
    - risk category
    - SHAP feature contributions
    - text explanation

### Frontend pages

- The main dashboard shows the applicant input form and prediction results.
- The `InputForm` component validates feature values and submits data.
- The `Results` component displays the prediction, probability, and explainability output.

---

## 7. Using the app

1. Open the browser at `http://localhost:3000`.
2. Wait until the app indicates the backend is online.
3. Enter values for the loan applicant fields.
4. Use the preset examples if you want a quick test.
5. Click the submit button to get a prediction and explanation.

The app will display:

- predicted status: `Fully Paid` or `Charged Off`
- default probability
- confidence score
- risk category: `Low Risk`, `Moderate Risk`, `High Risk`, or `Very High Risk`
- SHAP feature contributions and explanation text

---

## 8. Troubleshooting

- If the frontend shows a connection error, make sure the backend is running on `http://localhost:8000`.
- If `run_all.bat` fails, run the backend and frontend separately:

  - Backend:
    ```powershell
    cd "C:\Users\chinm\Desktop\Major project\backend"
    python app.py
    ```

  - Frontend:
    ```powershell
    cd "C:\Users\chinm\Desktop\Major project\frontend"
    npx serve -s dist
    ```

- If the backend fails to start, verify the ML artifacts are present and that `backend/requirements.txt` packages are installed.

---

## 9. Notes

- The backend health check is available at `GET /`.
- The frontend uses the backend URL hard-coded as `http://localhost:8000` in `frontend/src/utils/api.ts`.
- If you change the backend host or port, update `API_BASE_URL` accordingly.
