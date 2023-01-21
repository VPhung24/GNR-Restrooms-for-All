# GNR: Restrooms for All

built in high school

## set in `.zshrc`

```
export FLASK_APP=main.py
export FLASK_DEBUG=true
```

## virtual environment

- `python3 -m venv venv` create virtual env folder (run once)
- `. venv/bin/activate` enter virtual env
- `deactivate` leave virtual env

## requirement 

- python3.10 

## install dependencies

- `pip install -r requirements.txt` install python requirements

## create .env in project directory

- `touch .env`
- in `.env` file, add secrets

```
API_KEY='<api_key>`
```

## run app (dev)

- `flask run` start the server for development

- if you didn't update your `.zshrc`, `flask --app main --debug run`
