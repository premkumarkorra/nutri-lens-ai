import re

class IngredientParser:
    @staticmethod
    def clean_text(text):
        """Cleans raw text by removing typical prefixes, headers, and footer notes."""
        if not text:
            return ""
        
        # Convert to single line or space-spaced text
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove introductory text like "INGREDIENTS:" or "Contains:"
        prefixes = [
            r'^.*ingredients\s*:\s*',
            r'^.*contains\s*:\s*',
            r'^.*composition\s*:\s*'
        ]
        for prefix in prefixes:
            text = re.sub(prefix, '', text, flags=re.IGNORECASE)
            
        # Remove ending statements like "Manufactured in a facility..."
        footers = [
            r'\.?\s*manufactured in a facility.*$',
            r'\.?\s*may contain traces of.*$',
            r'\.?\s*facility warning.*$'
        ]
        for footer in footers:
            text = re.sub(footer, '', text, flags=re.IGNORECASE)
            
        # Clean trailing periods and spacing
        text = text.strip().rstrip('.')
        return text

    @staticmethod
    def split_ingredients(text):
        """Splits an ingredient string on commas, ignoring commas inside parentheses."""
        if not text:
            return []
            
        # Replace square brackets with parentheses for uniformity
        text = text.replace('[', '(').replace(']', ')')
        
        # Regex to split on commas NOT inside parentheses
        # This matches commas that are followed by an even number of parentheses
        parts = re.split(r',\s*(?![^()]*\))', text)
        
        ingredients = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Clean off percentages/quantities like (70%), (10g), 2%, less than 2% of, etc.
            part = re.sub(r'\b(less than )?\d+%\s*(of)?\b', '', part, flags=re.IGNORECASE)
            part = re.sub(r'\b\d+g\b', '', part, flags=re.IGNORECASE)
            part = re.sub(r'\s*\(\s*\d+\s*%\s*\)', '', part, flags=re.IGNORECASE)
            
            # Remove leading/trailing symbols, double spaces
            part = re.sub(r'\s+', ' ', part).strip().strip('*').strip()
            if not part:
                continue
                
            # Check if there is parentheses with sub-ingredients/aliases, e.g. "Soy Lecithin (E322)"
            parenthesis_match = re.search(r'\((.*?)\)', part)
            if parenthesis_match:
                # Get parent item: "Soy Lecithin"
                parent_item = re.sub(r'\(.*?\)', '', part).strip()
                # Get child item: "E322"
                child_item = parenthesis_match.group(1).strip()
                
                # Add parent
                if parent_item and len(parent_item) > 1:
                    ingredients.append(parent_item)
                
                # Check if child contains comma-separated sub-ingredients, e.g. "(wheat flour, iron)"
                if ',' in child_item:
                    sub_parts = [sp.strip() for sp in child_item.split(',')]
                    for sp in sub_parts:
                        if sp and len(sp) > 1:
                            ingredients.append(sp)
                else:
                    if child_item and len(child_item) > 1 and not child_item.lower().startswith('emulsifier'):
                        ingredients.append(child_item)
            else:
                ingredients.append(part)
                
        # Normalize and remove duplicates while preserving order
        seen = set()
        normalized_ingredients = []
        for ing in ingredients:
            # Strip common marketing terms
            clean_ing = re.sub(r'\b(organic|natural|artificial|pure|enriched|bleached)\b', '', ing, flags=re.IGNORECASE)
            clean_ing = re.sub(r'\s+', ' ', clean_ing).strip()
            
            if clean_ing and clean_ing.lower() not in seen:
                seen.add(clean_ing.lower())
                normalized_ingredients.append(clean_ing)
                
        return normalized_ingredients
