from flask import Blueprint, request, jsonify, session
from database.connection import db
from services.knowledge_base import KnowledgeBase
from services.personalization import PersonalizationEngine

profile_bp = Blueprint('profile', __name__)

def login_required(func):
    """Decorator to enforce authenticated routes."""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized. Please log in first."}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    user_id = session['user_id']
    try:
        # Fetch user's profile using personalization helper
        profile = PersonalizationEngine.get_user_profile(user_id)
        
        # Also get all available allergens from the system knowledge base
        system_allergens = KnowledgeBase.get_all_allergens()
        
        return jsonify({
            "profile": profile,
            "system_allergens": system_allergens,
            "all_allergens": system_allergens,
            "user_allergies": profile.get("allergens", []),
            "vegetarian_status": profile.get("vegetarian", False),
            "is_vegetarian": profile.get("vegetarian", False),
            "non_vegetarian": not profile.get("vegetarian", False),
            "vegan_status": profile.get("is_vegan", False),
            "age_range": profile.get("age_range", "25-34"),
            "avoid_ingredients": profile.get("avoid_ingredients", []),
            "preferences": profile.get("preferences", [])
        }), 200
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return jsonify({"error": "Failed to retrieve user profile."}), 500


@profile_bp.route('/api/profile', methods=['POST', 'PUT'])
@login_required
def update_profile():
    user_id = session['user_id']
    data = request.get_json() or {}

    # Basic validations
    age_range = data.get('age_range', '25-34').strip() if isinstance(data.get('age_range'), str) else '25-34'
    vegetarian = int(bool(data.get('vegetarian', False)))
    vegan = int(bool(data.get('vegan', False)))
    allergies = data.get('allergies', []) # List of allergen names
    preferences = data.get('preferences', []) # List of preference tags (e.g. "Low Sugar")
    avoid_ingredients = data.get('avoid_ingredients', []) # List of strings

    try:
        # 1. Update user_profiles table
        existing = db.execute_query_one("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
        if existing:
            db.execute_write(
                "UPDATE user_profiles SET age_range = ?, vegetarian_status = ?, vegan_status = ? WHERE user_id = ?",
                (age_range, vegetarian, vegan, user_id)
            )
        else:
            db.execute_write(
                "INSERT INTO user_profiles (user_id, age_range, vegetarian_status, vegan_status) VALUES (?, ?, ?, ?)",
                (user_id, age_range, vegetarian, vegan)
            )

        # 2. Update user_allergies mapping
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

        # 3. Update user_preferences (health goals)
        db.execute_write("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
        for pref in preferences:
            pref = pref.strip()
            if pref:
                db.execute_write(
                    "INSERT INTO user_preferences (user_id, preference_tag) VALUES (?, ?)",
                    (user_id, pref)
                )

        # 4. Update user_avoid_ingredients
        db.execute_write("DELETE FROM user_avoid_ingredients WHERE user_id = ?", (user_id,))
        for item in avoid_ingredients:
            item = item.strip()
            if item:
                db.execute_write(
                    "INSERT INTO user_avoid_ingredients (user_id, ingredient_name) VALUES (?, ?)",
                    (user_id, item)
                )

        # Return updated profile
        updated_profile = PersonalizationEngine.get_user_profile(user_id)
        return jsonify({
            "message": "User health and dietary profile updated successfully.",
            "profile": updated_profile
        }), 200

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({"error": "Failed to update profile settings."}), 500
