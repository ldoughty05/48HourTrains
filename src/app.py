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
    # train_velocity = db.Column(db.Double)
    train_block_time = db.Column(db.Integer)
    car_velocity = db.Column(db.Double)
    hold_time = db.Column(db.Integer)
    car_phase = db.Column(db.Integer)
    last_update_epoch = db.Column(db.Integer)


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
        # Extract 'location_id' from the JSON request
        location_id = request.json.get('location_id')

        if location_id is None:
            return jsonify({"error": "400 Bad Request", "details": "Missing 'location_id' in request body."}), 400

        # Query the database using 'location_id' as the primary key (id)
        intersection = RoadRailIntersection.query.get(location_id)

        if intersection is None:
            return jsonify({"error": "404 Not Found", "details": f"No intersection found for location_id {location_id}"}), 404

        # Update the intersection's attributes with new values from the request
        intersection.car_velocity = request.json.get('car_velocity', intersection.car_velocity)
        intersection.hold_time = request.json.get('hold_time', intersection.hold_time)
        intersection.car_phase = request.json.get('car_phase', intersection.car_phase)
        intersection.car_width = 4.0
        intersection.train_block_time = request.json.get('train_block_time', intersection.train_block_time)
        intersection.last_update_epoch = request.json.get('timestamp', intersection.last_update_epoch)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"message": "200 OK", "details": "Intersection updated successfully."}), 200

    except Exception as e:
        return jsonify({"error": "500 Internal Server Error", "details": str(e)}), 500

        

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
            "train_block_time": intersection.train_block_time,
            "car_velocity": intersection.car_velocity,
            "hold_time": intersection.hold_time,
            "car_phase": intersection.car_phase,
            "last_update_epoch": intersection.last_update_epoch,
        })
    except Exception as e:
        return jsonify({"error": f"502 Couldn't get intersection rows.", "details": str(e)}), 502


@app.route("/")
def index():
    res = requests.get("http://127.0.0.1:5000/data/1").json()
    print(res)
    # intersection = res.get("car_velocity", "Unknown")  # Handle case where key might not exist
    return render_template('index.html', intersection=res)

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

