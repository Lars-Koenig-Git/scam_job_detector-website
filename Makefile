
default: pytest

pytest:
	@echo "Running pytest..."
	@pytest -q


# ----------------------------------
#         LOCAL SET UP
# ----------------------------------

install_requirements:
	@pip install -r requirements.txt

# ----------------------------------
#         HEROKU COMMANDS
# ----------------------------------

streamlit:
	-@streamlit run app.py

# Convenience: run Streamlit with SCAM_API_URL (default http://127.0.0.1:8000)
run-streamlit:
	@echo "Starting Streamlit (SCAM_API_URL=${SCAM_API_URL:-http://127.0.0.1:8000})"
	@SCAM_API_URL=${SCAM_API_URL:-http://127.0.0.1:8000} streamlit run app.py

# Convenience: start FastAPI server from adjacent real app repo (if present)
run-api:
	@echo "Starting FastAPI from ../scam-job-detector (if available)"
	@cd ../scam-job-detector && uvicorn api.fast:app --reload || (echo "Could not start FastAPI: ensure ../scam-job-detector exists and uvicorn is installed" && exit 1)

# Run API (in background) and Streamlit (foreground)
run-all:
	@echo "Starting API and Streamlit; API runs in background"
	@cd ../scam-job-detector && nohup uvicorn api.fast:app --reload > /tmp/uvicorn.out 2>&1 & sleep 1 || true
	@SCAM_API_URL=${SCAM_API_URL:-http://127.0.0.1:8000} streamlit run app.py

# ----------------------------------
#    LOCAL INSTALL COMMANDS
# ----------------------------------
install:
	@pip install . -U

clean:
	@rm -fr */__pycache__
	@rm -fr __init__.py
	@rm -fr build
	@rm -fr dist
	@rm -fr *.dist-info
	@rm -fr *.egg-info
	-@rm model.joblib
