from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
import cloudinary.api
from urllib.parse import quote_plus

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

# Encode username and password
username = quote_plus("portcraft")
password = quote_plus("karthi@2k25")

# Configure Cloudinary with your credentials
cloudinary.config(
    cloud_name="dssvk1cxy", 
    api_key="885695763567298", 
    api_secret="NM7qkT3qJxdeBP0HAlhOhQl6k70"
)
 
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

app.config["MONGO_URI"] = f"mongodb+srv://{username}:{password}@portcraft.6b8vl3g.mongodb.net/myDatabase?retryWrites=true&w=majority"

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

        # Handle project images - Upload images to Cloudinary
        project_images = []
        if 'project_images' in request.files:
            files = request.files.getlist('project_images')
            for file in files:
                if file:
                    # Upload image to Cloudinary
                    try:
                        upload_result = cloudinary.uploader.upload(file)
                        image_url = upload_result['url']  # Get the URL of the uploaded image
                        project_images.append(image_url)  # Store image URL
                    except Exception as e:
                        flash(f"An error occurred while uploading image: {e}", 'error')
                        return redirect(request.url)  # Redirect back to the form

        # Include project_images in the portfolio data
        portfolio_data['project_images'] = project_images

        mongo.db.portfolios.insert_one({
            'user_id': user_id,
            'content': portfolio_data
        })

        flash('Portfolio created successfully!', 'success')
        return redirect(url_for('my-portfolios'))

    return render_template('create_portfolio.html')

# View Portfolio Route
@app.route('/portfolio/<username>/<portfolio_id>')
def view_portfolio(username, portfolio_id):
    # Fetch the portfolio from the database using the portfolio_id
    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})

    # Check if the portfolio exists
    if portfolio:
        portfolio['content'] = portfolio.get('content', {})
        portfolio['project_images'] = portfolio.get('project_images', [])  # Ensure images are included

        # Render the view_portfolio.html template with the portfolio data
        return render_template('view_portfolio.html', portfolio=portfolio)

    # If the portfolio is not found, return a 404 error
    return "Portfolio not found", 404

# My Portfolios Route
@app.route('/my-portfolios')
def my_portfolios():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    portfolios = list(mongo.db.portfolios.find({'user_id': user_id}))

    return render_template('my_portfolios.html', portfolios=portfolios)

# Edit Portfolio Route
@app.route('/edit_portfolio/<portfolio_id>', methods=['GET', 'POST'])
def edit_portfolio(portfolio_id):
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        about = request.form.get('about')
        skills = request.form.get('skills').split(',')
        contact = request.form.get('contact')
        work = request.form.get('work')  # Ensure this line is included
        projects = request.form.get('projects').split(',')
        social_links = request.form.get('social_links').split(',')

        # Handle project images - Upload images to Cloudinary
        project_images = []
        if 'project_images' in request.files:
            files = request.files.getlist('project_images')
            for file in files:
                if file:
                    # Upload image to Cloudinary
                    try:
                        upload_result = cloudinary.uploader.upload(file)
                        image_url = upload_result['url']  # Get the URL of the uploaded image
                        project_images.append(image_url)  # Store image URL
                    except Exception as e:
                        flash(f"An error occurred while uploading image: {e}", 'error')
                        return redirect(request.url)  # Redirect back to the form

        # Update the portfolio in the database
        mongo.db.portfolios.update_one(
            {'_id': ObjectId(portfolio_id)},
            {'$set': {
                'content': {
                    'name': name,
                    'about': about,
                    'skills': skills,
                    'contact': contact,
                    'work': work,  # Ensure this line is included
                    'projects': projects,
                    'social_links': social_links,
                    'project_images': project_images  # Update images with Cloudinary URLs
                }
            }}
        )

        flash('Portfolio updated successfully!', 'success')
        return redirect(url_for('my_portfolios'))

    # If GET request, retrieve the portfolio data
    portfolio = mongo.db.portfolios.find_one({'_id': ObjectId(portfolio_id)})
    return render_template('edit_portfolio.html', portfolio=portfolio)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
