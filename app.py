import os
import sys
from flask import Flask
from fnmcode import create_app

current_file_path = os.path.abspath(__file__)
root_folder_path = os.path.dirname(current_file_path)
project_dir = os.path.join(root_folder_path, "fnmcode")
env_file = os.path.join(project_dir, "vars.env")
templates_dir = os.path.join(project_dir, "templates")

if project_dir not in sys.path:
    sys.path.append(project_dir)

app = Flask(__name__, static_folder=templates_dir, template_folder=templates_dir)

app.config["SECRET_KEY"] = "FACTORYNSMANAGER"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

with open(env_file, "r", encoding="utf8") as f:
    for line in f:
        key, value = line.strip().split("=")
        os.environ[key] = value

app = create_app(app)

if __name__ == "__main__":
    app.run()
