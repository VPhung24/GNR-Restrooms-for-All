from __future__ import print_function

import os
import argparse
import requests
import sys
from urllib.error import HTTPError
from urllib.parse import quote

API_KEY = os.getenv("API_KEY")

# API constants
API_HOST = "https://api.yelp.com"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"  # Business ID will come after slash.

# Defaults for our simple example
DEFAULT_TERM = "dinner"
DEFAULT_LOCATION = "San Francisco, CA"
SEARCH_LIMIT = 6


def request(host, path, api_key, url_params=None):
    """
    Makes a request to the Yelp API and returns the response.
    """
    url_params = url_params or {}
    url = f"{host}{quote(path.encode('utf8'))}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, params=url_params)
    response.raise_for_status()
    return response.json()


def search(api_key, term, location):
    """
    Queries the Yelp API for businesses by search term and location.
    """
    url_params = {
        "term": term.replace(" ", "+"),
        "location": location.replace(" ", "+"),
        "limit": SEARCH_LIMIT,
        "attributes": "gender_neutral_restrooms",
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params)


def get_business(api_key, business_id):
    """
    Queries the Yelp API by business ID.
    """
    business_path = f"{BUSINESS_PATH}{business_id}"
    return request(API_HOST, business_path, api_key)


def query_api(term, location):
    """
    Queries the API with the given term and location.
    """
    response = search(API_KEY, term, location)
    return response


def fetch_businesses(term, location, page, items_per_page):
    """
    Fetches businesses from Yelp API with pagination support.
    """
    url_params = {
        "term": term.replace(" ", "+"),
        "location": location.replace(" ", "+"),
        "limit": items_per_page,
        "offset": (page - 1) * items_per_page,
        "attributes": "gender_neutral_restrooms",
    }
    response = request(API_HOST, SEARCH_PATH, API_KEY, url_params)

    businesses = response.get("businesses", [])

    # Format the business data as needed
    formatted_businesses = []
    for business in businesses:
        formatted_business = {
            "url": business["url"],
            "image_url": business["image_url"],
            "name": business["name"],
            "location": ", ".join(business["location"]["display_address"]),
            "rating": business["rating"],
            "review_count": business["review_count"],
        }
        formatted_businesses.append(formatted_business)

    return formatted_businesses


def get_total_results(term, location):
    """
    Gets the total number of results for the given search term and location.
    """
    url_params = {
        "term": term.replace(" ", "+"),
        "location": location.replace(" ", "+"),
        "attributes": "gender_neutral_restrooms",
    }
    response = request(API_HOST, SEARCH_PATH, API_KEY, url_params)

    return response.get("total", 0)
