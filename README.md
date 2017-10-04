# AssociationRules

Implementation of the Association Rules algorithm in Python with Django + Celery for the UTN course "Artificial Intelligence".

Dependencies:
* [Python 3.5 or higher](https://www.python.org/downloads/release/python-363/)

Recomendations:
* [Virtualenv through pip](https://virtualenv.pypa.io/en/stable/installation/)
* [GitHub](https://gist.github.com/derhuerst/1b15ff4652a867391f03)

Instalation:
Linux:
```bash
mkdir AssociationRules && cd AssociationRules
git clone https://github.com/paslo22/AssociationRules.git .
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

Windows:
```Windows
mkdir AssociationRules && cd AssociationRules
git clone https://github.com/paslo22/AssociationRules.git .
virtualenv -p Path\To\python3.exe env
env\Scripts\activate
pip install -r requirements.txt
```

Troubleshooting:
TODO

To get the server running you need to:
```bash
python manage.py migrate
python manage.py runserver
```

Then visit http://localhost:8000/

Live demo on:
TODO
