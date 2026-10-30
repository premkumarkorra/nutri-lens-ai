from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import db

auth_bp = Blueprint('auth', __name__)

def save_user_profile_data(user_id, data):
    """Saves user demographic, dietary, allergen, and avoidance settings."""
    age_range = data.get('age_range', '25-34').strip() if isinstance(data.get('age_range'), str) else '25-34'
    vegetarian = int(bool(data.get('vegetarian', False)))
    vegan = int(bool(data.get('vegan', False)))
    allergies = data.get('allergies', [])
    preferences = data.get('preferences', [])
    avoid_ingredients = data.get('avoid_ingredients', [])

    # 1. user_profiles table
    existing_profile = db.execute_query_one("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
    if existing_profile:
        db.execute_write(
            "UPDATE user_profiles SET age_range = ?, vegetarian_status = ?, vegan_status = ? WHERE user_id = ?",
            (age_range, vegetarian, vegan, user_id)
        )
    else:
        db.execute_write(
            "INSERT INTO user_profiles (user_id, age_range, vegetarian_status, vegan_status) VALUES (?, ?, ?, ?)",
            (user_id, age_range, vegetarian, vegan)
        )

    # 2. user_allergies table
    db.execute_write("DELETE FROM user_allergies WHERE user_id = ?", (user_id,))
    if allergies:
        allergen_placeholders = ",".join(["?"] * len(allergies))
        allergen_rows = db.execute_query(
            f"SELECT id FROM allergens WHERE name IN ({allergen_placeholders})",
            tuple(allergies)
        )
        for row in allergen_rows:
            db.execute_write(
                "INSERT INTO user_allergies (user_id, allergen_id) VALUES (?, ?)",
                (user_id, row['id'])
            )

    # 3. user_preferences table (health goals)
    db.execute_write("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
    for pref in preferences:
        pref = pref.strip()
        if pref:
            db.execute_write(
                "INSERT INTO user_preferences (user_id, preference_tag) VALUES (?, ?)",
                (user_id, pref)
            )

    # 4. user_avoid_ingredients table
    db.execute_write("DELETE FROM user_avoid_ingredients WHERE user_id = ?", (user_id,))
    for item in avoid_ingredients:
        item = item.strip()
        if item:
            db.execute_write(
                "INSERT INTO user_avoid_ingredients (user_id, ingredient_name) VALUES (?, ?)",
                (user_id, item)
            )


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    Registers a new user account AND captures their complete health & dietary profile
    at registration time.
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    try:
        # Check if user already exists
        existing = db.execute_query_one("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            return jsonify({"error": "Username is already taken. Please choose another."}), 409

        # Hash password and save user
        hashed = generate_password_hash(password)
        user_id = db.execute_write("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))

        # Save complete user profile info provided during sign up
        save_user_profile_data(user_id, data)

        # Set session
        session['user_id'] = user_id
        session['username'] = username

        return jsonify({
            "message": "Registration successful with personalized profile created.",
            "user": {"id": user_id, "username": username}
        }), 201

    except Exception as e:
        print(f"Registration exception: {e}")
        return jsonify({"error": f"An error occurred during registration: {str(e)}"}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    try:
        user = db.execute_query_one("SELECT * FROM users WHERE username = ?", (username,))
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid username or password."}), 401

        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']

        return jsonify({
            "message": "Login successful.",
            "user": {"id": user['id'], "username": user['username']}
        }), 200

    except Exception as e:
        print(f"Login exception: {e}")
        return jsonify({"error": "An internal server error occurred during login."}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful."}), 200


@auth_bp.route('/api/auth/session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "user": {"id": session['user_id'], "username": session['username']}
        }), 200
    return jsonify({"logged_in": False}), 200
