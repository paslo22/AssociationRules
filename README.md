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
#### Linux:
```bash
mkdir AssociationRules && cd AssociationRules
git clone https://github.com/paslo22/AssociationRules.git .
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
# Broker (Redis) instalation:
sudo apt-get install redis-server
```

#### Windows ([Celery is not current supported on Windows](http://docs.celeryproject.org/en/latest/faq.html#does-celery-support-windows)):
```Windows
mkdir AssociationRules && cd AssociationRules
git clone https://github.com/paslo22/AssociationRules.git .
virtualenv -p Path\To\python3.exe env
env\Scripts\activate
pip install -r requirements.txt
```

### To get the server running on Linux you need to:
```bash
source env/bin/activate
python manage.py makemigrations web
python manage.py migrate
python manage.py runserver
# On another terminal:
source env/bin/activate
celery -A associationRules worker -l info
```

Then visit http://localhost:8000/

### Live demo on:
[Demo](https://nabla.com.ar/tpi/)
