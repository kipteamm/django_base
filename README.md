# The base of all my projects

## Setup

To get started make sure you change all `INSERT_EMAIL`, `INSERT_NAME` and `INSERT_PSW` in [settings.py](/django_project/settings.py).  
After that run migrations:

```py
python manage.py makemigrations django_project
python manage.py migrate
```

## Contents

- Signing up (with verification email)
- Logging in and out
- Reset password feature
