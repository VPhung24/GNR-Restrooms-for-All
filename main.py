from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from uszipcode import SearchEngine
from yelp_fusion_helper import fetch_businesses, get_total_results
import os
import threading
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")
app.url_map.strict_slashes = False
bootstrap = Bootstrap4(app)
app.secret_key = "GNR for life"

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///businesses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Thread-local storage for the SearchEngine instance
search_engine_local = threading.local()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


# Define Business model
class Business(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    url = db.Column(db.String)
    review_count = db.Column(db.Integer)
    rating = db.Column(db.Float)
    location = db.Column(db.String)


def get_search_engine():
    if not hasattr(search_engine_local, "engine"):
        search_engine_local.engine = SearchEngine()
    return search_engine_local.engine


@app.route("/", methods=["GET", "POST"])
def main_route():
    if request.method == "POST":
        location_user = request.form["location"]
        type_user = request.form["type"]

        if not location_user or not type_user:
            return render_template(
                "index.html", error="Please provide inputs.", found=False
            )

        if len(type_user) <= 3:
            return render_template(
                "index.html",
                error="Sorry! Please input more than three characters for the type of establishment.",
                found=False,
            )

        # Validate and process the location
        zip_code = get_zip_code(location_user)
        if not zip_code:
            return render_template(
                "index.html",
                error="Sorry! Unable to determine a valid zip code from the provided location.",
                found=False,
            )

        # Redirect to results page
        return redirect(url_for("results", location=zip_code, type=type_user))

    return render_template("index.html", found=False)


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    input_text = request.args.get("input", "")

    if len(input_text) < 3:
        return jsonify([])

    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": input_text,
        "types": "(regions)",
        "components": "country:us",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params)
    results = response.json().get("predictions", [])

    suggestions = [
        {"description": result["description"], "place_id": result["place_id"]}
        for result in results
    ]

    return jsonify(suggestions)


@app.route("/get_details", methods=["GET"])
def get_details():
    place_id = request.args.get("place_id", "")

    if not place_id:
        return jsonify({"error": "No place_id provided"})

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "address_component",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params)
    result = response.json().get("result", {})

    zip_code = next(
        (
            component["long_name"]
            for component in result.get("address_components", [])
            if "postal_code" in component["types"]
        ),
        None,
    )

    return jsonify({"zip_code": zip_code})


def get_zip_code(location):
    # First, check if the location is already a valid zip code
    search = get_search_engine()
    if len(location) == 5 and search.by_zipcode(location):
        return location

    # If not, try to get the zip code from Google Places API
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": location,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params)
    result = response.json().get("candidates", [])

    if result:
        place_id = result[0]["place_id"]
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "address_component",
            "key": GOOGLE_API_KEY,
        }

        details_response = requests.get(details_url, params=details_params)
        details_result = details_response.json().get("result", {})

        zip_code = next(
            (
                component["long_name"]
                for component in details_result.get("address_components", [])
                if "postal_code" in component["types"]
            ),
            None,
        )

        return zip_code

    return None


# TODO: optimize pagination
@app.route("/results")
def results():
    page = request.args.get("page", 1, type=int)
    location = request.args.get("location")
    type = request.args.get("type")  # This is the 'term' in Yelp API context

    items_per_page = 9  # 3x3 grid

    businesses = fetch_businesses(type, location, page, items_per_page + 1)

    has_next = len(businesses) > items_per_page
    businesses = businesses[:items_per_page]  # Limit to items_per_page

    total_results = get_total_results(type, location)
    total_pages = (total_results + items_per_page - 1) // items_per_page

    return render_template(
        "results.html",
        businesses=businesses,
        current_page=page,
        total_pages=total_pages,
        location=location,
        type=type,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "error.html", error_message="Woops, this page does not exist (404)"
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed(e):
    return (
        render_template(
            "error.html",
            error_message="That request method is not permitted on this page (405)",
        ),
        405,
    )


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_message=f"500 {e}"), 500


@app.route("/slashboard/")
def slashboard():
    try:
        return render_template("index.html")
    except Exception as e:
        return render_template("error.html", error_message=f"500 {e}"), 500


# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
