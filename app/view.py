from app import app
from flask import render_template, url_for, redirect
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import UserForm, LoginForm

@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
    
    return render_template('index.html', form=form)