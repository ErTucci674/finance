
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

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime
import pytz

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session.get("user_id")

    cash = usd(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"])
    owned = db.execute("SELECT symbol, shares FROM own WHERE user_id = ? ORDER BY symbol", user_id)

    # Store all the shares the user bought, the symbols and total price and display them on a new page
    stocks = []
    tmp_stock = {}
    total = 0
    for own in owned:
        symbol = own["symbol"]
        price = lookup(symbol)["price"]
        shares = own["shares"]

        tmp_stock["symbol"] = symbol
        tmp_stock["price"] = usd(price)
        tmp_stock["shares"] = shares

        price_calc = float(price) * float(shares)
        tmp_stock["total"] = usd(price_calc)

        stocks.append(tmp_stock.copy())
        total += price_calc

    return render_template("index.html", cash=cash, stocks=stocks, total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Check if all tabs have been filled in
        if not symbol or not shares:
            return apology("Please, fill in the blanks. You'll make it easier for the both of us")

        stock = lookup(symbol)

        # Check if the symbol exists
        if not stock:
            return apology("Sorry, the inserted symbol does not exist")

        # Check if inserted shares is a positive integer
        try:
            int_shares = int(shares)
            if int_shares <= 0:
                return apology("A positive integer must be inserted for the shares")
        except:
            return apology("Insert a valid number for the shares")

        # Calculate total cost
        tot_price = float(stock["price"]) * int_shares

        # Check if the user owns enough money to buy the shares
        user_id = session.get("user_id")
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        cash = float(user[0]["cash"])
        if cash < tot_price:
            return apology(f"You need other {usd(tot_price - cash)} to buy the selected number of shares")

        # Check when the purchase has been done
        purchase_date = datetime.datetime.now(pytz.timezone("US/Eastern"))

        # Add the purchase details into the table 'own'
        # If shares for the same stock have already been bought, add them to the existing one
        symbol = symbol.upper()
        own = db.execute("SELECT * FROM own WHERE user_id = ? AND symbol = ?", user_id, symbol)

        if not own:
            db.execute("INSERT INTO own(user_id, symbol, shares, total) VALUES(?, ?, ?, ?)", user_id, stock["symbol"], shares, tot_price)
        else:
            old_shares = int(own[0]["shares"])
            old_total = float(own[0]["total"])
            new_shares = old_shares + int_shares
            new_total = old_total + tot_price
            db.execute("UPDATE own SET shares = ?, total = ? WHERE user_id = ? AND symbol = ?", new_shares, new_total, user_id, symbol)

        # Subtract money from user's cash
        new_cash = cash - tot_price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)

        # Record the purchasement
        db.execute("INSERT INTO history(user_id, symbol, shares, money, action, date) VALUES(?, ?, ?, ?, ?, ?)", user_id, symbol, shares, usd(tot_price), "BOUGHT", purchase_date)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    records = db.execute("SELECT * FROM history WHERE user_id = ?", session.get("user_id"))
    return render_template("history.html", records=records)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Reload the page if no input is inserted
        if not symbol:
            return apology("You must insert a symbol")

        stock = lookup(symbol)

        # Check if the symbol (stock) exists
        if not stock:
            return apology("The inserted stock symbol does not exist")
        else:
            return render_template(
                "quoted.html",
                name=stock["name"],
                price=usd(stock["price"]),
                symbol=stock["symbol"],
            )

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Check that the username tab has been filled in and if it doesn't exist already
        if not username:
            return apology(
                "You must insert a username! How am I supposed to register you otherwise?"
            )
        elif user and username == user[0]["username"]:
            return apology("My deepest apologies. This username has already been taken")

        # Check that the password and confirmation tabs have been filled in and if they match
        if not password or not confirmation:
            return apology("I suggest you to protect your account with a password")
        elif password != confirmation:
            return apology("Better re-type the confirming password (they don't match)")

        # Encrypt password
        hashed = generate_password_hash(password, method="pbkdf2", salt_length=16)

        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, hashed)

        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session.get("user_id")
    owns = db.execute("SELECT symbol, shares FROM own WHERE user_id = ? ORDER BY symbol", user_id)

    # Get all the shares symbols the user bought
    symbols = []
    for own in owns:
        symbols.append(own["symbol"])

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Check if user inserted inputs
        if not symbol or not shares:
            return apology("Please, fill in the blank tabs. You would make it easier for the both of us")

        # Check if user owns the selected
        if symbol not in symbols:
            return apology(f"You currently do not own any shares of {symbol}")

        # Check if shares is a positive integer
        try:
            int_shares = int(shares)
            if int_shares <= 0:
                return apology("The shares value must be a positive integer")
        except:
            return apology("You can start by inserting a number in the shares tab")

        for own in owns:
            if own["symbol"] == symbol:
                if int(own["shares"]) >= int_shares:
                    # Sell shares
                    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
                    earning = lookup(symbol)["price"] * int_shares
                    new_cash = float(cash) + float(earning)

                    # Give user the earning
                    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)

                    # Check and remove the number of shares that have been sold
                    # if all shares have been sold, remove row from 'own' table
                    old_shares = int(own["shares"])
                    new_shares = old_shares - int_shares

                    if new_shares == 0:
                        db.execute("DELETE FROM own WHERE user_id = ? AND symbol = ?", user_id, symbol)
                    else:
                        db.execute("UPDATE own SET shares = ? WHERE user_id = ? AND symbol = ?", new_shares, user_id, symbol)

                    # Check when the selling has been done
                    selling_date = datetime.datetime.now(pytz.timezone("US/Eastern"))

                    # Record the selling
                    db.execute("INSERT INTO history(user_id, symbol, shares, money, action, date) VALUES(?, ?, ?, ?, ?, ?)", user_id, symbol, shares, usd(earning), "SOLD", selling_date)

                else:
                    return apology("You don't currently own the selected amount of shares")

        return redirect("/")
    else:
        return render_template("sell.html", symbols=symbols)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change user's password"""
    if request.method == "POST":
        old = request.form.get("old")
        new = request.form.get("new")
        confirmation = request.form.get("confirmation")

        user_id = session.get("user_id")
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

        # Check if all tabs have been filled in
        if not old or not new or not confirmation:
            return apology("Please, fill in all the tabs so we can carry on")

        # Check if Old Password matches the one that is currently used
        if not check_password_hash(user["hash"], old):
            return apology("Old Password does not match")

        # Check if confimation matches
        if new != confirmation:
            return apology("The new password does not match the confirming one")

        # Encrypt password
        hashed = generate_password_hash(new, method="pbkdf2", salt_length=16)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed, user_id)

        return redirect("/")
    else:
        return render_template("password.html")
