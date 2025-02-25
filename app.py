from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import os
from bson.objectid import ObjectId

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)
app.config["MONGO_URI"] = "mongodb+srv://user1:sample1@sample.ofxan.mongodb.net/myDatabase"
mongo = PyMongo(app)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one({'username': request.form['username']})
        if existing_user is None:
            hashed_password = generate_password_hash(request.form['password'])
            mongo.db.users.insert_one({'username': request.form['username'], 'password': hashed_password})
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        flash('Username already exists', 'error')
    return render_template('register.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

# User Profile Route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('profile.html', user=user)

# Create Portfolio Route
@app.route('/create-portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        portfolio_data = {
            'name': request.form['name'],
            'about': request.form['about'],
            'skills': request.form['skills'],
            'work': request.form['work'],
            'projects': request.form['projects'],
            'contact': request.form['contact'],
            'social_links': request.form['social_links'].split(',')
        }

        user_id = ObjectId(session['user_id'])

        mongo.db.portfolios.insert_one({
            'user_id': user_id,
            'content': portfolio_data
        })

        flash('Portfolio created successfully!', 'success')
        return redirect(url_for('my_portfolios'))

    return render_template('create_portfolio.html')

# View Portfolio Route
@app.route('/portfolio/<username>/<portfolio_id>')
def view_portfolio(username, portfolio_id):
    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})
    if portfolio:
        return render_template('view_portfolio.html', portfolio=portfolio)
    return "Portfolio not found", 404


@app.route('/save_portfolio', methods=['POST'])
def save_portfolio():
    # Extract form data
    name = request.form.get('name')
    about = request.form.get('about')
    skills = request.form.get('skills').split(',')
    work = request.form.get('work')
    projects = request.form.get('projects').split(',')
    contact = request.form.get('contact')
    social_links = request.form.get('social_links').split(',')

    # Save data to MongoDB
    portfolio_data = {
        'name': name,
        'about': about,
        'skills': skills,
        'work': work,
        'projects': projects,
        'contact': contact,
        'social_links': social_links,
        'user_id': session['user_id']  # Save by user ID for authentication
    }
    mongo.db.portfolios.insert_one(portfolio_data)


    flash('Portfolio saved successfully!', 'success')
    return redirect(url_for('my_portfolios'))


# Delete Portfolio Route
@app.route('/delete_portfolio/<portfolio_id>', methods=['GET', 'POST'])
def delete_portfolio(portfolio_id):
    # Check if the portfolio exists
    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})
    if portfolio:
        mongo.db.portfolios.delete_one({'_id': ObjectId(portfolio_id)})
        print(f"Deleted portfolio with ID: {portfolio_id}")
        flash('Portfolio deleted successfully!', 'success')
    else:
        print(f"No portfolio found with ID: {portfolio_id}")
        flash('Portfolio not found.', 'error')
    return redirect(url_for('my_portfolios'))

# Preview Portfolio Route
@app.route('/preview', methods=['POST'])
def preview():
    portfolio_data = {
        'name': request.form.get('name', 'Not provided'),
        'about': request.form.get('about', 'Not provided'),
        'skills': request.form.get('skills', 'Not provided'),
        'contact': request.form.get('contact', 'Not provided'),
        'projects': request.form.getlist('projects'),  # Make sure this is a list
        'social_links': request.form.getlist('social_links')  # Make sure this is a list
    }
    return render_template('preview.html', portfolio_data=portfolio_data)

# My Portfolios Route
@app.route('/my-portfolios')
def my_portfolios():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    portfolios = list(mongo.db.portfolios.find({'user_id': user_id}))

    return render_template('my_portfolios.html', portfolios=portfolios)

# Edit Portfolio Route
@app.route('/edit-portfolio/<portfolio_id>', methods=['GET', 'POST'])
def edit_portfolio(portfolio_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})

    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'about': request.form['about'],
            'skills': request.form['skills'],
            'work': request.form['work'],
            'projects': request.form['projects'],
            'contact': request.form['contact'],
            'social_links': request.form['social_links'].split(',')
        }

        mongo.db.portfolios.update_one({'_id': ObjectId(portfolio_id)}, {'$set': {'content': updated_data}})
        flash('Portfolio updated successfully!', 'success')
        return redirect(url_for('my_portfolios'))

    return render_template('edit_portfolio.html', portfolio=portfolio)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
