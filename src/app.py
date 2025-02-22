# Enable venv on windows using the VSCode terminal with:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Unrestricted
# .\env\Scripts\Activate
# pip install -r requirements.txt


from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_cars = db.Column(db.Integer)
    car_width = db.Column(db.Double)
    velocity = db.Column(db.Double)
    # direction = db.Column(db.Integer)
    # last_recorded_intersection_id = db.Column(db.Integer, secondary_key=True)

class RoadRailIntersection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # trains_on_this_rail = db.Column(db.Integer, secondary_key=True)
    # time_until_blocked = db.Column(db.Integer)
    elapsed_blocked_time = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"RoadRailIntersection {self.id}"

@app.route("/")
def index():
    return "Hello World!"

@app.route("/data", methods=["POST", "GET"])
def data():
    if request.method == "POST":
        request_json = request.json
        return f"got it! {request_json}"
    elif request.method == "GET":
        return "/data"

if __name__ in "__main__":
    app.run(debug=True)
