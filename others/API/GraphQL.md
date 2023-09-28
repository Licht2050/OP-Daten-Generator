# Setup Graphql Endpoint
## first setup Python Envoriment first install "python3.10-venv"
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setup Graphql Endpoint
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

# run API GraphQL-Server
```bash
uvicorn app:app --host 192.168.29.120 --port 5000 --reload --ws wsproto
```

