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


def main():
    parser = argparse.ArgumentParser(description="Yelp API search example")
    parser.add_argument(
        "-q",
        "--term",
        dest="term",
        default=DEFAULT_TERM,
        type=str,
        help="Search term (default: %(default)s)",
    )
    parser.add_argument(
        "-l",
        "--location",
        dest="location",
        default=DEFAULT_LOCATION,
        type=str,
        help="Search location (default: %(default)s)",
    )

    args = parser.parse_args()

    try:
        response = query_api(args.term, args.location)
        print(response)
    except HTTPError as error:
        sys.exit(
            f"Encountered HTTP error {error.code} on {error.url}:\n{error.read()}\nAbort program."
        )


if __name__ == "__main__":
    main()
