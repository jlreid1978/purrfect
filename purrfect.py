from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from logging.handlers import RotatingFileHandler
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Length
import cat
import os
import user
import logging


app = Flask(__name__)
app.secret_key = b'ev$J"~d%tqvuJ4s'
admin_users = ['jreid']

# Setup logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    security_question = StringField('Security Question', validators=[DataRequired()])
    security_answer = StringField('Security Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PasswordResetForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    security_answer = StringField('Security Answer', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class UpdateEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Email')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


@app.context_processor
def inject_current_user():
    if 'username' in session:
        user_info = user.get_user_info(session['username'])
        if user_info:
            return {'current_user': user_info}
    return {'current_user': {'is_authenticated': False, 'username': None, 'name': None, 'email': None}}


@app.route('/')
def title_page():
    try:
        return render_template('welcome.html')
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return render_template('error.html', error_message="An error occurred")


@app.route('/logout', methods=['GET'])
def logout():
    try:
        session.pop('username', None)
        session.pop('name', None)
        session.pop('logged_in', None)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegisterForm()
        if request.method == 'POST':
            name = form.name.data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            confirm_password = form.confirm_password.data
            security_question = form.security_question.data
            security_answer = form.security_answer.data

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))

            message = user.register_user(name, username, email, password, security_question, security_answer)
            if message == "Registration successful":
                flash(message, 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'danger')

        return render_template('register.html', form=form)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            try:
                if user.verify_login(username, password):
                    session['username'] = username
                    session['name'] = user.get_name(username)
                    session['is_authenticated'] = True
                    flash(f'Welcome {user.get_name(username)}', 'success')
                    return redirect(url_for('title_page'))
                else:
                    flash('Invalid username or password', 'error')
            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return render_template('error.html', error_message="Failed to log in user")
        return render_template('login.html', form=form)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")


@app.route('/delete', methods=['POST'])
def delete():
    try:
        username = session.get('username')
        if username:
            user.delete_user(username)
            session.clear()
            flash("Account deleted successfully", 'success')
            return redirect(url_for('login'))
        else:
            flash('There has been an error deleting the account.', 'error')
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
    return redirect(url_for('account'))


@app.route('/account', methods=['GET', 'POST'])
def account():
    try:
        if 'username' not in session:
            flash('You need to log in to access your account settings', 'error')
            return redirect(url_for('login'))

        username = session['username']
        user_info = user.get_user_info(username)
        user_cats = cat.get_user_cats(username)
        update_email_form = UpdateEmailForm()
        change_password_form = ChangePasswordForm()

        return render_template('account.html', user_info=user_info, update_email_form=update_email_form, change_password_form=change_password_form, user_cats=user_cats)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/add-cat', methods=['POST'])
def add_cat():
    try:
        if 'username' not in session:
            flash('You need to log in to add a cat', 'error')
            return redirect(url_for('login'))

        username = session['username']
        cat_name = request.form.get('cat_name')
        cat.add_cat(username, cat_name)
        flash('Cat added successfully!', 'success')
        return redirect(url_for('account'))
    
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/remove-cat', methods=['POST'])
def remove_cat():
    if 'username' not in session:
        flash('You need to log in to remove a cat', 'error')
        return redirect(url_for('login'))

    username = session['username']
    cat_name = request.form.get('cat_name')

    try:
        cat.remove_cat(username, cat_name)
        flash('Cat removed successfully!', 'success')
    except Exception as e:
        flash(f'Error removing cat: {e}', 'error')

    return redirect(url_for('account'))


@app.route('/update-email', methods=['POST'])
def update_email():
    form = UpdateEmailForm()
    if form.validate_on_submit():
        new_email = form.email.data
        username = session.get('username')
        try:
            user.update_email(username, new_email)
            flash('Email updated successfully', 'success')
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            flash('Failed to update email', 'error')
    return redirect(url_for('account'))


@app.route('/change-password', methods=['POST'])
def change_password():
    try:
        if 'username' not in session:
            flash('You must be logged in to change your password.', 'error')
            return redirect(url_for('login'))

        form = ChangePasswordForm()
        if form.data:
            new_password = form.new_password.data
            confirm_password = form.confirm_password.data
            if new_password != confirm_password:
                flash('New password and confirm password do not match', 'error')
                return redirect(url_for('account'))

        if form.validate_on_submit():
            current_password = form.current_password.data

            if not user.is_valid_password(new_password):
                flash('Password must be at least 8 characters long, and contain an uppercase letter, a number, and a symbol', 'error')
                return redirect(url_for('account'))

            username = session['username']
            user_info = user.get_user_info(username)

            # Assuming user_info is always found because the user is logged in
            stored_password_hash = user_info['password_hash']

            if user.bcrypt.checkpw(current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                user.change_password(username, new_password)
                flash('Your password has been updated successfully!', 'success')
                return redirect(url_for('account'))
            else:
                flash('Incorrect current password. Please try again.', 'error')
                return redirect(url_for('account'))

        app.logger.error(f'An error occurred: {form.errors}')
        flash('Failed to update password. Please try again.', 'error')
        return redirect(url_for('account'))
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            user_info = user.get_forgot_info(username, email)
            if user_info['username'] == username and user_info['email'] == email:
                security_question = user_info['security_question']
                session['reset_username'] = username
                session['reset_email'] = email
                return render_template('reset_password.html', security_question=security_question)
            else:
                flash('Invalid username or email', 'error')
                return redirect(url_for('forgot_password'))

        return render_template('forgot.html')
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    try:
        if 'reset_username' not in session or 'reset_email' not in session:
            flash('Invalid session. Please start over.', 'error')
            return redirect(url_for('forgot_password'))

        if request.method == 'POST':
            username = session['reset_username']
            security_answer = request.form['security_answer']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if (user.verify_security_answer(username, security_answer)==True):
                flash('Incorrect security answer', 'error')
                return redirect(url_for('forgot_password'))

            if new_password != confirm_password:
                flash('New password and confirm password do not match', 'error')
                return redirect(url_for('reset_password'))

            if not user.is_valid_password(new_password):
                flash('Password must be at least 8 characters long, and contain an uppercase letter, a number, and a symbol', 'error')
                return redirect(url_for('reset_password'))

            user.change_password(username, new_password)
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('login'))

        return render_template('reset_password.html')
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/track', methods=['GET', 'POST'])
def track_meal():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))

        username = session['username']
        selected_date = request.args.get('selected_date')  # Retrieve selected date from query parameters

        # If selected_date is not provided, default to today's date
        if not selected_date:
            selected_date = date.today().strftime('%Y-%m-%d')

        # Fetch all meals for the selected date when the page is loaded
        meals_for_date = cat.get_meals_for_day(username, selected_date)

        if request.method == 'POST':
            selected_cat = request.form.get('cat')
            selected_food = request.form.get('food')
            weight = float(request.form.get('weight'))

            # Track the meal
            try:
                cat.track_meal(username, selected_cat, selected_food, weight, selected_date)
                flash('Meal tracked successfully!', 'success')
            except Exception as e:
                print(f"Error inserting meal: {e}")
                flash('Error tracking meal.', 'error')

            # Refresh the list of meals after tracking a new meal
            meals_for_date = cat.get_meals_for_day(username, selected_date)

        user_cats = cat.get_user_cats(username)
        foods = cat.get_foods()

        # Extract cat names from the tuple
        cat_names = [cat.strip() for cats in user_cats for cat in cats[0].split(',')]

        # Group meals by cat
        cat_meals = {}
        for meal in meals_for_date:
            cat_name = meal[0]
            if cat_name not in cat_meals:
                cat_meals[cat_name] = []
            cat_meals[cat_name].append(meal)

        # Calculate total weight and total calories for each cat
        cat_totals = {}
        for cat_name, meals in cat_meals.items():
            total_weight = sum(meal[5] for meal in meals)
            total_calories = sum(meal[6] * meal[5] for meal in meals)
            cat_totals[cat_name] = {'total_weight': total_weight, 'total_calories': total_calories}

        return render_template('track.html', cat_names=cat_names, foods=foods, 
                            cat_meals=cat_meals, cat_totals=cat_totals, 
                            selected_date=selected_date)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")


@app.route('/delete_meal', methods=['POST'])
def delete_meal():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    meal_id = request.form.get('meal_id')

    if meal_id:
        cat.remove_meal(username, meal_id)
        flash('Meal deleted successfully.', 'success')
    else:
        flash('Meal ID is required.', 'danger')
    return redirect(url_for('track_meal'))


@app.route('/add-food', methods=['POST'])
def add_food():
    if 'username' not in session:
        flash('You need to log in to add food', 'error')
        return redirect(url_for('login'))

    brand = request.form['brand']
    type = request.form['type']
    flavor = request.form['flavor']
    weight = float(request.form['weight'])
    calories = float(request.form['calories'])

    try:
        cat.add_food(brand, type, flavor, weight, calories)

        flash('Food added successfully!', 'success')
    except Exception:
        flash('An error has occurred', 'error')
    return redirect(url_for('manage_cat_food'))


@app.route('/delete-food', methods=['POST'])
def delete_food():
    if 'username' not in session:
        flash('You need to log in to manage cat food', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        food_id = request.form['food_id']
        cat.delete_food(food_id)
        flash('Food deleted successfully!', 'success')
        
    return redirect(url_for('manage_cat_food'))


@app.route('/cat_food', methods=['GET', 'POST'])
def manage_cat_food():
    try:
        if 'username' not in session:
            flash('You need to log in to manage cat food', 'error')
            return redirect(url_for('login'))

        if request.method == 'POST':
            if 'add_food' in request.form:
                return redirect(url_for('add_food'))
            elif 'delete_food' in request.form:
                return redirect(url_for('delete_food'))

        foods = cat.get_foods()
        
        return render_template('cat_food.html', foods=foods)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

@app.route('/change_date', methods=['POST'])
def change_date():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))

        username = session['username']
        selected_date = request.form.get('selected_date')
        change_type = request.form.get('change_date')
        current_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Handle date change based on the button clicked
        if change_type == 'prev':
            new_date = current_date - timedelta(days=1)
        elif change_type == 'next':
            new_date = current_date + timedelta(days=1)


        new_date_str = new_date.strftime('%Y-%m-%d')

        # Fetch meals for the new date
        meals_for_date = cat.get_meals_for_day(username, new_date_str)
        user_cats = cat.get_user_cats(username)
        foods = cat.get_foods()

        # Extract cat names from the tuple
        cat_names = [cat.strip() for cats in user_cats for cat in cats[0].split(',')]

        # Group meals by cat
        cat_meals = {}
        for meal in meals_for_date:
            cat_name = meal[0]
            if cat_name not in cat_meals:
                cat_meals[cat_name] = []
            cat_meals[cat_name].append(meal)

        # Calculate total weight and total calories for each cat
        cat_totals = {}
        for cat_name, meals in cat_meals.items():
            total_weight = sum(meal[5] for meal in meals)
            total_calories = sum(meal[6] * meal[5] for meal in meals)
            cat_totals[cat_name] = {'total_weight': total_weight, 'total_calories': total_calories}

        # Render the track.html template with the updated data
        return render_template('track.html', cat_names=cat_names, foods=foods, 
                            cat_meals=cat_meals, cat_totals=cat_totals, 
                            selected_date=new_date_str)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        flash("An error occurred", 'error')
        return render_template('error.html', error_message="An error occurred")
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
