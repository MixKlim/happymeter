SHELL=CMD

backend:
	@echo "Running backend"
	poetry run uvicorn src.app.main:app --port=8080 --reload

frontend:
	@echo "Running frontend"
	poetry run streamlit run src/streamlit/ui.py --server.port 8501

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
	docker build -t backend-image -f Dockerfile.backend .
	docker run --name backend-container -p 8080:8080 --rm backend-image

docker-frontend:
	@echo "Creating docker image and container for frontend"
	docker build -t frontend-image -f Dockerfile.frontend .
	docker run --name frontend-container -p 8501:8501 --rm frontend-image

docker-compose:
	@echo "Running docker compose"
	docker compose build
	docker compose up
