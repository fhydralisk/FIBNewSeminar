# FIBNewSeminar, FIB Lab Seminar background and frontend, Powered by django

## Requirement

Django >= 1.11.0

Python >= 2.7.6

Python3 is not supported


## Installation

Install Django >= 1.11.0

```bash
$ git clone https://github.com/fhydralisk/FIBNewSeminar.git
$ cd FIBNewSeminar
```

### Initialize database

```bash
$ python manage.py makemigrations

$ python manage.py migrate

$ python manage.py createsuperuser
Username (leave blank to use 'hydra'): superusername
Email address: your@company.com
Password: ********
```

## Run Testing Server

```bash
$ python manage.py runserver 127.0.0.1:8000
```

## Test The Admin site

http://127.0.0.1:8000/admin/

## Test The Index Page

http://127.0.0.1:8000/
