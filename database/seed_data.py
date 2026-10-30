import os
from werkzeug.security import generate_password_hash
from database.connection import db

def seed_database():
    print("Starting database seeding...")

    # 1. Seed Allergens
    allergens = [
        "Milk", "Egg", "Peanut", "Tree nuts", "Soy", "Wheat/gluten", "Fish", "Shellfish", "Sesame"
    ]
    for allergen in allergens:
        existing = db.execute_query_one("SELECT id FROM allergens WHERE name = ?", (allergen,))
        if not existing:
            db.execute_write("INSERT INTO allergens (name) VALUES (?)", (allergen,))
    
    # Reload allergens map
    allergen_rows = db.execute_query("SELECT id, name FROM allergens")
    allergen_map = {row['name']: row['id'] for row in allergen_rows}

    # 2. Seed Ingredients & Aliases & Ingredient-Allergen relationships
    ingredients_data = [
        {
            "canonical_name": "Milk",
            "category": "Dairy",
            "explanation": "Standard dairy milk. Source of calcium and lactose.",
            "vegan_status": "NO",
            "vegetarian_status": "YES",
            "dietary_tags": "dairy",
            "safer_alternatives": "Almond milk, Oat milk, Soy milk, Coconut milk.",
            "aliases": ["milk solids", "whole milk", "skim milk", "dehydrated milk"],
            "allergens": [("Milk", "DIRECT")]
        },
        {
            "canonical_name": "Whey Protein Isolate",
            "category": "Dairy Protein",
            "explanation": "A high-protein derivative of milk serum. Frequently used in protein powders.",
            "vegan_status": "NO",
            "vegetarian_status": "YES",
            "dietary_tags": "dairy,high_protein",
            "safer_alternatives": "Pea protein isolate, Rice protein, Hemp protein.",
            "aliases": ["whey protein", "whey", "sweet whey", "whey powder"],
            "allergens": [("Milk", "DERIVATIVE")]
        },
        {
            "canonical_name": "Casein",
            "category": "Dairy Protein",
            "explanation": "The primary phosphorus-containing protein in milk. Slowly digesting protein.",
            "vegan_status": "NO",
            "vegetarian_status": "YES",
            "dietary_tags": "dairy,high_protein",
            "safer_alternatives": "Soy protein, Pea protein.",
            "aliases": ["caseinate", "sodium caseinate", "calcium caseinate"],
            "allergens": [("Milk", "DERIVATIVE")]
        },
        {
            "canonical_name": "Soy Lecithin",
            "category": "Emulsifier",
            "explanation": "An emulsifier extracted from soybeans. Helps blend ingredients and textures.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "soy_derived",
            "safer_alternatives": "Sunflower lecithin, Egg lecithin.",
            "aliases": ["lecithin", "E322", "lecithins", "soya lecithin"],
            "allergens": [("Soy", "DERIVATIVE")]
        },
        {
            "canonical_name": "Peanut Flour",
            "category": "Nut Product",
            "explanation": "Finely ground peanuts. High risk for severe peanut allergies.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "nuts",
            "safer_alternatives": "Sunflower seed flour, Oat flour, Almond flour (if not allergic to tree nuts).",
            "aliases": ["peanuts", "peanut powder", "ground peanuts", "arachis oil"],
            "allergens": [("Peanut", "DIRECT")]
        },
        {
            "canonical_name": "Wheat Flour",
            "category": "Grain",
            "explanation": "Standard wheat grain flour. Contains gluten.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "gluten",
            "safer_alternatives": "Rice flour, Almond flour, Coconut flour, Gluten-free flour blend.",
            "aliases": ["flour", "wheat starch", "refined wheat flour", "all purpose flour", "semolina", "maida"],
            "allergens": [("Wheat/gluten", "DIRECT")]
        },
        {
            "canonical_name": "Rice Flour",
            "category": "Grain",
            "explanation": "Gluten-free flour made from ground rice.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "gluten_free",
            "safer_alternatives": "Oat flour, Tapioca starch.",
            "aliases": ["ground rice", "rice starch"],
            "allergens": []
        },
        {
            "canonical_name": "Egg Powder",
            "category": "Poultry Product",
            "explanation": "Dehydrated whole egg. High binding and protein content.",
            "vegan_status": "NO",
            "vegetarian_status": "YES",
            "dietary_tags": "egg",
            "safer_alternatives": "Applesauce, Flaxseed meal egg replacements, Chia seed gel.",
            "aliases": ["eggs", "dehydrated egg", "egg white", "egg yolk", "albumin"],
            "allergens": [("Egg", "DIRECT")]
        },
        {
            "canonical_name": "Sesame Seed",
            "category": "Seed",
            "explanation": "Small, oil-rich seeds. Can trigger allergic reactions.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "seeds",
            "safer_alternatives": "Sunflower seeds, Pumpkin seeds.",
            "aliases": ["sesame", "sesame oil", "tahini", "gingelly oil"],
            "allergens": [("Sesame", "DIRECT")]
        },
        {
            "canonical_name": "Gelatin",
            "category": "Thickener",
            "explanation": "An animal protein prepared from the collagen of bones and skins.",
            "vegan_status": "NO",
            "vegetarian_status": "NO",
            "dietary_tags": "animal_derived",
            "safer_alternatives": "Agar-agar, Pectin, Carrageenan.",
            "aliases": ["gelatine", "beef gelatin", "pork gelatin"],
            "allergens": []
        },
        {
            "canonical_name": "Carmine",
            "category": "Coloring",
            "explanation": "A bright red pigment obtained from crushed cochineal scale insects.",
            "vegan_status": "NO",
            "vegetarian_status": "NO",
            "dietary_tags": "animal_derived,artificial_color",
            "safer_alternatives": "Beetroot juice extract, Annatto, Lycopene red.",
            "aliases": ["cochineal", "cochineal extract", "carminic acid", "E120", "Natural Red 4"],
            "allergens": []
        },
        {
            "canonical_name": "Citric Acid",
            "category": "Preservative",
            "explanation": "A weak organic acid found in citrus fruits. Used as a natural preservative and sour flavor.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "preservative",
            "safer_alternatives": "Lemon juice, Malic acid, Tartaric acid.",
            "aliases": ["E330", "citrate"],
            "allergens": []
        },
        {
            "canonical_name": "Maltodextrin",
            "category": "Additive",
            "explanation": "A polysaccharide used as a food additive. Has a high glycemic index (causes quick blood sugar spikes).",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "high_glycemic",
            "safer_alternatives": "Pectin, Tapioca starch.",
            "aliases": ["maltodextrin powder"],
            "allergens": []
        },
        {
            "canonical_name": "High Fructose Corn Syrup",
            "category": "Sweetener",
            "explanation": "An industrial sweetener made from corn starch. Strongly linked to insulin resistance and obesity.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "high_sugar",
            "safer_alternatives": "Pure maple syrup, Honey (non-vegan), Stevia, Monk fruit extract.",
            "aliases": ["HFCS", "corn syrup", "isoglucose"],
            "allergens": []
        },
        {
            "canonical_name": "Sodium Benzoate",
            "category": "Preservative",
            "explanation": "A chemical preservative commonly used in acidic foods. Can be high in sodium.",
            "vegan_status": "YES",
            "vegetarian_status": "YES",
            "dietary_tags": "high_sodium,preservative",
            "safer_alternatives": "Natural fermentation, Citric acid, Rosemary extract.",
            "aliases": ["E211", "benzoate of soda"],
            "allergens": []
        }
    ]

    ingredients_data.extend([
        {
            "canonical_name": "Chickpea Flour",
            "category": "Pulse",
            "explanation": "Ground Bengal gram, commonly called besan. A plant protein used in namkeen, pakora and batter mixes.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "pulse,gluten_free",
            "safer_alternatives": "Rice flour, Moong dal flour.",
            "aliases": ["besan", "gram flour", "bengal gram flour", "chana flour"], "allergens": []
        },
        {
            "canonical_name": "Chickpeas",
            "category": "Pulse",
            "explanation": "Whole chickpeas, also known as chana or garbanzo beans, used in snacks, curries and ready meals.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "pulse,high_protein",
            "safer_alternatives": "Green gram, Lentils.",
            "aliases": ["chana", "kabuli chana", "chick pea", "garbanzo beans"], "allergens": []
        },
        {
            "canonical_name": "Lentils",
            "category": "Pulse",
            "explanation": "Edible split pulses used in dals, instant mixes, soups and savoury snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "pulse,high_protein",
            "safer_alternatives": "Chickpeas, Green gram.",
            "aliases": ["dal", "dhal", "masoor dal", "red lentils"], "allergens": []
        },
        {
            "canonical_name": "Green Gram",
            "category": "Pulse",
            "explanation": "Mung bean or moong dal, a common pulse in Indian snacks, dosa mixes and ready-to-cook foods.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "pulse,high_protein",
            "safer_alternatives": "Chickpea flour, Lentils.",
            "aliases": ["moong dal", "mung bean", "green gram dal", "moong"], "allergens": []
        },
        {
            "canonical_name": "Corn Starch",
            "category": "Starch",
            "explanation": "Fine starch from corn used to thicken sauces and improve the crispness of fried or baked snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "starch,gluten_free",
            "safer_alternatives": "Tapioca starch, Rice starch.",
            "aliases": ["corn flour", "maize starch", "corn starch powder"], "allergens": []
        },
        {
            "canonical_name": "Oats",
            "category": "Grain",
            "explanation": "Whole or rolled oats used in breakfast mixes, biscuits and granola-style snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "grain,high_fiber",
            "safer_alternatives": "Rice flakes, Millet flakes.",
            "aliases": ["oat flour", "rolled oats", "whole oats"], "allergens": []
        },
        {
            "canonical_name": "Coconut",
            "category": "Fruit and Seed",
            "explanation": "Coconut flesh or powder used in sweets, curry pastes, snack coatings and bakery products.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "tree_nut_related",
            "safer_alternatives": "Sunflower seed, Sesame seed.",
            "aliases": ["desiccated coconut", "coconut powder", "copra", "coconut milk"], "allergens": []
        },
        {
            "canonical_name": "Cashew",
            "category": "Tree Nut",
            "explanation": "Tree nut used in sweets, gravies, trail mixes and premium savoury snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "tree_nut,high_fat",
            "safer_alternatives": "Roasted chickpeas, Pumpkin seeds.",
            "aliases": ["cashew nut", "kaju", "cashew pieces", "kaju paste"], "allergens": [("Tree nuts", "DIRECT")]
        },
        {
            "canonical_name": "Almond",
            "category": "Tree Nut",
            "explanation": "Tree nut found in Indian sweets, health bars, cereals and flavoured milk products.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "tree_nut,high_fat",
            "safer_alternatives": "Sunflower seeds, Pumpkin seeds.",
            "aliases": ["almond nut", "badam", "almond powder", "almond meal"], "allergens": [("Tree nuts", "DIRECT")]
        },
        {
            "canonical_name": "Palmolein Oil",
            "category": "Edible Oil",
            "explanation": "Refined palm olein frequently used for frying namkeen, chips and instant snack products.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "refined_oil,high_fat",
            "safer_alternatives": "Groundnut oil, Rice bran oil, Sunflower oil.",
            "aliases": ["refined palmolein", "palm oil", "refined palm oil"], "allergens": []
        },
        {
            "canonical_name": "Sunflower Oil",
            "category": "Edible Oil",
            "explanation": "A neutral cooking oil commonly used in packaged snacks, savouries and ready-to-eat foods.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "edible_oil,high_fat",
            "safer_alternatives": "Rice bran oil, Mustard oil.",
            "aliases": ["refined sunflower oil", "sunflower seed oil"], "allergens": []
        },
        {
            "canonical_name": "Rice Bran Oil",
            "category": "Edible Oil",
            "explanation": "Cooking oil extracted from rice bran and used in fried snacks and ready meals.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "edible_oil,high_fat",
            "safer_alternatives": "Sunflower oil, Groundnut oil.",
            "aliases": ["rice bran", "refined rice bran oil"], "allergens": []
        },
        {
            "canonical_name": "Mustard Seed",
            "category": "Spice",
            "explanation": "A pungent seed used in pickles, spice blends, chutneys and Indian savoury foods.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "Cumin, Fennel.",
            "aliases": ["mustard", "rai", "sarson", "mustard oil"], "allergens": []
        },
        {
            "canonical_name": "Turmeric",
            "category": "Spice",
            "explanation": "Haldi, an earthy yellow spice used in curry powders, soups, snacks and ready meals.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "No direct substitute required.",
            "aliases": ["haldi", "turmeric powder", "curcuma"], "allergens": []
        },
        {
            "canonical_name": "Cumin",
            "category": "Spice",
            "explanation": "Jeera seed or powder used in masala blends, namkeen, instant mixes and savoury foods.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "Coriander, Fennel.",
            "aliases": ["jeera", "cumin powder", "cumin seed"], "allergens": []
        },
        {
            "canonical_name": "Coriander",
            "category": "Spice",
            "explanation": "Dhania seed or powder used in curry powders, chutneys and packaged masala blends.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "Cumin, Fennel.",
            "aliases": ["dhania", "coriander powder", "coriander seed"], "allergens": []
        },
        {
            "canonical_name": "Monosodium Glutamate",
            "category": "Flavour Enhancer",
            "explanation": "MSG, also called Ajinomoto, is used to intensify savoury flavour in noodles, soups, chips and namkeen.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "flavour_enhancer",
            "safer_alternatives": "Yeast extract, Mushroom powder.",
            "aliases": ["MSG", "ajinomoto", "INS 621", "E621"], "allergens": []
        },
        {
            "canonical_name": "Baking Soda",
            "category": "Leavening Agent",
            "explanation": "Sodium bicarbonate used to aerate biscuits, batters, breads and savoury mixes.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "leavening_agent",
            "safer_alternatives": "Baking powder, Yeast.",
            "aliases": ["sodium bicarbonate", "bicarbonate of soda", "cooking soda"], "allergens": []
        }
    ])

    ingredients_data.extend([
        {
            "canonical_name": "Potato",
            "category": "Vegetable", "explanation": "A common base for chips, aloo bhujia, patties and ready-to-eat Indian snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "vegetable",
            "safer_alternatives": "Sweet potato, Roasted chickpeas.", "aliases": ["potatoes", "aloo", "dehydrated potato"], "allergens": []
        },
        {
            "canonical_name": "Tomato",
            "category": "Vegetable", "explanation": "Tomato powder, puree or concentrate used in sauces, soups, noodles and masala snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "vegetable",
            "safer_alternatives": "Tamarind, Kokum.", "aliases": ["tomato powder", "tomato puree", "tomato paste"], "allergens": []
        },
        {
            "canonical_name": "Red Chilli",
            "category": "Spice", "explanation": "Lal mirch used for heat and colour in namkeen, spice mixes, sauces and instant foods.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "Black pepper, Paprika.", "aliases": ["red chilli powder", "lal mirch", "chilli pepper", "cayenne"], "allergens": []
        },
        {
            "canonical_name": "Black Pepper",
            "category": "Spice", "explanation": "Kali mirch used in seasoning blends, soups, chips and savoury ready meals.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "White pepper, Cumin.", "aliases": ["black pepper powder", "kali mirch", "pepper"], "allergens": []
        },
        {
            "canonical_name": "Garlic",
            "category": "Spice", "explanation": "Garlic powder or dehydrated garlic used in seasoning, sauces, noodles and savoury snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "Onion powder, Asafoetida.", "aliases": ["garlic powder", "dehydrated garlic", "lahsun"], "allergens": []
        },
        {
            "canonical_name": "Onion",
            "category": "Vegetable", "explanation": "Onion powder or dehydrated onion used in masala blends, chips, soups and instant noodles.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "vegetable",
            "safer_alternatives": "Garlic powder, Chives.", "aliases": ["onion powder", "dehydrated onion", "pyaz"], "allergens": []
        },
        {
            "canonical_name": "Ginger",
            "category": "Spice", "explanation": "Adrak powder or extract used in chai mixes, sauces, spice blends and ready meals.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "No direct substitute required.", "aliases": ["ginger powder", "adrak", "dry ginger"], "allergens": []
        },
        {
            "canonical_name": "Asafoetida",
            "category": "Spice", "explanation": "Hing used in dal, namkeen, pickles and spice mixes; some commercial blends contain wheat flour.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "spice",
            "safer_alternatives": "Garlic powder, Onion powder.", "aliases": ["hing", "compounded asafoetida", "asafoetida powder"], "allergens": []
        },
        {
            "canonical_name": "Tamarind",
            "category": "Fruit", "explanation": "Imli pulp or powder used in chutneys, sauces, instant meals and savoury snack seasonings.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "fruit",
            "safer_alternatives": "Kokum, Citric acid.", "aliases": ["imli", "tamarind pulp", "tamarind powder"], "allergens": []
        },
        {
            "canonical_name": "Jaggery",
            "category": "Sweetener", "explanation": "Gur, an unrefined cane sweetener found in chikki, ladoo, cereal bars and traditional snacks.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "high_sugar",
            "safer_alternatives": "Stevia, Erythritol.", "aliases": ["gur", "gud", "cane jaggery", "jaggery powder"], "allergens": []
        },
        {
            "canonical_name": "Honey",
            "category": "Sweetener", "explanation": "A bee-derived sweetener used in breakfast foods, biscuits, granola and wellness drinks.",
            "vegan_status": "NO", "vegetarian_status": "YES", "dietary_tags": "high_sugar,animal_derived",
            "safer_alternatives": "Date syrup, Maple syrup, Stevia.", "aliases": ["honey powder", "wildflower honey"], "allergens": []
        },
        {
            "canonical_name": "Cocoa Powder",
            "category": "Cocoa", "explanation": "Unsweetened cocoa used in chocolate biscuits, drinks, cereal and confectionery.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "cocoa",
            "safer_alternatives": "Carob powder.", "aliases": ["cocoa", "cacao powder", "cocoa solids"], "allergens": []
        },
        {
            "canonical_name": "Skim Milk Powder",
            "category": "Dairy", "explanation": "Dried low-fat milk used in biscuits, tea whiteners, chocolate, instant mixes and confectionery.",
            "vegan_status": "NO", "vegetarian_status": "YES", "dietary_tags": "dairy,high_protein",
            "safer_alternatives": "Coconut milk powder, Oat milk powder.", "aliases": ["skimmed milk powder", "milk powder", "dry milk"], "allergens": [("Milk", "DERIVATIVE")]
        },
        {
            "canonical_name": "Tapioca Starch",
            "category": "Starch", "explanation": "Sabudana or cassava starch used in vrat snacks, papad, instant mixes and thickened foods.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "starch,gluten_free",
            "safer_alternatives": "Rice starch, Potato starch.", "aliases": ["sabudana", "sago", "cassava starch", "tapioca flour"], "allergens": []
        },
        {
            "canonical_name": "Yeast Extract",
            "category": "Flavour Enhancer", "explanation": "A savoury flavouring used in noodles, soups, seasoning powders and snack coatings.",
            "vegan_status": "YES", "vegetarian_status": "YES", "dietary_tags": "flavour_enhancer",
            "safer_alternatives": "Mushroom powder, Herb seasoning.", "aliases": ["autolyzed yeast", "yeast extract powder"], "allergens": []
        }
    ])

    for ing in ingredients_data:
        # Check if ingredient exists
        existing_ing = db.execute_query_one("SELECT id FROM ingredients WHERE canonical_name = ?", (ing['canonical_name'],))
        if not existing_ing:
            ing_id = db.execute_write(
                "INSERT INTO ingredients (canonical_name, category, explanation, vegan_status, vegetarian_status, dietary_tags, safer_alternatives) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ing['canonical_name'], ing['category'], ing['explanation'], ing['vegan_status'], ing['vegetarian_status'], ing['dietary_tags'], ing['safer_alternatives'])
            )
        else:
            ing_id = existing_ing['id']

        # Add aliases
        for alias in ing['aliases']:
            existing_alias = db.execute_query_one("SELECT id FROM ingredient_aliases WHERE alias_name = ?", (alias,))
            if not existing_alias:
                db.execute_write("INSERT INTO ingredient_aliases (ingredient_id, alias_name) VALUES (?, ?)", (ing_id, alias))

        # Add ingredient allergens
        for allergen_name, risk_level in ing['allergens']:
            allergen_id = allergen_map.get(allergen_name)
            if allergen_id:
                existing_rel = db.execute_query_one(
                    "SELECT ingredient_id FROM ingredient_allergens WHERE ingredient_id = ? AND allergen_id = ?",
                    (ing_id, allergen_id)
                )
                if not existing_rel:
                    db.execute_write(
                        "INSERT INTO ingredient_allergens (ingredient_id, allergen_id, risk_level) VALUES (?, ?, ?)",
                        (ing_id, allergen_id, risk_level)
                    )

    # 3. Seed Demo Users
    users_data = [
        {
            "username": "usera",
            "password": "Password123",
            "age_range": "25-34",
            "vegetarian": 1,
            "vegan": 0,
            "allergies": ["Milk"],
            "preferences": ["Organic"],
            "avoid_ingredients": []
        },
        {
            "username": "userb",
            "password": "Password123",
            "age_range": "35-44",
            "vegetarian": 1,
            "vegan": 1,
            "allergies": ["Peanut"],
            "preferences": [],
            "avoid_ingredients": ["Gelatin"]
        },
        {
            "username": "userc",
            "password": "Password123",
            "age_range": "18-24",
            "vegetarian": 0,
            "vegan": 0,
            "allergies": ["Soy"],
            "preferences": ["Low Sugar"],
            "avoid_ingredients": ["Sodium Benzoate"]
        }
    ]

    for u in users_data:
        existing_user = db.execute_query_one("SELECT id FROM users WHERE username = ?", (u['username'],))
        if not existing_user:
            # Create user
            pass_hash = generate_password_hash(u['password'])
            user_id = db.execute_write("INSERT INTO users (username, password_hash) VALUES (?, ?)", (u['username'], pass_hash))
            
            # Create profile
            db.execute_write(
                "INSERT INTO user_profiles (user_id, age_range, vegetarian_status, vegan_status) VALUES (?, ?, ?, ?)",
                (user_id, u['age_range'], u['vegetarian'], u['vegan'])
            )
            
            # Add allergies
            for allergy_name in u['allergies']:
                allergen_id = allergen_map.get(allergy_name)
                if allergen_id:
                    db.execute_write("INSERT INTO user_allergies (user_id, allergen_id) VALUES (?, ?)", (user_id, allergen_id))

            # Add preferences
            for pref in u['preferences']:
                db.execute_write("INSERT INTO user_preferences (user_id, preference_tag) VALUES (?, ?)", (user_id, pref))

            # Add avoid ingredients
            for avoid in u['avoid_ingredients']:
                db.execute_write("INSERT INTO user_avoid_ingredients (user_id, ingredient_name) VALUES (?, ?)", (user_id, avoid))
                
            print(f"Demo user '{u['username']}' seeded successfully.")
        else:
            print(f"Demo user '{u['username']}' already exists. Skipping.")

    print("Database seeding completed.")

if __name__ == "__main__":
    # Ensure tables are setup before seeding
    db.init_db("database/schema.sql")
    seed_database()
