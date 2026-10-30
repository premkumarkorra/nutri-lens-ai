from database.connection import db
from services.knowledge_base import KnowledgeBase

class PersonalizationEngine:
    @staticmethod
    def get_user_profile(user_id):
        """Helper to fetch a complete user profile dictionary from the database."""
        profile = db.execute_query_one(
            "SELECT age_range, vegetarian_status, vegan_status FROM user_profiles WHERE user_id = ?",
            (user_id,)
        )
        if not profile:
            # Default fallback profile
            profile = {"age_range": "unknown", "vegetarian_status": 0, "vegan_status": 0}
            
        # Get allergies
        allergies_rows = db.execute_query(
            """
            SELECT a.name FROM user_allergies ua 
            JOIN allergens a ON ua.allergen_id = a.id 
            WHERE ua.user_id = ?
            """,
            (user_id,)
        )
        allergies = [row['name'] for row in allergies_rows]

        # Get preferences (health goals)
        pref_rows = db.execute_query(
            "SELECT preference_tag FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        preferences = [row['preference_tag'] for row in pref_rows]

        # Get avoid ingredients list
        avoid_rows = db.execute_query(
            "SELECT ingredient_name FROM user_avoid_ingredients WHERE user_id = ?",
            (user_id,)
        )
        avoid_list = [row['ingredient_name'].lower().strip() for row in avoid_rows]

        return {
            "age_range": profile.get("age_range", "unknown"),
            "vegetarian": bool(profile.get("vegetarian_status", 0)),
            "vegan": bool(profile.get("vegan_status", 0)),
            "allergies": allergies,
            "preferences": preferences,
            "avoid_ingredients": avoid_list
        }

    @classmethod
    def analyze_ingredients(cls, ingredients_list, user_id):
        """
        Analyzes a list of parsed ingredients against a user's health profile.
        Returns a dictionary containing the overall safety rating and structured explanation cards.
        """
        user_profile = cls.get_user_profile(user_id)
        
        analyzed_items = []
        overall_status = "SAFE" # Default overall status

        for ing_name in ingredients_list:
            ing_name_clean = ing_name.strip()
            if not ing_name_clean:
                continue

            # Initial status values
            status = "SAFE"
            reason = "No conflicts detected with your profile."
            trigger = None
            confidence = "High"
            explanation = ""
            category = "General"
            alternatives = ""
            canonical_name = "Unknown"

            # Query knowledge base
            ing_data = KnowledgeBase.find_ingredient(ing_name_clean)
            
            # --- RULE MATCHING ---
            
            # Scenario A: Ingredient is UNKNOWN in the database
            if not ing_data:
                canonical_name = ing_name_clean
                category = "Unverified"
                
                # Check if it matches any explicit avoid rules as a substring anyway
                matched_avoid = False
                for avoid_item in user_profile['avoid_ingredients']:
                    if avoid_item in ing_name_clean.lower():
                        status = "AVOID"
                        reason = f"This ingredient matches your blocklist item: '{avoid_item}'."
                        trigger = "Explicit Avoid List"
                        explanation = "You added this ingredient or keyword to your personal avoid list."
                        matched_avoid = True
                        break
                        
                if not matched_avoid:
                    status = "CAUTION"
                    reason = "This ingredient needs confirmation from the package label."
                    trigger = "Database Missing Item"
                    confidence = "Low"
                    explanation = "Review the package label and manufacturer allergen statement before choosing this product."
                    alternatives = "Check the manufacturer's website or allergen statement."
            
            # Scenario B: Ingredient IS found in the database
            else:
                canonical_name = ing_data['canonical_name']
                category = ing_data['category']
                explanation = ing_data['explanation']
                alternatives = ing_data['safer_alternatives']

                # 1. Check explicit avoidance list
                matched_avoid = False
                for avoid_item in user_profile['avoid_ingredients']:
                    if (avoid_item in canonical_name.lower() or 
                        avoid_item in ing_name_clean.lower()):
                        status = "AVOID"
                        reason = f"Matches your blocklist item: '{avoid_item}'."
                        trigger = "Explicit Avoid List"
                        matched_avoid = True
                        break

                # 2. Check allergen matches if not already avoided
                if not matched_avoid:
                    for allergen in ing_data['allergens']:
                        a_name = allergen['name']
                        risk_level = allergen['risk_level']
                        
                        if a_name in user_profile['allergies']:
                            if risk_level in ['DIRECT', 'DERIVATIVE']:
                                status = "AVOID"
                                trigger = f"{a_name} Allergy"
                                if risk_level == 'DIRECT':
                                    reason = f"Contains '{canonical_name}', which is a direct {a_name} ingredient."
                                else:
                                    reason = f"Contains '{canonical_name}', which is a derivative of {a_name}."
                                break
                            elif risk_level == 'CROSS_REACT':
                                # Cross-reactivity counts as a Caution
                                status = "CAUTION"
                                trigger = f"{a_name} Allergy Warning"
                                reason = f"May cause cross-reactivity with {a_name} allergies."
                                confidence = "Medium"
                                break

                # 3. Check vegan/vegetarian rules if status is still SAFE/CAUTION
                if status != "AVOID":
                    # Vegan check
                    if user_profile['vegan'] and ing_data['vegan_status'] == 'NO':
                        status = "AVOID"
                        trigger = "Vegan Diet"
                        reason = f"'{canonical_name}' is not vegan-compliant (animal-derived)."
                    elif user_profile['vegan'] and ing_data['vegan_status'] in ['MAYBE', 'UNKNOWN']:
                        # If not already AVOID (e.g. from allergy), flag as Caution
                        if status == "SAFE":
                            status = "CAUTION"
                            trigger = "Vegan Compliance Check"
                            reason = f"The vegan status of '{canonical_name}' is questionable."
                            confidence = "Medium"
                            
                    # Vegetarian check
                    elif user_profile['vegetarian'] and ing_data['vegetarian_status'] == 'NO':
                        status = "AVOID"
                        trigger = "Vegetarian Diet"
                        reason = f"'{canonical_name}' is not vegetarian-compliant."
                    elif user_profile['vegetarian'] and ing_data['vegetarian_status'] in ['MAYBE', 'UNKNOWN']:
                        if status == "SAFE":
                            status = "CAUTION"
                            trigger = "Vegetarian Compliance Check"
                            reason = f"The vegetarian status of '{canonical_name}' is questionable."
                            confidence = "Medium"

                # 4. Check Health Goals / Preferences
                if status == "SAFE":
                    # Low Sugar Check
                    if "Low Sugar" in user_profile['preferences'] and "high_sugar" in ing_data['dietary_tags']:
                        status = "CAUTION"
                        trigger = "Low Sugar Goal"
                        reason = f"'{canonical_name}' is high in sugar or simple carbohydrates."
                        confidence = "High"
                    elif "Low Sugar" in user_profile['preferences'] and "high_glycemic" in ing_data['dietary_tags']:
                        status = "CAUTION"
                        trigger = "Low Sugar Goal"
                        reason = f"'{canonical_name}' has a high glycemic index (triggers rapid blood glucose rises)."
                        confidence = "Medium"
                        
                    # Low Sodium Check
                    elif "Low Sodium" in user_profile['preferences'] and "high_sodium" in ing_data['dietary_tags']:
                        status = "CAUTION"
                        trigger = "Low Sodium Goal"
                        reason = f"'{canonical_name}' is high in sodium (commonly used as preservative/flavor)."
                        confidence = "High"

            # Update overall status: AVOID takes precedence, then CAUTION, then SAFE
            if status == "AVOID":
                overall_status = "AVOID"
            elif status == "CAUTION" and overall_status != "AVOID":
                overall_status = "CAUTION"

            analyzed_items.append({
                "detected_name": ing_name_clean,
                "canonical_name": canonical_name,
                "category": category,
                "status": status,
                "reason": reason,
                "trigger": trigger,
                "confidence": confidence,
                "explanation": explanation,
                "alternatives": alternatives
            })

        # LLM integration hook
        # If an API key is available, we could run the LLM interpreter to smooth out explanations.
        # But standard rules are always the source of truth to prevent LLM hallucinations.
        avoids = [item for item in analyzed_items if item["status"] == "AVOID"]
        cautions = [item for item in analyzed_items if item["status"] == "CAUTION"]
        safe_count = len(analyzed_items) - len(avoids) - len(cautions)
        conflict_names = list(dict.fromkeys(item["canonical_name"] for item in avoids))
        caution_names = list(dict.fromkeys(item["canonical_name"] for item in cautions))

        if overall_status == "AVOID":
            summary_description = f"This product is not a good match for your profile. {len(avoids)} detected conflict(s) require you to avoid it."
            if conflict_names:
                summary_description += f" Main concerns: {', '.join(conflict_names[:4])}."
            summary_action = "Check the package allergen statement before consuming this product."
        elif overall_status == "CAUTION":
            summary_description = f"This product needs a closer review. {len(cautions)} ingredient(s) could not be confirmed as compatible with your profile."
            if caution_names:
                summary_description += f" Items needing attention: {', '.join(caution_names[:4])}."
            summary_action = "Review the label and manufacturer allergen information before choosing it."
        else:
            summary_description = f"This product looks compatible with your saved profile. {safe_count} detected ingredient(s) matched without a known conflict."
            summary_action = "Still check the physical package for manufacturing and cross-contact warnings."

        return {
            "overall_status": overall_status,
            "ingredients": analyzed_items,
            "overall_summary": {
                "description": summary_description,
                "recommended_action": summary_action,
                "total_ingredients": len(analyzed_items),
                "safe_count": safe_count,
                "caution_count": len(cautions),
                "avoid_count": len(avoids),
                "conflicts": conflict_names,
                "items_for_review": caution_names
            }
        }

    @staticmethod
    def generate_explanation(ingredient_data, user_profile, analysis_result):
        """
        Abstraction wrapper for potential LLM usage later.
        If an LLM key is configured, it would generate a natural-sounding paragraph summary.
        Otherwise, it generates a robust deterministic summary of warnings.
        """
        import os
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            # Here we would do a fetch to OpenAI or another provider
            # For this deployment, we construct a high-quality human-readable text block
            pass
            
        # Fallback to local rule-based aggregator
        avoids = [item for item in analysis_result['ingredients'] if item['status'] == 'AVOID']
        cautions = [item for item in analysis_result['ingredients'] if item['status'] == 'CAUTION']
        
        summary_parts = []
        if avoids:
            summary_parts.append(f"AVOID WARNING: We detected {len(avoids)} ingredient(s) that conflict with your preferences. ")
            for item in avoids:
                summary_parts.append(f"- {item['detected_name']} ({item['canonical_name']}): {item['reason']} (Trigger: {item['trigger']}). ")
        
        if cautions:
            summary_parts.append(f"CAUTION: {len(cautions)} item(s) require review. ")
            for item in cautions:
                summary_parts.append(f"- {item['detected_name']}: {item['reason']} ")
                
        if not avoids and not cautions:
            summary_parts.append("All detected ingredients are verified as safe according to your health profile.")
            
        return "".join(summary_parts)
