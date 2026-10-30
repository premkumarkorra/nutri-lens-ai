import json
import os
from urllib import error, request


class AIReviewService:
    """Creates grounded product reviews with an optional OpenAI enhancement."""

    ENDPOINT = "https://api.openai.com/v1/chat/completions"

    @classmethod
    def create_review(cls, analysis_result, recommendations):
        summary = analysis_result.get("overall_summary", {})
        items = analysis_result.get("ingredients", [])
        deterministic = cls._deterministic_review(summary, items, recommendations)

        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            deterministic["source"] = "rules"
            deterministic["message"] = "Review generated from the verified NutriLens knowledge base."
            return deterministic

        try:
            ai_review = cls._request_ai_review(api_key, summary, items, recommendations)
            if ai_review:
                ai_review["source"] = "ai + rules"
                ai_review["message"] = "AI wording is grounded in the verified ingredient findings below."
                ai_review["safer_options"] = cls._merge_options(
                    ai_review.get("safer_options", []), deterministic["safer_options"]
                )
                return ai_review
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"AI product review unavailable: {exc}")

        deterministic["source"] = "rules"
        deterministic["message"] = "AI review was unavailable; this review uses the verified NutriLens knowledge base."
        return deterministic

    @staticmethod
    def _deterministic_review(summary, items, recommendations):
        avoids = [item for item in items if item.get("status") == "AVOID"]
        cautions = [item for item in items if item.get("status") == "CAUTION"]
        safe_count = summary.get("safe_count", len(items) - len(avoids) - len(cautions))
        options = []
        for recommendation in recommendations:
            alternatives = recommendation.get("alternatives", "")
            for option in alternatives.split(","):
                option = option.strip().rstrip(".")
                if option and option not in options and len(options) < 8:
                    options.append(option)

        names = " ".join(item.get("canonical_name", "").lower() for item in items)
        if any(term in names for term in ("potato", "palmolein", "namkeen", "chickpea", "besan")):
            product_identity = "Likely savoury Indian packaged snack"
        elif any(term in names for term in ("wheat flour", "maida", "biscuit", "cocoa")):
            product_identity = "Likely biscuit or baked snack"
        elif any(term in names for term in ("milk", "whey", "casein")) and any(term in names for term in ("sugar", "cocoa")):
            product_identity = "Likely dairy-based sweet or beverage mix"
        else:
            product_identity = "Packaged food product; exact brand cannot be confirmed from ingredients alone"

        if avoids:
            headline = "Avoid this product for your saved profile."
            explanation = (
                f"The label contains {len(avoids)} conflict(s) linked to your profile. "
                f"{safe_count} other detected ingredient(s) did not create a known conflict, "
                "but that does not cancel the flagged items."
            )
            action = "Choose a product with a matching allergen-free label and verify shared-facility warnings."
        elif cautions:
            headline = "Review this product before choosing it."
            explanation = (
                f"The label contains {len(cautions)} ingredient(s) that could not be confidently cleared "
                "against your profile or health goals."
            )
            action = "Check the manufacturer's allergen statement and nutrition panel before consuming it."
        else:
            headline = "This product appears compatible with your saved profile."
            explanation = f"All {safe_count} detected ingredient(s) matched without a known profile conflict."
            action = "Still verify the physical package for cross-contact and batch-specific warnings."

        return {
            "product_identity": product_identity,
            "headline": headline,
            "review": explanation,
            "recommended_action": action,
            "safer_options": options,
            "strengths": [f"{safe_count} detected ingredient(s) did not trigger a known profile conflict."],
            "concerns": [item.get("reason", "Needs review") for item in avoids + cautions][:4],
            "source": "rules"
        }

    @classmethod
    def _request_ai_review(cls, api_key, summary, items, recommendations):
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        grounded_items = [
            {
                "name": item.get("canonical_name", item.get("detected_name", "Unknown")),
                "status": item.get("status"),
                "reason": item.get("reason"),
                "category": item.get("category")
            }
            for item in items
        ]
        prompt = {
            "product_identity_instruction": "Infer a likely product category only. Never invent an exact brand or product name from ingredients alone.",
            "profile_verdict": summary.get("description", ""),
            "counts": {
                "total": summary.get("total_ingredients", len(items)),
                "safe": summary.get("safe_count", 0),
                "avoid": summary.get("avoid_count", 0),
                "review": summary.get("caution_count", 0)
            },
            "verified_findings": grounded_items,
            "known_alternatives": recommendations
        }
        body = {
            "model": model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful food-label reviewer. Use only the supplied verified findings. "
                        "Do not add allergens, medical diagnoses, or ingredient facts not present in the data. "
                        "Write a concise product-level review, not one paragraph per ingredient. "
                        "Return JSON with exactly: product_identity, headline, review, strengths, concerns, recommended_action, safer_options. "
                        "product_identity must be a cautious likely category, never a made-up brand or exact product name. "
                        "strengths and concerns must be arrays of short strings. "
                        "safer_options must be an array of strings chosen only from known_alternatives. "
                        "State that packaging and medical advice remain authoritative for severe allergies."
                    )
                },
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=True)}
            ]
        }
        http_request = request.Request(
            cls.ENDPOINT,
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST"
        )
        with request.urlopen(http_request, timeout=12) as response:
            response_body = json.loads(response.read().decode("utf-8"))
        content = response_body["choices"][0]["message"]["content"]
        result = json.loads(content)
        if not all(isinstance(result.get(field), str) and result[field].strip() for field in ("product_identity", "headline", "review", "recommended_action")):
            raise ValueError("AI returned an incomplete product review")
        if not all(isinstance(result.get(field), list) for field in ("strengths", "concerns", "safer_options")):
            raise ValueError("AI returned invalid review sections")
        if not isinstance(result.get("safer_options", []), list):
            raise ValueError("AI returned invalid safer options")
        known_options = []
        for recommendation in recommendations:
            known_options.extend(
                option.strip().rstrip(".")
                for option in recommendation.get("alternatives", "").split(",")
                if option.strip()
            )
        allowed_options = {option.lower() for option in known_options}
        if any(option.strip().lower() not in allowed_options for option in result["safer_options"]):
            raise ValueError("AI returned an unapproved safer option")
        return {
            "product_identity": result["product_identity"].strip(),
            "headline": result["headline"].strip(),
            "review": result["review"].strip(),
            "strengths": [str(item).strip() for item in result["strengths"] if str(item).strip()][:4],
            "concerns": [str(item).strip() for item in result["concerns"] if str(item).strip()][:4],
            "recommended_action": result["recommended_action"].strip(),
            "safer_options": [str(option).strip() for option in result["safer_options"] if str(option).strip()][:8]
        }

    @staticmethod
    def _merge_options(primary, fallback):
        merged = []
        for option in list(primary) + list(fallback):
            if option not in merged and len(merged) < 8:
                merged.append(option)
        return merged
