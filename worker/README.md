# worker

## Local debug
Create Virtual env and install requirements.
```bash
cd worker
python3 -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```

## Local start
```bash
celery -A src.tasks worker --loglevel=info

celery -A src.tasks --loglevel=info -Q run_calculation,ta_calculation,ta_final
```