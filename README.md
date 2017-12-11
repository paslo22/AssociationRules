# AssociationRules

Implementation of the Association Rules algorithm in Python with Django + Celery for the UTN course "Artificial Intelligence".

### Dependencies:
* [Python 3.5 or higher](https://www.python.org/downloads/release/python-363/)
* [Celery 4](http://www.celeryproject.org/)
* [Redis 4](https://redis.io/)

### Recomendations:
* [Virtualenv through pip](https://virtualenv.pypa.io/en/stable/installation/)

### Instalation:
#### On Linux:
```bash
unzip AssociationRules.zip
cd AssociationRules-master
pip install -r requirements.txt
# Broker (Redis) instalation:
sudo apt-get install redis-server
```

### To get the server running on Linux you need to:
```bash
python3 manage.py makemigrations web
python3 manage.py migrate
python3 manage.py runserver
# On another terminal:
celery -A associationRules worker -l info
```

Then visit http://localhost:8000/

### Live demo on:
[Demo](https://nabla.com.ar/tpi/)
