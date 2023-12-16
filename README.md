# Finance
A finance website where the user can login with their own credentials, buy and sell stocks.

## About the Project 📖
The project is a web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you "buy" and "sell" stocks by querying for stocks’ prices.

The project makes use of HTML and Jinja web template engine.

## Built with ⌨️
+ HTML/CSS
+ SQL
+ Python

## Program and Execute Project 🗔
### Requirements 🗉
Programming/markup languages needed:
+ HTML/CSS
+ SQL
+ Python

Frameworks used:
+ Bootstrap - CSS
+ Flask (Jinja) - Python

Libraries:
+ CS50 - Python

The CS50 Python library can be installed with the `pip` command.

```
pip3 install CS50
```

Otherwise, you can manually install the libraries from [CS50 Python Libraries GitHub](https://github.com/cs50/python-cs50) and include them in the repository.

### Execute ▶️
Start by cloning the repository in your local machine
```
git clone https://github.com/ErTucci674/cs50-finance.git
```

To run the program, on the command prompt, execute the code:
```
flask run
```

This will start and execute the code stored in `app.py` and give you a URL to access the _local website_.

## Files and Code 🗐
### Folders 📁
The repository includes two main folders, `static` and `templates`. In the latter, all the pages layouts are stored. In the _static_ folder, the HTML style sheet and icon are icluded instead.

### Main File ⚡
The `app.py` file controls everything that occurs on the website.

Before running the file, a _Flask_ object is create so all the _Flask_ functionalities can be accessed through a variable called _app_.

```python
app = Flask(__name__)
```

Depending whether the user logs in or not, different pages are loaded. When the program is ran for the first time, the `login.html` page is shown by the following function:

```python
@app.route("/login", methods=["GET", "POST"])
```

Otherwise a 'default' page is open, `index.html`, which makes sure logged in first, so no one can access that page by just tiping the corresponding URL.

```python
@app.route("/")
@login_required
```

The website allows multiple users' data to be separately stored. All the data is managed with _SQL_ tables which are stored in `finance.db`, a _Database File_. The CS50 libraries include _SQL_ functionalities that can be controlled with _Python_. These functionalities are accessed through the _db_ object.

```python
db = SQL("sqlite:///finance.db")
```

### Default Pages Layout 📄
All pages contain the a navigation bar on the top of the window with the logo as well. To avoid repeatition in the code, a default page setup is written and stored in the `layout.html` file.

```html
{% extends "layout.html" %}

{% block title %}
    Log In
{% endblock %}

{% block main %}
    <form action="/login" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" id="username" name="username" placeholder="Username" type="text">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" id="password" name="password" placeholder="Password" type="password">
        </div>
        <button class="btn btn-primary" type="submit">Log In</button>
    </form>
{% endblock %}
```

The code above is taken from the `login.html` file. The `{% extends "layout.html" %}` takes the entirety of the code in the `layout.html` file where the login content will be added and placed together on the window.

## Aknowledgements 🤝
Harvard University Online Course (edx50) - [Introduction to Computer Science](https://www.edx.org/learn/computer-science/harvard-university-cs50-s-introduction-to-computer-science)

## Licence 🖋️
This project is licensed under the terms of the Attribution-NonCommercial-ShareAlike 4.0 International.
