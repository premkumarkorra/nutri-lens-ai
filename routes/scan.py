import os
import uuid
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from config import Config
from routes.profile import login_required
from services.ocr_service import OCRService
from database.connection import db

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/api/scan', methods=['POST'])
@login_required
def upload_and_ocr():
    user_id = session['user_id']

    # 1. Check if the file is present
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided in the request."}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Selected file has an empty filename."}), 400

    # 2. Verify file extension and size
    if not OCRService.allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Supported: PNG, JPG, JPEG, WEBP, GIF."}), 400

    try:
        # Secure the filename and make it unique using UUID to prevent overlaps
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Save to uploads folder
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # 3. Extract text from image via OCR service
        ocr_result = OCRService.extract_text(filepath)

        if ocr_result.get("is_fallback") or not ocr_result.get("text", "").strip():
            return jsonify({
                "error": "Could not read this label. Make sure Tesseract OCR is installed, then try a clear, well-lit photo of the ingredients panel. You can also type or paste the ingredients manually.",
                "ocr_unavailable": True
            }), 503
        
        return jsonify({
            "message": ocr_result["message"],
            "raw_text": ocr_result["text"],
            "confidence": ocr_result["confidence"],
            "is_fallback": ocr_result["is_fallback"],
            "image_path": filepath
        }), 200

    except Exception as e:
        print(f"Error during scan/OCR: {e}")
        return jsonify({"error": "Failed to process image and extract text."}), 500


@scan_bp.route('/api/history', methods=['GET'])
@login_required
def get_scan_history():
    user_id = session['user_id']
    try:
        # Fetch previous scans for this user
        scans = db.execute_query(
            "SELECT id, image_path, status, created_at FROM scans WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        
        history_list = []
        for scan in scans:
            # Get main warning allergen or text
            warnings = db.execute_query(
                "SELECT detected_name FROM scan_ingredients WHERE scan_id = ? AND match_status = 'AVOID' LIMIT 2",
                (scan['id'],)
            )
            warning_items = [w['detected_name'] for w in warnings]
            
            main_warning = ""
            if warning_items:
                main_warning = f"Avoid: {', '.join(warning_items)}"
            else:
                cautions = db.execute_query(
                    "SELECT detected_name FROM scan_ingredients WHERE scan_id = ? AND match_status = 'CAUTION' LIMIT 1",
                    (scan['id'],)
                )
                if cautions:
                    main_warning = f"Caution: {cautions[0]['detected_name']}"
                else:
                    main_warning = "Verified Safe"

            history_list.append({
                "id": scan['id'],
                "image_path": scan['image_path'],
                "status": scan['status'],
                "main_warning": main_warning,
                "created_at": scan['created_at']
            })

        return jsonify({"history": history_list}), 200
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": "Failed to retrieve scan history."}), 500


@scan_bp.route('/api/history/<int:scan_id>', methods=['GET'])
@login_required
def get_scan_detail(scan_id):
    user_id = session['user_id']
    try:
        # 1. Fetch scan metadata
        scan = db.execute_query_one(
            "SELECT * FROM scans WHERE id = ? AND user_id = ?",
            (scan_id, user_id)
        )
        if not scan:
            return jsonify({"error": "Scan record not found or access denied."}), 404

        # 2. Fetch matched ingredients
        ingredients_rows = db.execute_query(
            """
            SELECT si.*, i.canonical_name, i.category, i.explanation, i.safer_alternatives
            FROM scan_ingredients si
            LEFT JOIN ingredients i ON si.ingredient_id = i.id
            WHERE si.scan_id = ?
            """,
            (scan_id,)
        )

        ingredients = []
        for row in ingredients_rows:
            ingredients.append({
                "detected_name": row['detected_name'],
                "canonical_name": row['canonical_name'] or row['detected_name'],
                "category": row['category'] or "General",
                "status": row['match_status'],
                "reason": row['match_reason'],
                "explanation": row['explanation'] or "",
                "alternatives": row['safer_alternatives'] or ""
            })

        # 3. Fetch recommendation summaries
        rec_row = db.execute_query_one(
            "SELECT recommendations_text FROM recommendations WHERE scan_id = ?",
            (scan_id,)
        )
        
        # Structure alternatives nicely for the UI
        # We can extract it from ingredients directly or fetch saved recommendation texts
        import json
        recommendations = []
        if rec_row and rec_row['recommendations_text']:
            try:
                recommendations = json.loads(rec_row['recommendations_text'])
            except:
                pass

        return jsonify({
            "scan_id": scan['id'],
            "image_path": scan['image_path'],
            "status": scan['status'],
            "created_at": scan['created_at'],
            "raw_text": scan['raw_text'],
            "ingredients": ingredients,
            "recommendations": recommendations
        }), 200

    except Exception as e:
        print(f"Error fetching scan detail: {e}")
        return jsonify({"error": "Failed to retrieve scan details."}), 500
