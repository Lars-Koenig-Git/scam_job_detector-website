# Scam Job Detector 🔍

**Scam Job Detector** is a small Streamlit app that helps identify likely fake job postings using a remote ML prediction service. Enter a job posting (title, description, requirements, benefits) and the app will call a hosted API to predict whether the posting is fraudulent and provide an explanation (word cloud) of features driving the result.

---

## ⚙️ Features

- Paste a full job posting and get a prediction (fake vs. genuine)
- Optional fields to improve predictions: **employment type**, **country**, **industry**, **has company logo**
- Word cloud explanation showing text features that drove the prediction
- URL preview card for quick article/link inspection

---

## 🚀 Quick start

1. Clone the repository and open the project folder.
2. (Recommended) Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Unix / macOS
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
# or
make install_requirements
```

4. Run the app locally:

```bash
streamlit run app.py
# or
make streamlit
```

5. Open the local Streamlit URL shown in the terminal (usually http://localhost:8501).

---

## 🧩 How to use

- Paste the full job posting in the main text area.
- Optionally select `Employment type`, `Country`, `Industry`, and whether the company provided a logo.
- Click **Predict** to get a fraud probability and a simple fake/genuine indicator.
- Click **Explain** to compute and display the word cloud with features contributing to the prediction.
- Use the **URL** input to render a preview card for a given link.

---

## 🔧 Configuration & notes

- The app calls two local endpoints for model inference:
  - `/predict` (used by the **Predict** button)
  - `/explain` (used by the **Explain** button)

  This Streamlit UI expects a local FastAPI server (the "real app") to be running. You can run the real FastAPI server from the other repository (e.g., `../scam-job-detector`) which provides the prediction and explain endpoints.

  Quick steps to run the API locally:
  1. Clone or navigate to the real app repo (e.g., `../scam-job-detector`).
  2. Install dependencies: `pip install -r requirements.txt`.
  3. Ensure model artifacts exist in `models/` (run training steps in that repo if needed).
  4. Start the API: `uvicorn api.fast:app --reload` (default: http://127.0.0.1:8000).

  Configuring the Streamlit app:
  - The Streamlit app reads the API base URL from the `SCAM_API_URL` environment variable. If not set it defaults to `http://127.0.0.1:8000`.
  - Example (Unix/macOS): `export SCAM_API_URL="http://127.0.0.1:8000"` then `streamlit run app.py`.
  - Example (Windows PowerShell): `$env:SCAM_API_URL = "http://127.0.0.1:8000"; streamlit run app.py`.

  Or use the provided Makefile helpers from this folder:

  - `make run-streamlit` → runs Streamlit with `SCAM_API_URL` defaulting to `http://127.0.0.1:8000` (or use `SCAM_API_URL=... make run-streamlit`).
  - `make run-api` → attempts to start the FastAPI server from `../scam-job-detector` (useful if you keep the real app next to this repo).
  - `make run-all` → runs the API (background) and Streamlit (foreground).


- The link preview scraper can be blocked by some sites (LinkedIn may respond with status 999/401/403). The app will show a warning if preview is unavailable.

---

## 🐞 Troubleshooting

- If you get network errors when predicting, confirm you have internet access and that the remote API is reachable.
- If word cloud or model outputs are empty, ensure you clicked **Predict** first so the required session state values are populated before using **Explain**.
- If the URL preview fails for a site, try opening the link directly in your browser.

---

## 📦 Project files

- `app.py` — Streamlit application UI and logic
- `requirements.txt` — Python dependencies
- `scam_job_detector.png` — Banner image used in the app
- `data/` — JSON files with countries, industries, functions and employment types

---

## Contributing

Contributions are welcome. Open an issue or submit a pull request with improvements or bug fixes.

---

## License

No license specified. Add a `LICENSE` file if you want to pick one (e.g., MIT).

---

> If you'd like, I can also add a basic `Makefile` target or an environment variable option to configure the API base URL instead of editing `app.py` directly. 💡
