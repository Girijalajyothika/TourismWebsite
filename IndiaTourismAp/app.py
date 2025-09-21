from flask import Flask, render_template, request, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load JSON with default values if missing
def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    with open(filename, 'r') as f:
        return json.load(f)

# Save JSON
def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Landing Page
@app.route('/')
def home():
    return render_template('index.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_json('users.json', {"users": []})
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            return "Please fill in all fields."

        if any(u['username'] == username for u in users['users']):
            return "Username already exists! Go back and try another."

        users['users'].append({"username": username, "password": password})
        save_json(users, 'users.json')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json('users.json', {"users": []})
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        for user in users['users']:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                return redirect(url_for('states'))
        return "Invalid credentials! Go back and try again."
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# List of states
@app.route('/states')
def states():
    if 'username' not in session:
        return redirect(url_for('login'))
    states_data = load_json('states.json', {"states": []})
    return render_template('states.html', states=states_data['states'])

# Tours for a specific state
@app.route('/tours/<state_name>')
def tours(state_name):
    if 'username' not in session:
        return redirect(url_for('login'))
    states_data = load_json('states.json', {"states": []})
    tours_list = []
    for state in states_data['states']:
        if state['name'].lower() == state_name.lower():
            tours_list = state.get('tours', [])
            break
    return render_template('tours.html', tours=tours_list, state_name=state_name)

# Book a specific tour
@app.route('/book/<int:tour_id>', methods=['GET', 'POST'])
def book_tour(tour_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    states_data = load_json('states.json', {"states": []})
    selected_tour = None
    selected_state = None
    for state in states_data['states']:
        for tour in state.get('tours', []):
            if tour['id'] == tour_id:
                selected_tour = tour
                selected_state = state['name']
                break
        if selected_tour:
            break

    if not selected_tour:
        return "Tour not found"

    if request.method == 'POST':
        booking_date = request.form['date']
        bookings = load_json('bookings.json', [])
        bookings.append({
            "username": session['username'],
            "tour_id": tour_id,
            "tour_name": selected_tour['name'],
            "state": selected_state,
            "date": booking_date
        })
        save_json(bookings, 'bookings.json')
        return redirect(url_for('mybookings'))

    return render_template('book_tour.html', tour=selected_tour)

# View user's bookings
@app.route('/mybookings')
def mybookings():
    if 'username' not in session:
        return redirect(url_for('login'))
    bookings = load_json('bookings.json', [])
    user_bookings = [b for b in bookings if b['username'] == session['username']]
    return render_template('mybookings.html', bookings=user_bookings)

if __name__ == '__main__':
    app.run(debug=True, port=2018)
