# Django User Management

- [Django User Management](#django-user-management)
  - [Summary](#summary)
  - [Set up a Django Project](#set-up-a-django-project)
      - [activate virtual environment](#activate-virtual-environment)
      - [Start the project](#start-the-project)
  - [Create a Dashboard View](#create-a-dashboard-view)
  - [Work with Django User Management](#work-with-django-user-management)
  - [Create a Login Page](#create-a-login-page)
  - [Create a Logout Page](#create-a-logout-page)
  - [Change Password](#change-password)
  - [Send Password Reset Links](#send-password-reset-links)
  - [Reset Passwords](#reset-passwords)
  - [Change Email Templates](#change-email-templates)
  - [Register New Users](#register-new-users)
  - [Send Emails to the Outside World](#send-emails-to-the-outside-world)
  - [Login With Github](#login-with-github)
  - [Select Authentication Backend](#select-authentication-backend)

## Summary

![final-view](final-app.gif)

Learning Goal:

- Application with user login, registration, reset and change password feature
- Edit the default django templates responsible for user management
- Set password dreset emails to actual email addresses
- Authenticate using an external service

## Set up a Django Project

#### activate virtual environment

```shell
py -m venv venv
venv\Scripts\activate or source venv\bin\activate
```

[optional] upgrade pip

```shell
py -m pip install --upgrade pip
```

install django

```shell
pip install django
```

#### Start the project

```shell
django-admin startproject awesome_website
cd awesome_website
python manage.py startapp users
```

Note: we have created app named `users` not `user`

Add `users` to the `INSTALLED_APPS` in `awesome_website/awesome_website/settings.py`

```python
INSTALLED_APPS = [
    "users",
    # ...,
]
```

Run Data migrations. The following commands migrate all models in our apps to the database

```shell
python manage.py migrate
python manage.py runserver
```

Note: `cd` into the directory that has `manage.py`. Our `manage.py` is at `[root]/awesome_website/`, where root is the main directory.

So that we should not need to set up a strong password everytime, we will comment out password validators in `awesome_website/awesome_website/settings.py`

```python
AUTH_PASSWORD_VALIDATORS = [
    # {
    #     "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    # },
]
```

Note: this is to make it easy for the development phase only. Enable these features when going to production.

Create a admin user

```shell
python manage.py createsuperuser
```

## Create a Dashboard View

All template files will be kept inside `awesome_website/users/templates/`
The structure of the project will look like

```
awesome_website/
│
├── awesome_website/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/
│   │
│   ├── migrations/
│   │   └── __init__.py
│   │
│   ├── templates/
│   │   │
│   │   ├── registration/  ← Templates used by Django user management
│   │   │
│   │   ├── users/  ← Other templates of your application
│   │   │
│   │   └── base.html  ← The base template of your application
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── db.sqlite3
└── manage.py
```

Create a base template called `base.html` in `users/templates/`:

```html
<h1>Welcome to Awesome Website</h1>
{% block content %} {% endblock %}
```

Other templates are going to use `{%block content %} {% endblock %}` to fill up their contents.

create another template `users/templates/dashboard.html`:

```html
{% extends 'base.html' %} {% block content %} Hello, {{ user.username |
default:'Guest' }}! {% endblock %}
```

If the user isn't logged in, Django will set the user variable using an [AnnonymousUser](https://docs.djangoproject.com/en/3.0/ref/contrib/auth/#anonymoususer-object) object, which is always empty. So, the dashboard will show `Hello, Guest!`

Set up views for the template to work:

```python
from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")
```

Create a `users/urls.py` and add the following:

```python
from django.conf.urls import url
from users.views import dashboard

urlpatterns = [
    url(r"^dashboard/", dashboard, name="dashboard"),
]
```

Now, add the application's URL to the main project's URL

```python
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r"^", include("users.urls")),
    url(r"^admin/", admin.site.urls),
]
```

Run the application `python manage.py runserver` and visit `localhost:8000/dashboard/` or `127.0.0.1:8000/dashboard/`.
Note, `localhost:8000` will give us a page not found error, and it okay because we have not set up any template for `/`.

Go to `localhost:8000/admin/` and login as the admin user. Then, visit `localhost:8000/dashboard/` again. Do you see a change?

## Work with Django User Management

Django has a lot of user management-related resources that can handle login, logout, password change, and password reset.
Templates needs to supplied by us though.

Add the URLs provided by the Django authentication system in `users/urls.py`:

```python
from django.conf.urls import include, url
# from ...

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls")),
    # url(r"^dashboard/", dashboard, name="dashboard"),
]
```

This will give us access to the following URLs:

- `accounts/login/` is used to log a user into the application. Refer to it by the name `login`
- `accounts/logout/` is used to log a user out of the application. Refer to it by the name `logout`
- `accounts/password_change/` is used to change a password. Refer to it by the name `password_change`
- `accounts/password_change/done` is used to show a confirmation that a password was changed. Refer to it by the name `password_change_done`.
- `accounts/password_reset` is used to request an email with a password reset link. Refer to it by the name `password_reset`
- `accounts/password_reset/done` is used to show a confirmation that a password reset email was sent. Refer to it by the name `password_reset_done`.
- `accounts/reset/<uidb64>/<token>/` is used to set a new password using a password reset link. Refer to it by the name `password_reset_confirm`.
- `accounts/reset/done/` is used to show a confirmation that a password was reset. Refer to it by the name `password_reset_complete`.

## Create a Login Page

For login page, Django will try to use a template called `registration/login.html`.
So, create the file `users/templates/registration/login.html`

```html
{% extends 'base.html' %} {% block content %}
<h2>Login</h2>

<form method="post">
  {% csrf_token %} {{ form.as_p }}
  <input type="submit" value="Login" />
</form>

<a href="{% url 'dashboard' %}">Back to dashboard</a>
{% endblock %}
```

Here, `form` is just a variable passed through `context`. Django uses this dictionary `context` to pass data to templates while rendering it. USing `{{ form.as_p }}` will render a series of HTML paragraphs which will look nicer than just `{{ form }}`
Visit the [link](https://www.squarefree.com/securitytips/web-developers.html#CSRF) to learn about cross-site request forgery (CRSF) token, `csrf_token`.

Add some more CSS to improve the looks of `users/templates/base.html`:

```html
<style>
  label,
  input {
    display: block;
  }
  span.helptext {
    display: none;
  }
</style>

<h1>Welcome to Awesome Website</h1>
<!-- ... -->
```

After logging in, we will get redirected to `/accounts/profile` which does not exist yet. So, we might see `Page not found` error.

The address `/accounts/profile/` is a default destination for users after a successful login.
Let's define another redirect url. In `awesome_website/settings.py` add the following at the end:

```python
LOGIN_REDIRECT_URL = "dashboard"
```

This should fix the error.

## Create a Logout Page

Let's define a redirect url for logout too. In `awesome_website/settings.py` add the following line at the end:

```python
LOGOUT_REDIRECT_URL = "dashboard"
```

Let's add logout link to the dashboard and a link to login as well.
In `users/templates/users/dashboard.html` add:

```html
{% extends 'base.html' %} {% block content %} Hello, {{ user.username | default:
'Guest' }}!

<div>
  {% if user.is_authenticated %}
  <a href="{% url 'logout' %}">Logout</a>
  {% else %}
  <a href="{% url 'login' %}">Login</a> {% endif %}
</div>
{% endblock %}
```

## Change Password

Django needs two templates to make this work:

1. `registration/password_change_form.html` to display the password change form
2. `registration/password_change_done.html` to show a confirmation that the password was successfully changed

Create `registration/password_change_form.html`:

```html
{% extends 'base.html' %} {% block content %}
<h2>Change Password</h2>

<form method="post">
  {% csrf_token %} {{ form.as_p }}
  <input type="submit" value="Change" />
</form>
<a href="{% url 'dashboard' %}">Back to Dashboard</a>
{% endblock %}
```

This form look almost the same as login template. Howevedr, this time, Django will put a password change form here, not a login form, so that browser will display it differently.

Create `registration/password_change_done.html`

```html
{% extends 'base.html' %} {% block content %}
<h2>Password changed</h2>

<a href="{% url 'dashboard' %}">Back to Dashboard</a>
{% endblock %}
```

This page will reassure the user that the password change was successful and let them go back to the dashboard.

Finally, add the link to the password change form at `users/templates/dashboard.html`:

```html
<!-- ... -->
{% if user.is_authenticated %}
<!-- ... -->
<a href="{% url 'password_change' %}">Change Password</a>
<!-- add this -->
{% else %}
<!-- ... --->
```

Test the `Change Password` link when logged in. It should work.
If you log out and a try to visit `localhost:8000/accounts/password_change/` directly, Django will redirect you to the login page.

## Send Password Reset Links

This functionality is a bit more complicated because, in oder to deliver password reset links, Django needs to send emails.
For this tutorial however, we will set a local test server to confirm that the emails are sent.
In the terminal run the command:

```shell
python -m smtpd -n -c DebuggingServer localhost:1025
```

This will start the simple SMTP server at `http://localhost:1025`. It won't send any emails to the actual email addresses. Instead, it'll show the content of the messages in the command line.

All we need to do now is, let Django know that we are using it by adding the following lines at the end of the settings file `awesome_website/settings.py`:

```python
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
```

Now, Django needs two templates for sending password reset links:

1. `registration/password_reset_form.html` to display the form used to request a password reset email
2. `registration/password_reset_done.html` to show a confirmation that a password reset email was sent

Start by creating `registration/password_reset_form.html`:

```html
{% extends 'base.html' %} {% block content %}
<h2>Send password reset link</h2>

<form method="post">
  {% csrf_token %} {{ form.as_p }}
  <input type="submit" value="Reset" />
</form>

<a href="{% url 'dashboard' %}">Back to Dashboard</a>
{% endblock %}
```

Add the confirmation template `registration/password_reset_done.html`:

```html
{% extends 'base.html' %} {% block content %}
<h2>Password reset link sent</h2>

<a href="{% url 'login' %}">Back to login</a>
{% endblock %}
```

Also, add a link to the password reset form on the login page `users/templates/registration/login.html`

```html
{% extends 'base.html' %}

<!-- ... -->

<!-- <a href="... -->
<a href="{% url 'password_reset' %}">Reset Password</a>
{% endblock %}
```

If you hit `Reset Password` from `http://localhost/account/login` and enter the admin email, you will get the following message in the server

```shell
---------- MESSAGE FOLLOWS ----------
b'Content-Type: text/plain; charset="utf-8"'
b'MIME-Version: 1.0'
b'Content-Transfer-Encoding: 8bit'
b'Subject: Password reset on localhost:8000'
b'From: webmaster@localhost'
b'To: <theusername>@gmail.com'
b'Date: Thu, 24 Dec 2020 13:26:51 -0000'
b'Message-ID: <160881641196.14116.9954328995282593482@DESKTOP-7V1GTOQ.lan1>'
b'X-Peer: ::1'
b''
b''
b"You're receiving this email because you requested a password reset for your user account at localhost:8000."
b''
b'Please go to the following page and choose a new password:'
b''
b'http://localhost:8000/accounts/reset/MQ/afdm4r-bc23b743255cfff65f6298882687a5dd/'
b''
b'Your username, in case you\xe2\x80\x99ve forgotten: root'
b''
b'Thanks for using our site!'
b''
b'The localhost:8000 team'

```

## Reset Passwords

Password reset emails sent by Django contains a link that can be used to reset the password. To handle the link correctly, Djnago needs two more templates:

1. `registration/password_reset_confirm.html` to display the actual password reset form
2. `registration/password_reset_complete.html` to show a confirmation that a password was reset

Create `registration/password_reset_confirm.html`:

```html
{% extends 'base.html' %} {% block content %}
<h2>Confirm Password Reset</h2>

<form method="post">
  {% csrf_token %} {{ form.as_p }}
  <input type="submit" value="Confirm" />
</form>
{% endblock %}
```

Add a confirmation template at `users/templates/registration/password_reset_complete.html`:

```html
{% extends 'base.html' %} {% block content %}
<h2>Password Reset Complete</h2>

<a href="{% url 'login' %}">Back to login</a>
{% endblock %}
```

## Change Email Templates

We need to create two files to change the email templates:

1. `registration/password_reset_email.html` determines the body of the email
2. `registration/password_reset_subject.txt` determines the subject of the email
   While we will be changing a few, Django provides a lot of other [variables](https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.PasswordResetView) that we can use to compose our own messages.

Create `users/templates/registration/password_reset_email.html`

```html
Someone requested to reset password for your email {{ email }}. Follow the link
below to reset the password: {{ protocol }}://{{ domain }}{% url
'password_reset_confirm' uidb64=uid token=token %}
```

Add `Reset Password` or any text you like in `users/templates/registration/password_reset_subject.txt`

Try resetting password again and you will see that the subject and the email message has changed.

## Register New Users

Django doesn't provide user registration form out of the box. So we need to add our own.
Django, however, provides [UserCreationForm](https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.forms.UserCreationForm). `UserCreationForm` provides all necessary fields to create the user except the email form. So, what we will do is use almost the entire UserCreationForm and we will add one more `email` field.

Create `users/forms.py` and add a custom form there:

```python
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

```

Here, our class `CustomUserCreationForm` extends Django's `UserCreationForm`. The inner class `Meta` keeps additional information about the form and in this case extends `UserCreationForm.Meta`, so almost everything from Django's form will be reused. We will just add `email` field.

Now that the form is ready, create a new view called `register`:

```python
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm

def dashboard(request):
    # ...

def register(request):
    if request.method == "GET":
        return render(
            request, "register.html",
            {"form": CustomUserCreationForm }
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))

```

`request.method=="GET"` checks if the request is 'GET'. It renders `users/register.html` if it is the case. The last argument of `render()` is a context, which contains `"form": CustomUserCreationForm`
If the form is submitted, the view will be accessed by a `POST` method. In that case, Django will attempt to create a user. A new `CustomUserCreationForm` is created using the values submitted to the form through `request.POST` object.
If the form inputs are valid, then a new user is created using `form.save()`. The user is logged in using `login()` and user redirected to `dashboard`.

Add URL for the registration view:

```python
from django.conf.urls import include, url
from user.views import dashboard, register

urlpatterns = [
    # ...,
    # ...,
    url(r"^register/", register, name="register"),
]

```

Finally, add a link to the registration form on the login page `users/templates/registration/login.html`:

```html
<!-- ... -->

<a href="{% url 'register' %}">Register</a>
{% endblock %}
```

Create a register template at `users/templates/register.html`:

```html
{% extends 'base.html' %} {% block content %}
<h2>Register</h2>

<form method="post">
  {% csrf_token %} {{ form }}
  <input type="submit" value="Register" />
</form>

<a href="{% url 'login' %}">Back to Login</a>
{% endblock %}
```

Add link to registration at `users/templates/registration/login.html`

```html
<!--... -->
<a href="{% url 'register' %}">Register</a>
{% endblock %}
```

## Send Emails to the Outside World

Go to [mailgun](https://www.mailgun.com/) and create an account.
Go to Sending, click on sandbox domain. Choose SMTP: Scroll down and collect the following information:

1. SMTP hostname
2. Port
3. Username
4. Default Password

In `awesome_website/settings.py` add the following:

```python
EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
```

Note: I have used `os.getenv("XXXX")` in my `settings.py`. It works the same way as `os.environ.get("XXXX")`.

We have set the values for `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` to some variables stored in the os environment.
Let's set those environment variables:
Windows in Powershell:

```shell
$env:EMAIL_HOST_USER="the username we collected from mailgun"
$env:EMAIL_HOST_PASSWORD="the password we collected from mailgun"
```

You can check the value of the variables for example by doing `echo $EMAIL_HOST_USER`. The same command will probably work for linux/mac too. If it returns a value then, you know that the value has been store in the environment. If it doesn't return any value, there is a problem.

Linux/Mac:

```shell
export EMAIL_HOST_USER="the username we collected from mailgun"
export EMAIL_HOST_PASSWORD="the password we collected from mailgun"
```

Visit `http://localhost:8000/accounts/password_reset/` and enter a email address you have access to and is also in the data base to test if it works.

## Login With Github

We will use the Python module `social-auth-app-django` for this authentication. Read more about it [here](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html).

Set up social authentication

```shell
pip install social-auth-app-django
```

Add it to the `INSTALLED_APPS` in `awesome_website/settings.py`

```python
INSTALLED_APPS = [
  "users",
  "social_django",
  # " ...",
]
```

Add the following context processors to `TEMPLATES` at `awesome_website/settings.py`

```python
TEMPLATES =[
  {
    # ...
    "OPTIONS":{
      "context_processors":[
        # ...,
        "social_django.context_processors.backends",
        "social_django.context_processors.login_redirect",
      ]
    }
  }
]
```

Apply migrations:

```shell
python manage.py migrate
```

Include the social authentication URLs in the application at `users/urls.py`

```python
# from ...

urlpatterns = [
  # ...,
  url(r"^oauth/", include("social_django.urls")),
  # ...,
]
```

Note: `^` Caret - matches the start of the string.

By default, Django settings don't specify authentication backends, and the default backend used by Django is `django.contrib.auth.backends.ModelBackend`. So to use, social authentication, we have to create a new value in settings: add the following in `awesome_website/settings.py`:

```python
AUTHENTICATION_BACKENDS = [
  "django.contrib.auth.backends.ModelBackend", # default one used by django for standard users
  "social_core.backends.github.GithubOAuth2", # used for Github and other Social logins
]
```

Note: As you get into bigger projects, having to use two separate authentication backends might become unreliable. That's why there is a package like [`django-allauth`](https://django-allauth.readthedocs.io/en/latest/installation.html) which attempts to combine both standard user login and social login.

Lastly, lets add link to the Github login on our page `users/templates/registration/login.html`

```html
{% extends 'base.html' %}

<!--... -->

<a href="{% url 'social:begin' 'github' %}">Login with GitHub</a>
<!--<a href=... -->
{% endblock %}
```

Now, we need to create a Github application. Go to the [link](https://github.com/settings/applications/new)
Fill up the fields with:

```
Application Name: "name of your choice"
Homepage URL: "http://localhost:8000/" or "http://127.0.0.1:8000/"
Authorization callback URL: "http://localhost:8000/oauth/complete/github/" or "http://127.0.0.1:8000/oauth/complete/github/"
```

Click `Generate a new client secret` to generate a github key.
Record `Client ID` and `Client secret`

Add the following lines in `awesome_website/settings.py`

```python
SOCIAL_AUTH_GITHUB_KEY = os.environ.get("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get("SOCIAL_AUTH_GITHUB_SECRET")
```

Pass the values for `Client ID` and `Client Secret` through the environment
Windows

```shell
$env:SOCIAL_AUTH_GITHUB_KEY="the ID we collected from github"
$env:SOCIAL_AUTH_GITHUB_SECRET="the secret key we collected from github"
```

Linux/Mac:

```shell
export SOCIAL_AUTH_GITHUB_KEY="the ID we collected from github"
export SOCIAL_AUTH_GITHUB_SECRET="the secret key we collected from github"
```

After adding, start the server `python manage.py runserver`.

Try signing in with Github. It should work.

But with this github signin, we will not be authorized to sign into admin dashboard. If we try to access `localhost:8000/admin/`, the following error will arise

```
You are authenticated as [github-username], but are not authorized to access this page. Would you like to login to a different account?
```

If we sign into the admin dashboard with a admin account, we will see that a new user has been added with a github username, but there is no password and email.

Here, by enabling Github login, we accidentally broke the normal user creation process.

## Select Authentication Backend

The error occured because Django previously had 1 default authentication backend, but now it has two. Django doesn't know which one to use when creating new user, so we'll have to help it decide. To do that replace the `user=form.save()` in the registration view `users/views.py` with the indicated codes below:

```python
# from ...

# def dashboard(...)

def register(request):
  # if ...
  elif request.method == "POST":
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False) # replace with this line
      user.backend = "django.contrib.auth.backends.ModelBackend" # replace with this line
      user.save() # and replace with this line
      # ...
```

Because we used `commit=False`, the user created from the github is not immediately saved. This way, we can have both normal user creation and social media authentication in the same Django user management system. I'm not sure about the last sentence though.

Thanks to [RealPathon](https://realpython.com/django-user-management/) for this great tutorial.
Ideas are welcome at [discussions](https://github.com/sunilale0/django-user-management/discussions).
Post issues [here](https://github.com/sunilale0/django-user-management/issues).
