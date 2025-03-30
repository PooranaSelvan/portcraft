from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import base64
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

        # Handle project images
        project_images = []
        if 'project_images' in request.files:
            files = request.files.getlist('project_images')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    project_images.append(f'uploads/{filename}')

        # Include project_images in the portfolio data
        portfolio_data['project_images'] = project_images

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

# Save Portfolio Route
@app.route('/save_portfolio', methods=['POST'])
def save_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    about = request.form.get('about')
    skills = request.form.get('skills').split(',')
    contact = request.form.get('contact')
    social_links = request.form.get('social_links').split(',')

    # Handling project images
    project_images = []
    if 'project_images' in request.files:
        files = request.files.getlist('project_images')
        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                project_images.append(f'uploads/{filename}')

    # Save data to MongoDB
    portfolio_data = {
        'user_id': ObjectId(session['user_id']),
        'content': {
            'name': name,
            'about': about,
            'skills': skills,
            'contact': contact,
            'social_links': social_links,
            'project_images': project_images
        }
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


from bson import ObjectId  # Make sure you import ObjectId

# Preview Portfolio Route
@app.route('/preview-portfolio', methods=['GET', 'POST'])
def preview_portfolio():
    if request.method == 'POST':
        # Fetching form data correctly
        name = request.form.get('name')
        about = request.form.get('about')
        skills = request.form.get('skills')
        work_experiences = request.form.get('work')
        contact = request.form.get('contact')

        # Fetching and processing projects and social links
        projects = request.form.get('projects').split(',') if request.form.get('projects') else []
        social_links = request.form.get('social_links').split(',') if request.form.get('social_links') else []

        # Handling the project images
        project_images = []
        if 'project_images' in request.files:
            files = request.files.getlist('project_images')

            for file in files:
                if file:
                    # Convert file to base64 string
                    image_data = base64.b64encode(file.read()).decode('utf-8')
                    # Append the image as a base64 string with prefix
                    project_images.append(f"data:image/jpeg;base64,{image_data}")

        portfolio_data = {
            'name': name,
            'about': about,
            'skills': skills,
            'work_experiences': work_experiences,
            'contact': contact,
            'projects': projects,
            'social_links': social_links,
            'project_images': project_images
        }

        return render_template('preview.html', portfolio_data=portfolio_data)

    return render_template('create_portfolio.html')


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
                    'social_links': social_links
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