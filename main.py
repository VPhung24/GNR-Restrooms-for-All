from flask_bootstrap import Bootstrap4
from json import loads
import os
from flask import Flask, render_template, request
import yelp_fusion_helper
from http import *
from uszipcode import SearchEngine

app = Flask(__name__, template_folder='templates', static_folder='static')
bootstrap = Bootstrap4(app)


@app.route("/", methods=["GET", "POST"])
def main_route():
    if request.method == "POST":
        location_user = request.form['location']
        type_user = request.form['type']
        search = SearchEngine()
        # quick refactor: validation should be done on the front end
        if (len(location_user) == 0) or (len(type_user) == 0):
            found = False
            error = "Please provide inputs."
            return render_template("index.html", error=error, found=found)
        elif ((not len(location_user) == 5) or (bool(search.by_zipcode(location_user)) == False)):
            found = False
            error = "Sorry! Please input a vaild zipcode."
            return render_template("index.html", error=error, found=found)
        elif (len(type_user) <= 3):
            found = False
            error = "Sorry! Please input more than three characters for type of establishment"
            return render_template("index.html", error=error, found=found)
        else:
            v = yelp_fusion_helper.query_api(type_user, location_user)
            v = v["businesses"]
            if len(v) > 1:
                return render_template("index.html", found=True, data=v)
            else:
                error = "Sorry! We don't know of any Gender Neutral Restrooms in your area of the type you specified. Please try again!"
                return render_template("index.html", found=False, error=error)
    else:
        return render_template("index.html", found=False)


app.secret_key = 'GNR for life'


@app.route("/about/")
def about_route():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    options = {
        "edit": False
    }
    return render_template("404.html", **options)


@app.errorhandler(405)
def method_not_found(e):
    options = {
        "edit": False
    }
    return render_template("405.html", **options)


@app.route('/slashboard/')
def slashboard():
    try:
        return render_template("index.html")
    except Exception as e:
        return render_template("500.html", error=e)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
