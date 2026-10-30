import re


class RecommendationService:
    @staticmethod
    def _normalize(value):
        return re.sub(r"[^a-z0-9 ]", "", value.lower()).strip()

    @classmethod
    def _is_duplicate_of_label(cls, option, detected_names):
        option_clean = cls._normalize(option)
        if not option_clean:
            return True
        return any(
            option_clean == detected_clean
            or option_clean in detected_clean
            or detected_clean in option_clean
            for detected_clean in (cls._normalize(name) for name in detected_names)
        )

    @staticmethod
    def get_recommendations(analysis_result):
        """
        Takes the output of PersonalizationEngine.analyze_ingredients and compiles
        a list of actionable suggestions and alternative food ingredients.
        """
        recommendations = []
        detected_names = [
            item.get("canonical_name", item.get("detected_name", ""))
            for item in analysis_result.get("ingredients", [])
        ]
        
        for item in analysis_result.get("ingredients", []):
            if item["status"] in ["AVOID", "CAUTION"]:
                if item["alternatives"]:
                    alternatives = [
                        option.strip().rstrip(".")
                        for option in item["alternatives"].split(",")
                        if option.strip() and not RecommendationService._is_duplicate_of_label(option, detected_names)
                    ]
                    alternatives = list(dict.fromkeys(alternatives))
                    if not alternatives:
                        continue
                    recommendations.append({
                        "ingredient": item["canonical_name"],
                        "status": item["status"],
                        "reason": item["reason"],
                        "alternatives": ", ".join(alternatives)
                    })
                elif item["status"] == "CAUTION" and item["category"] == "Unverified":
                    # Unknown ingredient recommendations
                    recommendations.append({
                        "ingredient": item["detected_name"],
                        "status": "CAUTION",
                        "reason": "This item needs confirmation from the package label.",
                        "alternatives": "Choose a clearly labelled alternative and confirm the manufacturer's allergen statement."
                    })
                    
        return recommendations
