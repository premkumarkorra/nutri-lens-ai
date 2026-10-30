from database.connection import db

class KnowledgeBase:
    @staticmethod
    def find_ingredient(name):
        """
        Looks up an ingredient by its canonical name or alias in the database.
        Returns a dictionary with ingredient info and allergens if found, otherwise None.
        """
        if not name:
            return None
            
        name_clean = name.strip().lower()
        
        # 1. Try to find direct match in ingredients table (case-insensitive)
        ing_row = db.execute_query_one(
            "SELECT * FROM ingredients WHERE LOWER(canonical_name) = ?",
            (name_clean,)
        )
        
        # 2. If not found, try to find via ingredient_aliases
        if not ing_row:
            alias_row = db.execute_query_one(
                "SELECT ingredient_id FROM ingredient_aliases WHERE LOWER(alias_name) = ?",
                (name_clean,)
            )
            if alias_row:
                ing_row = db.execute_query_one(
                    "SELECT * FROM ingredients WHERE id = ?",
                    (alias_row['ingredient_id'],)
                )
        
        # 3. If still not found, try a wildcard check as fallback (e.g. "whole milk" matches "milk")
        if not ing_row:
            # Let's see if any canonical name is a substring of the detected name, or vice versa
            # E.g. "organic peanuts" matches "peanuts" or "peanut flour" matches "peanut"
            all_ingredients = db.execute_query("SELECT * FROM ingredients")
            for item in all_ingredients:
                cname = item['canonical_name'].lower()
                # Check if canonical name is in the detected name
                # E.g., 'milk' is inside 'milk solids'
                if cname in name_clean or name_clean in cname:
                    ing_row = item
                    break

        if not ing_row:
            return None

        # Fetch associated allergens
        allergen_rows = db.execute_query(
            """
            SELECT a.name as allergen_name, ia.risk_level 
            FROM ingredient_allergens ia
            JOIN allergens a ON ia.allergen_id = a.id
            WHERE ia.ingredient_id = ?
            """,
            (ing_row['id'],)
        )
        
        allergens = []
        for row in allergen_rows:
            allergens.append({
                "name": row['allergen_name'],
                "risk_level": row['risk_level']
            })

        return {
            "id": ing_row['id'],
            "canonical_name": ing_row['canonical_name'],
            "category": ing_row['category'],
            "explanation": ing_row['explanation'],
            "vegan_status": ing_row['vegan_status'],
            "vegetarian_status": ing_row['vegetarian_status'],
            "dietary_tags": ing_row['dietary_tags'].split(',') if ing_row['dietary_tags'] else [],
            "safer_alternatives": ing_row['safer_alternatives'],
            "allergens": allergens
        }

    @staticmethod
    def get_all_allergens():
        """Returns a list of all allergens in the database."""
        return db.execute_query("SELECT id, name FROM allergens ORDER BY name")
