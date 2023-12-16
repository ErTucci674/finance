#  Finance
#  
#  Copyright (c) 2023 Alessandro Amatucci Girlanda
#  
#  This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike
#  4.0 International License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
#  Commons, PO Box 1866, Mountain View, CA 94042, USA.
#  
#  You are free to:
#    - Share — copy and redistribute the material in any medium or format
#    - Adapt — remix, transform, and build upon the material
# 
#  Under the following terms:
#    - Attribution — You must give appropriate credit, provide a link to the license, and
#                   indicate if changes were made. You may do so in any reasonable manner,
#                   but not in any way that suggests the licensor endorses you or your use.
#    - NonCommercial — You may not use the material for commercial purposes.
#    - ShareAlike — If you remix, transform, or build upon the material, you must
#                   distribute your contributions under the same license as the original.
# 
#  No additional restrictions — You may not apply legal terms or technological measures
#  that legally restrict others from doing anything the license permits.
#
#  Acknowledgment:
#  This file includes classes developed by Harvard University CS50.

import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={"User-Agent": "python-requests", "Accept": "*/*"})
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        return {
            "name": symbol,
            "price": price,
            "symbol": symbol
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
