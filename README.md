set PYTHON_ENV=development, production # default development
set FLASK_ENV=development, production

in .env file
PYTHONPATH in .env file - use semi colon in windows and maybe colon in unix


# If you haven't already, then start a pipenv shell
pipenv shell

PYTHON_ENV=development python src/main.py

# run test in pipenv shell
python -m pytest 



# Database
check if postgres service is up through services.msc
user/pass - postgres/same

# Database migration
flask db init - used initially to setup tables
flask db migrate - whenever tables change
flask db upgrade - actually run the changes in tables
flask db downgrade - revert the changes from tables
