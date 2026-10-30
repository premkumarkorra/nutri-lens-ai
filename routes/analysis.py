import json
from flask import Blueprint, request, jsonify, session
from database.connection import db
from routes.profile import login_required
from services.ingredient_parser import IngredientParser
from services.personalization import PersonalizationEngine
from services.recommendation import RecommendationService
from services.knowledge_base import KnowledgeBase
from services.product_engine import ProductIdentificationEngine

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/identify', methods=['POST'])
@login_required
def identify_product_direct():
    """
    Public and Authenticated endpoint implementing the ingredient-to-food-product
    identification and recommendation engine specification.
    
    Accepts:
    {
      "ingredients": "Potato, Edible Vegetable Oil, Salt"
    }
    or
    {
      "text": "Ingredients: Potato, Edible Vegetable Oil, Salt"
    }
    
    Returns the exact JSON schema defined in the prompt.
    """
    data = request.get_json() or {}
    raw_text = data.get('ingredients') or data.get('text') or data.get('corrected_text', '')
    
    if not raw_text or not raw_text.strip():
        return jsonify({
            "input_ingredients": [],
            "identified_product": {
                "name": None,
                "brand": None,
                "category": None,
                "match_level": "Insufficient",
                "verified": False
            },
            "reasoning_summary": "No ingredient text provided in request.",
            "review": {
                "taste_profile": "N/A",
                "pros": [],
                "cons": [],
                "overall": "No input ingredients to review."
            },
            "alternative_product": {
                "name": None,
                "brand": None,
                "reason": "Please provide an ingredient list to identify products and alternatives."
            },
            "accuracy_note": "Factual accuracy prioritized. No ingredients supplied."
        }), 400

    # Run product identification engine
    result = ProductIdentificationEngine.identify_with_ai_enhancement(raw_text.strip())
    
    # If user is logged in, optionally persist to scan history
    user_id = session.get('user_id')
    if user_id:
        try:
            parsed_text_str = ", ".join(result.get("input_ingredients", []))
            product_name = result.get("identified_product", {}).get("name") or "Unverified Product"
            match_lvl = result.get("identified_product", {}).get("match_level") or "Insufficient"
            status = "SAFE" if match_lvl in ["Exact", "Strong", "Likely"] else ("CAUTION" if match_lvl == "Possible" else "AVOID")
            
            scan_id = db.execute_write(
                """
                INSERT INTO scans (user_id, image_path, raw_text, parsed_text, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, None, raw_text.strip(), parsed_text_str, status)
            )
            result["scan_id"] = scan_id
        except Exception as e:
            print(f"Warning: Could not save scan to history: {e}")

    return jsonify(result), 200


@analysis_bp.route('/api/analyze', methods=['POST'])
def analyze_label():
    """
    Unified analysis endpoint:
    Performs Product Identification & Finished-Product Alternative Recommendation
    AND Personalization Health/Allergy Profile Screening.
    """
    data = request.get_json() or {}

    corrected_text = (data.get('corrected_text') or data.get('ingredients') or data.get('text', '')).strip()
    raw_image_path = data.get('image_path')
    image_path = raw_image_path.strip() if isinstance(raw_image_path, str) else None
    image_path = image_path or None

    if not corrected_text:
        return jsonify({"error": "No ingredient text provided for analysis."}), 400

    try:
        # 1. Clean and parse ingredients
        cleaned_text = IngredientParser.clean_text(corrected_text)
        ingredients_list = IngredientParser.split_ingredients(cleaned_text)

        if not ingredients_list:
            return jsonify({"error": "No ingredients could be parsed from the text. Check punctuation."}), 422

        # 2. Run Product Identification & Recommendation Engine
        product_identification = ProductIdentificationEngine.identify_with_ai_enhancement(corrected_text)

        # 3. Run personalization analysis engine (if user logged in or guest profile)
        user_id = session.get('user_id')
        analysis_result = PersonalizationEngine.analyze_ingredients(ingredients_list, user_id)
        overall_status = analysis_result["overall_status"]

        scan_id = None
        if user_id:
            # Create scan record in database
            parsed_text_str = ", ".join(ingredients_list)
            scan_id = db.execute_write(
                """
                INSERT INTO scans (user_id, image_path, raw_text, parsed_text, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, image_path, corrected_text, parsed_text_str, overall_status)
            )

            # Save individual ingredient analysis items
            for item in analysis_result["ingredients"]:
                ing_db_id = None
                ing_data = KnowledgeBase.find_ingredient(item["detected_name"])
                if ing_data:
                    ing_db_id = ing_data["id"]

                db.execute_write(
                    """
                    INSERT INTO scan_ingredients (scan_id, ingredient_id, detected_name, match_status, match_reason)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (scan_id, ing_db_id, item["detected_name"], item["status"], item["reason"])
                )

            # Compile and save recommendations
            recommendations_json = json.dumps(product_identification)
            db.execute_write(
                """
                INSERT INTO recommendations (scan_id, user_id, recommendations_text)
                VALUES (?, ?, ?)
                """,
                (scan_id, user_id, recommendations_json)
            )

        # 4. Return combined comprehensive response
        return jsonify({
            "scan_id": scan_id,
            "status": overall_status,
            "overall_summary": analysis_result["overall_summary"],
            "ingredients": analysis_result["ingredients"],
            # Strict Prompt Output Integration
            "product_identification": product_identification,
            "input_ingredients": product_identification.get("input_ingredients", ingredients_list),
            "identified_product": product_identification.get("identified_product"),
            "reasoning_summary": product_identification.get("reasoning_summary"),
            "review": product_identification.get("review"),
            "alternative_product": product_identification.get("alternative_product"),
            "accuracy_note": product_identification.get("accuracy_note")
        }), 200

    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"error": f"Failed to analyze ingredients: {str(e)}"}), 500
