# AssociationRules

Implementation of the Association Rules algorithm in Python with Django + Celery for the UTN course "Artificial Intelligence".

### Dependencies:
* [Python 3.5 or higher](https://www.python.org/downloads/release/python-363/)
* [Celery 4](http://www.celeryproject.org/)
* [Redis 4](https://redis.io/)

### Recomendations:
* [Virtualenv through pip](https://virtualenv.pypa.io/en/stable/installation/)
* [GitHub](https://gist.github.com/derhuerst/1b15ff4652a867391f03)

### Instalation:
#### On Linux:
```bash
mkdir AssociationRules && cd AssociationRules
git clone https://github.com/paslo22/AssociationRules.git .
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
