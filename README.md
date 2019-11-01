set PYTHON_ENV=development, production # default development
set FLASK_ENV=development, production

in .env file
PYTHONPATH in .env file - use semi colon in windows and maybe colon in unix


# If you haven't already, then start a pipenv shell
pipenv shell

PYTHON_ENV=development python src/main.py

# run test in pipenv shell
python -m pytest 