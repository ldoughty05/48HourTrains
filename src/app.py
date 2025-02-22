# Enable venv on windows using the VSCode terminal with:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Unrestricted
# .\env\Scripts\Activate
# pip install -r requirements.txt


from flask import Flask, render_template, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # num_cars = db.Column(db.Integer)
    # car_width = db.Column(db.Double)
    # velocity = db.Column(db.Double)
    # direction = db.Column(db.Integer)
    # last_recorded_intersection_id = db.Column(db.Integer, secondary_key=True)

class RoadRailIntersection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_cars = db.Column(db.Integer)
    car_width = db.Column(db.Double)
    train_velocity = db.Column(db.Double)
    train_block_time = db.Column(db.Integer)
    # trains_on_this_rail = db.Column(db.Integer, secondary_key=True)
    # time_until_blocked = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"RoadRailIntersection {self.id}"
    
def initialize_database():
    db.create_all()
    if not RoadRailIntersection.query.first():
        intersection000 = RoadRailIntersection(id=0)
        intersection001 = RoadRailIntersection(id=1)
        db.session.add(intersection000)
        db.session.add(intersection001)
        db.session.commit()


def handle_data_put():
    try:
        id = request.json['location_id']
        intersection = RoadRailIntersection.query.get_or_404(id)
    except Exception as e:
        return jsonify({"error": f"504 Couldn't find intersection in database.", "details": str(e)}), 504
    try:
        intersection.velocity = request.json['train_velocity']
        intersection.train_block_time = request.json['train_block_time']
        return "200 OK"
    except Exception as e:
        return jsonify({"error": f"501 Couldn't update intersection rows.", "details": str(e)}), 501
        

def handle_data_post():
    request_json = request.json
    return f"got it! {request_json}"


def handle_data_get(id:int):
    try:
        intersection = RoadRailIntersection.query.get_or_404(id)
    except Exception as e:
        return jsonify({"error": f"504 Couldn't find intersection in database.", "details": str(e)}), 504
    try:
        return jsonify({
            "id": intersection.id,
            "num_cars": intersection.num_cars,
            "car_width": intersection.car_width,
            "train_velocity": intersection.train_velocity,
            "train_block_time": intersection.train_block_time
        })
    except Exception as e:
        return jsonify({"error": f"502 Couldn't get intersection rows.", "details": str(e)}), 502
    

@app.route("/")
def index():
    res = requests.get("http://127.0.0.1:5000/data/1").json()
    velocity = res.get("train_velocity", "Unknown")  # Handle case where key might not exist
    return f"Toy Car Velocity {velocity}"

@app.route("/data", methods=["POST", "PUT"])
def data():
    if request.method == "PUT":
        return handle_data_put()
    elif request.method == "POST":
        return handle_data_post()
    

@app.route("/data/<int:id>", methods=["GET"])
def data_get(id:int):
    if request.method == "GET":
        return handle_data_get(id)
    

if __name__ == "__main__":
    with app.app_context():
        initialize_database()
    app.run(debug=True)

