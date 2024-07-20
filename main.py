from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from uszipcode import SearchEngine
from yelp_fusion_helper import fetch_businesses, get_total_results
import os
import threading

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

        search = get_search_engine()
        if not (len(location_user) == 5 and search.by_zipcode(location_user)):
            return render_template(
                "index.html", error="Sorry! Please input a valid zipcode.", found=False
            )

        if len(type_user) <= 3:
            return render_template(
                "index.html",
                error="Sorry! Please input more than three characters for the type of establishment.",
                found=False,
            )

        # Redirect to results page
        return redirect(url_for("results", location=location_user, type=type_user))

    return render_template("index.html", found=False)


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
