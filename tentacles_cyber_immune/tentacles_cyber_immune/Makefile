dev_install:
	pip install -r requirements.txt

all:
	docker compose up -d --build
	sleep 3

logs:
	docker compose logs -f

test:
	pytest tests/e2e_test.py -v

test_security:
	docker compose exec central_system pytest tests/test_policies.py -v

clean:
	docker compose down -v
