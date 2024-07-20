# GNR: Restrooms for All

This is a simple web app built in high school to find gender-neutral restrooms anywhere in the US. Visit [restroom.network](https://restroom.network) to see it in action.

- web framework: [flask](https://flask.palletsprojects.com/en/2.2.x)
- template engine: [jinja2](https://jinja.palletsprojects.com/en/3.1.x)
- css framework: current [tailwindcss](https://tailwindcss.com); past [bootstrap](https://getbootstrap.com)

## Getting Started

### Virtual Environment

- `python3 -m venv venv` create virtual env folder (run once)
- `. venv/bin/activate` enter virtual env
- `deactivate` leave virtual env

### Install Dependencies

- `pip3 install -r requirements.txt` install python requirements

### Create .env in project directory

```zsh
cp .env.example .env
```

### Development

- `flask --app main --debug run` start the server for development
- `tailwindcss -i styles/main.css -o static/css/main.css --watch` start tailwindcss

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
