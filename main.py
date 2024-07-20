from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap4
from uszipcode import SearchEngine
import yelp_fusion_helper
import os
import threading

app = Flask(__name__, template_folder="templates", static_folder="static")
app.url_map.strict_slashes = False
bootstrap = Bootstrap4(app)
app.secret_key = "GNR for life"

# Thread-local storage for the SearchEngine instance
search_engine_local = threading.local()


def get_search_engine():
    if not hasattr(search_engine_local, "engine"):
        search_engine_local.engine = SearchEngine()
    return search_engine_local.engine


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


@app.route("/", methods=["GET", "POST"])
def main_route():
    if request.method == "POST":
        location_user = request.form["location"]
        type_user = request.form["type"]

        # Front-end validation should ideally handle this
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

        # Query Yelp API
        result = yelp_fusion_helper.query_api(type_user, location_user)
        businesses = result.get("businesses", [])

        if businesses:
            return render_template("index.html", found=True, data=businesses)
        else:
            error = "Sorry! We don't know of any Gender Neutral Restrooms in your area of the type you specified. Please try again!"
            return render_template("index.html", found=False, error=error)

    return render_template("index.html", found=False)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
