SHELL=CMD

help:
	@echo "  backend           - Run the backend using uvicorn"
	@echo "  frontend          - Run the frontend using Streamlit"
	@echo "  eval              - Run pre-commit checks on all files"
	@echo "  test              - Run unit tests with pytest"
	@echo "  cov               - Generate coverage report and badge"
	@echo "  build             - Evaluate code, run tests, and generate coverage"
	@echo "  docker-backend    - Create and run Docker container for backend"
	@echo "  docker-frontend   - Create and run Docker container for frontend"
	@echo "  docker-compose    - Build and run services using Docker Compose"

backend:
	@echo "Running backend"
	poetry run uvicorn src.app.main:app --port=8080 --reload

frontend:
	@echo "Running frontend"
	poetry run streamlit run src/streamlit/ui.py --server.address 127.0.0.1 --server.port 8501

eval:
	@echo "Running pre-commit"
	poetry run pre-commit run --all-files

test:
	@echo "Running unit test"
	poetry run pytest --doctest-modules --cov=. --cov-report=html

cov:
	@echo "Creating coverage badge"
	coverage report
	coverage xml -o ./reports/coverage/coverage.xml
	coverage html
	genbadge coverage --output-file reports/coverage/coverage-badge.svg

build: eval test cov

docker-backend:
	@echo "Creating docker image and container for backend"
	docker build -t happymeter-backend -f Dockerfile.backend .
	docker run --name backend-container -p 8080:8080 --rm happymeter-backend

docker-frontend:
	@echo "Creating docker image and container for frontend"
	docker build -t happymeter-frontend -f Dockerfile.frontend .
	docker run --name frontend-container -p 8501:8501 --rm happymeter-frontend

docker-compose:
	@echo "Running docker compose"
	docker compose build
	docker compose up
