dev:
	pip install -e ".[dev]"

test:
	pytest -s

runapi:
	AX_ENV=TEST AWS_PROFILE=acrossfc fastapi dev tests/dev_api_server.py

lambda:
	lambda/deploy.sh
