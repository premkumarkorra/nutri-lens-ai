import json
import os
import re
from urllib import request, error

class ProductIdentificationEngine:
    """
    Ingredient-to-Food-Product Identification and Recommendation Engine.
    Identifies real-world packaged food products from ingredients, provides
    evidence-based reviews, and recommends specific finished food products
    as alternatives (never raw ingredients).
    """

    # Comprehensive Food Products Knowledge Base
    PRODUCT_DATABASE = [
        # --- POTATO CHIPS & SAVORY SNACKS ---
        {
            "id": "lays_magic_masala",
            "name": "Lay's India's Magic Masala Potato Chips",
            "brand": "Lay's (PepsiCo)",
            "category": "Potato Chips & Savory Snacks",
            "primary_base": "potato",
            "signature_ingredients": [
                "potato",
                "palm oil",
                "salt",
                "red chilli powder",
                "spices and condiments",
                "onion powder",
                "garlic powder"
            ],
            "optional_ingredients": [
                "maltodextrin",
                "refined wheat flour",
                "black salt",
                "milk solids",
                "sugar",
                "tomato powder",
                "hydrolysed groundnut protein",
                "flavour enhancers",
                "dry mango powder",
                "coriander powder",
                "vegetable oil"
            ],
            "negative_markers": ["cocoa", "chocolate", "oats", "cheese", "noodle", "pasta", "rice meal", "corn meal"],
            "taste_profile": "Spicy, tangy (amchur/dry mango), savory with rich onion, garlic, and aromatic Indian masala undertones on a crisp potato chip.",
            "pros": [
                "Distinctive bold Indian spice blend formulation",
                "Made from whole farm-grown sliced potatoes",
                "Consistent thin-cut crisp texture"
            ],
            "cons": [
                "Contains flavour enhancers (INS 508 / potassium chloride, INS 627, INS 631)",
                "High in sodium and saturated fats from refined palmolein",
                "Added sugar in seasoning blend"
            ],
            "overall": "India's most popular spiced potato chip with intense masala tang and heat. Highly flavorful for occasional snacking, though portion control is recommended due to palmolein and sodium.",
            "alternative": {
                "name": "Bingo! Tedhe Medhe (Masala Tadka)",
                "brand": "Bingo! (ITC)",
                "reason": "Provides a similar zesty Indian spice kick made from a multigrain pulse and corn base."
            },
            "verified": True
        },
        {
            "id": "lays_classic",
            "name": "Lay's Classic Potato Chips",
            "brand": "Lay's (PepsiCo)",
            "category": "Potato Chips & Savory Snacks",
            "primary_base": "potato",
            "signature_ingredients": ["potato", "palm oil", "salt"],
            "optional_ingredients": ["vegetable oil", "sunflower oil", "iodized salt"],
            "negative_markers": ["cocoa", "refined wheat flour", "sugar", "chilli", "onion", "garlic", "cheese", "noodle", "tomato powder", "maltodextrin"],
            "taste_profile": "Crisp, light, lightly salted with a pure potato crunch.",
            "pros": [
                "Simple 3-ingredient formulation with no artificial preservatives",
                "Naturally gluten-free snack base",
                "Consistent thin-cut crisp texture"
            ],
            "cons": [
                "High in saturated fat from palmolein/vegetable oil",
                "High sodium content per serving",
                "High glycemic index snack"
            ],
            "overall": "A classic salted potato chip with a minimalist ingredient list. While free from synthetic additives, it remains a calorie-dense snack high in sodium and fats.",
            "alternative": {
                "name": "Too Yumm! Baked Potato Chips (Classic Salted)",
                "brand": "Too Yumm!",
                "reason": "Offers 40% less fat as a baked alternative without deep frying in palmolein, retaining classic salted flavor."
            },
            "verified": True
        },
        {
            "id": "kurkure_masala_munch",
            "name": "Kurkure Masala Munch",
            "brand": "Kurkure (PepsiCo)",
            "category": "Extruded Corn & Grain Snacks",
            "primary_base": "rice meal",
            "signature_ingredients": ["rice meal", "palm oil", "corn meal", "gram meal", "spices and condiments", "salt", "sugar"],
            "optional_ingredients": ["vegetable oil", "onion powder", "chilli powder", "garlic powder", "coriander powder", "acidity regulator", "flavour enhancers"],
            "negative_markers": ["cocoa", "potato", "chocolate", "noodle"],
            "taste_profile": "Crunchy, spicy, tangy masala crunch with roasted grain undertones.",
            "pros": [
                "Made with Indian kitchen ingredients (rice, corn, gram/besan)",
                "Trans-fat free formulation"
            ],
            "cons": [
                "Deep-fried in refined palmolein oil",
                "High sodium and acidity from seasoning",
                "High calorie density"
            ],
            "overall": "An iconic extruded spicy snack combining rice, corn, and besan. Satisfyingly crunchy and spicy, but best consumed in moderation due to palmolein and sodium.",
            "alternative": {
                "name": "Soulfull Ragi Bites (Masala)",
                "brand": "Tata Soulfull",
                "reason": "Made from whole millets (Ragi) with 70% less fat and higher dietary fiber while satisfying savory masala cravings."
            },
            "verified": True
        },
        {
            "id": "bingo_tedhe_medhe_masala_tadka",
            "name": "Bingo! Tedhe Medhe (Masala Tadka)",
            "brand": "Bingo! (ITC)",
            "category": "Extruded Rice and Pulse Snacks",
            "primary_base": "rice meal",
            "signature_ingredients": [
                "rice meal", "palm oil", "maltodextrin", "black salt",
                "garlic powder", "tomato powder", "gram meal"
            ],
            "optional_ingredients": [
                "corn meal", "spices and condiments", "onion powder", "flavour enhancers",
                "hydrolysed vegetable protein", "acidity regulator", "sugar"
            ],
            "negative_markers": ["potato", "cocoa", "chocolate", "noodle", "wheat flour"],
            "taste_profile": "A crunchy, seasoned rice and pulse snack with savory Indian spices.",
            "pros": ["Rice and pulse based extruded snack", "Seasoned savory flavor"],
            "cons": ["Seasoned packaged snack; sodium and oil content depend on the variant"],
            "overall": "The ingredient pattern is consistent with a Bingo! Tedhe Medhe style extruded snack. Check the flavor and current package label to confirm the exact variant.",
            "alternative": {
                "name": "Kurkure Masala Munch",
                "brand": "Kurkure (PepsiCo)",
                "reason": "A similar seasoned extruded grain snack; compare the ingredient and allergen statements on the packs."
            },
            "verified": False
        },
        {
            "id": "bingo_seasoned_potato_chips",
            "name": "Bingo! Potato Chips (Seasoned)",
            "brand": "Bingo! (ITC)",
            "category": "Potato Chips & Savory Snacks",
            "primary_base": "potato",
            "signature_ingredients": [
                "potato", "palm oil", "sugar", "salt", "spices and condiments",
                "garlic", "dehydrated onion", "acidity regulator", "flavour enhancers"
            ],
            "optional_ingredients": ["vegetable oil", "nature identical flavouring substances", "natural flavours"],
            "negative_markers": ["cocoa", "noodle", "rice meal", "corn meal", "cheese powder"],
            "taste_profile": "Seasoned potato chips with savory spices and onion and garlic notes.",
            "pros": ["Potato based snack with a seasoned flavor profile"],
            "cons": ["Seasoned packaged chips; sodium and oil content depend on the flavor"],
            "overall": "The potato, palmolein, seasoning, acidity regulator, and flavor enhancer pattern is consistent with Bingo! seasoned potato chips. The exact flavor should be confirmed from the front of the pack.",
            "alternative": {
                "name": "Lay's India's Magic Masala Potato Chips",
                "brand": "Lay's (PepsiCo)",
                "reason": "A similar seasoned potato chip; compare the seasoning and allergen statements on the package."
            },
            "verified": False
        },
        {
            "id": "bingo_original",
            "name": "Bingo! Original Style Potato Chips (Salted)",
            "brand": "Bingo! (ITC)",
            "category": "Potato Chips & Savory Snacks",
            "primary_base": "potato",
            "signature_ingredients": ["potato", "vegetable oil", "palm oil", "salt"],
            "optional_ingredients": ["sunflower oil", "iodized salt"],
            "negative_markers": ["cocoa", "refined wheat flour", "sugar", "chilli", "onion", "garlic", "noodle"],
            "taste_profile": "Extra crunchy, flat-cut salted potato chips with savory crispness.",
            "pros": [
                "Golden flat-cut crunch",
                "No artificial color or preservatives added"
            ],
            "cons": [
                "High in saturated fats from refined palm oil",
                "High sodium content"
            ],
            "overall": "A crisp, straightforward salted potato snack competing directly with classic potato wafers.",
            "alternative": {
                "name": "BRB Popped Potato Chips (Classic Salt)",
                "brand": "BRB",
                "reason": "Popped using heat and pressure instead of deep-frying, cutting fat content by 60%."
            },
            "verified": True
        },
        {
            "id": "haldirams_bhujia_sev",
            "name": "Haldiram's Bhujia Sev",
            "brand": "Haldiram's",
            "category": "Traditional Indian Namkeen",
            "primary_base": "tepary bean flour",
            "signature_ingredients": ["tepary bean flour", "gram meal", "vegetable oil", "salt", "red chilli powder", "black pepper", "ginger powder", "cardamom"],
            "optional_ingredients": ["cottonseed oil", "palmolein", "clove powder", "nutmeg"],
            "negative_markers": ["cocoa", "sugar cream", "potato", "noodle", "hazelnut"],
            "taste_profile": "Crisp, spicy, peppery, aromatic sev with distinctive moth/tepary bean savoriness.",
            "pros": [
                "Authentic Rajasthani recipe using moth dal flour (tepary bean)",
                "Naturally gluten-free pulse formulation",
                "Rich warming whole-spice aromatics"
            ],
            "cons": [
                "High total and saturated fat content",
                "Substantial sodium level",
                "Calorie dense"
            ],
            "overall": "The quintessential Bikaneri spicy bhujia sev with intense spice notes, best enjoyed in modest portions.",
            "alternative": {
                "name": "Haldiram's Roasted Diet Mixture",
                "brand": "Haldiram's",
                "reason": "Roasted grain and pulse mixture offering the satisfying spiced crunch with over 60% less oil."
            },
            "verified": True
        },
        {
            "id": "pringles_original",
            "name": "Pringles Original Potato Crisps",
            "brand": "Pringles (Kellogg's)",
            "category": "Potato Chips & Savory Snacks",
            "primary_base": "dried potatoes",
            "signature_ingredients": ["dried potatoes", "vegetable oil", "corn flour", "wheat starch", "rice flour", "emulsifier", "salt"],
            "optional_ingredients": ["maltodextrin", "e471", "palm oil", "sunflower oil"],
            "negative_markers": ["cocoa", "chilli powder", "onion powder", "meat", "noodle"],
            "taste_profile": "Uniformly hyperbolic, light, savory, melt-in-mouth reconstituted potato crisp.",
            "pros": [
                "Signature uniform saddle shape and canister crush protection",
                "Zero trans fat"
            ],
            "cons": [
                "Reconstituted flour-starch blend rather than sliced fresh potatoes",
                "Contains gluten/wheat starch (not gluten-free)",
                "High sodium and carbohydrate density"
            ],
            "overall": "A distinctively engineered stackable potato crisp known for shape consistency and crunch.",
            "alternative": {
                "name": "BRB Popped Potato Crisps (Salted)",
                "brand": "BRB",
                "reason": "Air-popped potato crisps with fewer processed starches and 60% reduced fat."
            },
            "verified": True
        },
        {
            "id": "doritos_nacho_cheese",
            "name": "Doritos Nacho Cheese Tortilla Chips",
            "brand": "Doritos (PepsiCo)",
            "category": "Corn Tortilla Chips",
            "primary_base": "corn",
            "signature_ingredients": ["corn", "vegetable oil", "cheese powder", "milk solids", "salt", "tomato powder", "onion powder", "garlic powder", "spices and condiments"],
            "optional_ingredients": ["palm oil", "sunflower oil", "whey powder", "flavour enhancers", "citric acid", "e627", "e631"],
            "negative_markers": ["cocoa", "potato", "refined wheat flour", "chocolate", "noodle"],
            "taste_profile": "Zesty, savory cheddar cheese tang on a robust roasted corn tortilla crunch.",
            "pros": [
                "Made with whole yellow corn grain",
                "Bold savory cheese seasoning profile"
            ],
            "cons": [
                "Contains flavour enhancers (INS 627, INS 631)",
                "High sodium and palm oil content",
                "Contains dairy allergens (cheese powder/milk solids)"
            ],
            "overall": "A globally popular triangular cheese tortilla chip offering rich corn crunch and bold seasoning.",
            "alternative": {
                "name": "Cornitos Baked Nacho Crisps (Sea Salt)",
                "brand": "Cornitos",
                "reason": "Non-GMO baked whole corn crisps with simpler seasoning and reduced sodium."
            },
            "verified": True
        },

        # --- COOKIES & BISCUITS ---
        {
            "id": "oreo_original",
            "name": "Oreo Original Sandwich Cookies",
            "brand": "Oreo (Mondelez)",
            "category": "Cookies & Sweet Biscuits",
            "primary_base": "refined wheat flour",
            "signature_ingredients": ["refined wheat flour", "sugar", "palm oil", "cocoa solids", "leavening agents", "salt", "soy lecithin"],
            "optional_ingredients": ["maida", "invert sugar", "high fructose corn syrup", "baking soda", "soybean andor canola oil", "natural and artificial flavor", "chocolate", "vanillin"],
            "negative_markers": ["potato", "chilli", "onion", "garlic", "noodle", "cheese powder", "meat"],
            "taste_profile": "Deep bittersweet dark chocolate wafer cookies with a sweet vanilla cream center.",
            "pros": [
                "Consistent cocoa flavor and crisp wafer texture",
                "Eggless / vegetarian recipe",
                "Zero trans fat"
            ],
            "cons": [
                "High refined sugar content (nearly 40% by weight)",
                "Contains refined palm oil and refined wheat flour (maida)",
                "Low in fiber and micronutrients"
            ],
            "overall": "A globally recognized chocolate cream sandwich cookie. Deliciously indulgent for occasional treats, but calorie-dense with refined flour and sugars.",
            "alternative": {
                "name": "Sunfeast Farmlite Digestive Choco Oats Biscuits",
                "brand": "Sunfeast",
                "reason": "Delivers genuine cocoa indulgence baked with whole oats and dietary fiber with zero maida."
            },
            "verified": True
        },
        {
            "id": "parle_g_biscuits",
            "name": "Parle-G Original Gluco Biscuits",
            "brand": "Parle",
            "category": "Cookies & Sweet Biscuits",
            "primary_base": "refined wheat flour",
            "signature_ingredients": ["refined wheat flour", "sugar", "vegetable oil", "invert sugar", "milk solids", "salt", "leavening agents"],
            "optional_ingredients": ["maida", "palm oil", "e503", "e500", "soy lecithin", "vanillin"],
            "negative_markers": ["cocoa", "potato", "chilli", "onion", "garlic", "noodle", "hazelnut"],
            "taste_profile": "Mildly sweet, malty, comforting wheat tea-biscuit.",
            "pros": [
                "Fortified with Glucose and Milk for energy",
                "Extremely accessible, affordable tea companion",
                "No artificial colors"
            ],
            "cons": [
                "Contains refined maida and palm oil",
                "Invert sugar syrup increases glycemic response"
            ],
            "overall": "India's largest-selling heritage glucose biscuit. Perfect companion for chai, but formulated with refined wheat flour and sugar.",
            "alternative": {
                "name": "Britannia NutriChoice Digestive 100% Atta Biscuits",
                "brand": "Britannia",
                "reason": "Baked with 100% whole wheat grain (Atta) offering dietary fiber with reduced sugar."
            },
            "verified": True
        },
        {
            "id": "sunfeast_dark_fantasy",
            "name": "Sunfeast Dark Fantasy Choco Fills",
            "brand": "Sunfeast (ITC)",
            "category": "Cookies & Sweet Biscuits",
            "primary_base": "refined wheat flour",
            "signature_ingredients": ["choco creme", "sugar", "refined wheat flour", "palm oil", "cocoa solids", "invert sugar", "leavening agents", "salt", "soy lecithin"],
            "optional_ingredients": ["hydrogenated vegetable oil", "maida", "e322", "e500", "e503", "vanillin"],
            "negative_markers": ["potato", "chilli", "onion", "garlic", "noodle", "meat", "high fructose corn syrup", "soybean andor canola oil", "baking soda"],
            "taste_profile": "Crisp golden cookie crust bursting with a molten, gooey dark chocolate center.",
            "pros": [
                "Rich molten chocolate core experience",
                "Eggless vegetarian dessert biscuit"
            ],
            "cons": [
                "High saturated fat from choco creme and hydrogenated fats",
                "High refined sugar content",
                "Calorie dense"
            ],
            "overall": "A luxurious dessert cookie with a molten chocolate center, best enjoyed as an occasional treat.",
            "alternative": {
                "name": "Sunfeast Farmlite Supergrains Choco Cookie",
                "brand": "Sunfeast",
                "reason": "Formulated with whole multigrains and real cocoa with less refined fats."
            },
            "verified": True
        },

        # --- INSTANT NOODLES & MEALS ---
        {
            "id": "maggi_masala_noodles",
            "name": "Maggi 2-Minute Noodles (Masala)",
            "brand": "Maggi (Nestlé)",
            "category": "Instant Noodles & Soups",
            "primary_base": "refined wheat flour",
            "signature_ingredients": ["refined wheat flour", "palm oil", "salt", "wheat gluten", "mineral", "hydrolysed groundnut protein", "onion powder", "garlic powder", "spices and condiments"],
            "optional_ingredients": ["maida", "calcium carbonate", "acidity regulator", "coriander powder", "turmeric powder", "chilli powder", "cumin powder", "flavour enhancers", "e635"],
            "negative_markers": ["potato", "cocoa", "sugar cream", "chocolate", "rice meal", "corn meal", "hazelnut"],
            "taste_profile": "Savory, aromatic Indian garam masala broth coating springy wheat noodles.",
            "pros": [
                "Fortified with Iron (Mineral)",
                "Rapid 2-minute cooking convenience",
                "Iconic familiar taste profile"
            ],
            "cons": [
                "Fried noodle cake using refined palm oil",
                "High sodium level in the tastemaker sachet",
                "Refined flour (maida) base with limited dietary fiber"
            ],
            "overall": "The quintessential quick-meal noodle in India. Convenient and comforting, though best balanced with added fresh vegetables due to sodium and refined flour.",
            "alternative": {
                "name": "Maggi Nutri-Licious Atta Masala Noodles",
                "brand": "Nestlé Maggi",
                "reason": "Made from 100% whole wheat flour (Atta) delivering more fiber and essential nutrients with the same signature masala tastemaker."
            },
            "verified": True
        },
        {
            "id": "yippee_magic_masala",
            "name": "Sunfeast YiPPee! Magic Masala Noodles",
            "brand": "YiPPee! (ITC)",
            "category": "Instant Noodles & Soups",
            "primary_base": "refined wheat flour",
            "signature_ingredients": ["refined wheat flour", "palm oil", "salt", "wheat gluten", "spices and condiments", "onion powder", "garlic powder", "tomato powder"],
            "optional_ingredients": ["maida", "dehydrated vegetables", "turmeric", "chilli", "acidity regulator", "flavour enhancers"],
            "negative_markers": ["potato", "cocoa", "chocolate", "rice meal", "corn meal"],
            "taste_profile": "Non-sticky, round-strand slurpy noodles in a mild sweet-tangy Indian masala broth.",
            "pros": [
                "Round noodle block minimizes strand breakage",
                "Includes dehydrated vegetable bits (carrot, beans)",
                "Non-sticky texture after cooking"
            ],
            "cons": [
                "Refined maida and palm oil fried noodle cake",
                "High sodium per serving"
            ],
            "overall": "A vibrant slurpy instant noodle alternative to Maggi featuring dehydrated vegetable inclusions.",
            "alternative": {
                "name": "YiPPee! Power Up Atta Noodles",
                "brand": "ITC YiPPee!",
                "reason": "Whole wheat flour noodles with vegetable additions for enhanced dietary fiber."
            },
            "verified": True
        },

        # --- CHOCOLATES & SPREADS ---
        {
            "id": "cadbury_dairy_milk",
            "name": "Cadbury Dairy Milk Chocolate",
            "brand": "Cadbury (Mondelez)",
            "category": "Chocolates & Confectionery",
            "primary_base": "sugar",
            "signature_ingredients": ["sugar", "milk solids", "cocoa butter", "cocoa solids", "emulsifiers"],
            "optional_ingredients": ["e442", "e476", "soy lecithin", "flavouring substances", "vanilla"],
            "negative_markers": ["potato", "spices and condiments", "chilli", "onion", "garlic", "refined wheat flour", "noodle"],
            "taste_profile": "Creamy, sweet, melt-in-mouth milk chocolate with smooth dairy richness.",
            "pros": [
                "Rich dairy content (glass and a half of milk promise)",
                "No artificial colors",
                "Silky melt-in-mouth cocoa butter texture"
            ],
            "cons": [
                "High refined sugar content (primary ingredient)",
                "Contains PGPR (INS 476) emulsifiers",
                "Calorie and saturated fat dense"
            ],
            "overall": "A household favorite milk chocolate known for its rich dairy creaminess. Great sweet comfort food, but should be consumed mindfully due to high sugar.",
            "alternative": {
                "name": "Amul 75% Single Origin Dark Chocolate",
                "brand": "Amul",
                "reason": "Significantly higher cocoa antioxidant solids with less than half the sugar and zero dairy fat additives."
            },
            "verified": True
        },
        {
            "id": "nestle_kitkat",
            "name": "Nestlé KitKat 4-Finger Wafer Bar",
            "brand": "Nestlé",
            "category": "Chocolates & Confectionery",
            "primary_base": "sugar",
            "signature_ingredients": ["sugar", "refined wheat flour", "milk solids", "cocoa butter", "cocoa solids", "palm kernel oil", "soy lecithin"],
            "optional_ingredients": ["maida", "e322", "leavening agents", "vanilla flavour"],
            "negative_markers": ["potato", "chilli", "onion", "garlic", "noodle", "meat"],
            "taste_profile": "Crisp, airy wafer fingers enveloped in smooth milk chocolate.",
            "pros": [
                "Iconic 'snap' wafer lightness",
                "100% certified sustainable cocoa (Nestlé Cocoa Plan)"
            ],
            "cons": [
                "Contains palm kernel oil in wafer fats",
                "High sugar to fiber ratio"
            ],
            "overall": "The classic break-time crispy chocolate wafer with balanced sweetness.",
            "alternative": {
                "name": "Amul Choco Crunch Biscuit Dark Chocolate Bar",
                "brand": "Amul",
                "reason": "Dark chocolate coating with whole wheat crispies and reduced cane sugar."
            },
            "verified": True
        },
        {
            "id": "nutella_hazelnut_spread",
            "name": "Nutella Hazelnut Spread with Cocoa",
            "brand": "Nutella (Ferrero)",
            "category": "Spreads & Sweet Condiments",
            "primary_base": "sugar",
            "signature_ingredients": ["sugar", "palm oil", "hazelnuts", "skimmed milk powder", "cocoa solids", "soy lecithin", "vanillin"],
            "optional_ingredients": ["fat-reduced cocoa", "e322", "hazelnut 13%", "milk solids"],
            "negative_markers": ["potato", "refined wheat flour", "chilli", "onion", "garlic", "salt savory", "noodle"],
            "taste_profile": "Velvety, rich, decadent roasted hazelnut blended with sweet cocoa.",
            "pros": [
                "Contains 13% real roasted hazelnuts",
                "Free from artificial colorings and preservatives",
                "Smooth spreadable texture"
            ],
            "cons": [
                "Sugar and palm oil constitute over 70% of total jar content",
                "High saturated fat and calorie content",
                "Contains dairy and tree nuts (major allergens)"
            ],
            "overall": "A world-renowned hazelnut cocoa spread. Outstanding taste and texture for breakfast treats, though sugar and palm oil represent the primary ingredients.",
            "alternative": {
                "name": "Pintola All Natural Dark Chocolate Peanut Butter",
                "brand": "Pintola",
                "reason": "Provides delicious cocoa richness powered by 100% roasted peanuts and dark cocoa, with 3x higher protein and no palm oil."
            },
            "verified": True
        },

        # --- DAIRY & SPREADS ---
        {
            "id": "amul_butter",
            "name": "Amul Pasteurized Salted Butter",
            "brand": "Amul (GCMMF)",
            "category": "Dairy Spreads",
            "primary_base": "butter",
            "signature_ingredients": ["butter", "salt", "permitted natural colour"],
            "optional_ingredients": ["milk fat", "annatto", "carotene", "pasteurized cream"],
            "negative_markers": ["cocoa", "sugar", "refined wheat flour", "potato", "chilli", "onion", "garlic", "noodle"],
            "taste_profile": "Rich, creamy, savory, subtly salty with pure dairy aroma.",
            "pros": [
                "Pure natural dairy fat with no hydrogenated oils",
                "Natural color from annatto seeds",
                "Rich source of fat-soluble Vitamin A"
            ],
            "cons": [
                "High in saturated fats and dietary cholesterol",
                "Added table salt increases sodium",
                "Calorie dense (720 kcal / 100g)"
            ],
            "overall": "India's iconic 'Utterly Butterly' salted table butter made from fresh dairy cream. Pure and wholesome in moderate culinary portions.",
            "alternative": {
                "name": "Amul Lite Bread Spread (Low Fat / Low Cholesterol)",
                "brand": "Amul",
                "reason": "Contains 35% less fat and 50% fewer calories while preserving the smooth buttery taste on bread and toast."
            },
            "verified": True
        },
        {
            "id": "epigamia_greek_yogurt",
            "name": "Epigamia Greek Yogurt (Natural / Plain)",
            "brand": "Epigamia (Drums Food)",
            "category": "Dairy & Yogurts",
            "primary_base": "pasteurized milk",
            "signature_ingredients": ["pasteurized milk", "milk solids", "active lactic cultures"],
            "optional_ingredients": ["double toned milk", "probiotic cultures"],
            "negative_markers": ["cocoa", "sugar", "palm oil", "potato", "refined wheat flour", "noodle"],
            "taste_profile": "Thick, creamy, velvety with a clean, mild tangy yogurt acidity.",
            "pros": [
                "High protein density (approx. 6g protein per 100g cup)",
                "Zero added refined sugar",
                "Traditional straining method yields rich natural thickness"
            ],
            "cons": [
                "Short refrigerated shelf life",
                "Contains lactose (dairy allergen)"
            ],
            "overall": "A nutrient-dense strained Greek yogurt offering double the protein of standard curd with zero added sugars.",
            "alternative": {
                "name": "Epigamia No Added Sugar Greek Yogurt (Wild Blueberry)",
                "brand": "Epigamia",
                "reason": "Fruit-infused Greek yogurt sweetened with real fruit puree rather than refined cane sugar."
            },
            "verified": True
        },

        # --- BEVERAGES & CEREALS ---
        {
            "id": "coca_cola_original",
            "name": "Coca-Cola Original Taste",
            "brand": "Coca-Cola",
            "category": "Carbonated Soft Drinks",
            "primary_base": "carbonated water",
            "signature_ingredients": ["carbonated water", "sugar", "acidity regulator", "caffeine", "caramel color", "natural flavours"],
            "optional_ingredients": ["phosphoric acid", "e338", "e150d", "caramel 150d"],
            "negative_markers": ["potato", "refined wheat flour", "milk", "vegetable oil", "salt savory", "noodle", "sodium benzoate", "citric acid", "coffee powder", "sucralose", "acesulfame potassium"],
            "taste_profile": "Bubbly, crisp, sweet cola with notes of citrus, spice, and vanilla.",
            "pros": [
                "Classic refreshing carbonation and distinctive taste",
                "Instant glucose energy boost"
            ],
            "cons": [
                "High sugar concentration (~10.6g per 100ml)",
                "Contains phosphoric acid which can affect dental enamel",
                "Zero essential nutrients or dietary fiber"
            ],
            "overall": "The world's most famous carbonated soft drink. Refreshing and sweet, but contains high levels of simple sugars and phosphoric acid.",
            "alternative": {
                "name": "Raw Pressery Coconut Water",
                "brand": "Raw Pressery",
                "reason": "Naturally refreshing beverage loaded with bio-available electrolytes and zero added refined sugars or chemical colorants."
            },
            "verified": True
        },
        {
            "id": "coca_cola_coffee_vanilla",
            "name": "Coca-Cola Coffee Vanilla",
            "brand": "Coca-Cola",
            "category": "Coffee-Flavored Carbonated Soft Drinks",
            "primary_base": "carbonated water",
            "signature_ingredients": [
                "carbonated water", "high fructose corn syrup", "coffee powder",
                "caffeine", "sucralose", "acesulfame potassium"
            ],
            "optional_ingredients": [
                "caramel color", "phosphoric acid", "natural flavors", "sodium benzoate", "potassium sorbate"
            ],
            "negative_markers": ["orange pulp", "milk", "vegetable oil", "potato", "wheat flour"],
            "taste_profile": "Coffee-flavored cola with vanilla flavoring.",
            "pros": ["The ingredient list identifies coffee powder and caffeine"],
            "cons": ["Contains added sweeteners and caffeine"],
            "overall": "Coffee powder and the listed sweeteners distinguish this coffee-flavored Coca-Cola variant from regular Coca-Cola. Check the exact product name and serving information on the package.",
            "alternative": {
                "name": "Coca-Cola Original Taste",
                "brand": "Coca-Cola",
                "reason": "The original cola variant has a different ingredient profile and does not use coffee powder."
            },
            "verified": False
        },
        {
            "id": "sprite_lemon_lime",
            "name": "Sprite Lemon-Lime Soft Drink",
            "brand": "Sprite (The Coca-Cola Company)",
            "category": "Carbonated Soft Drinks",
            "primary_base": "carbonated water",
            "signature_ingredients": [
                "carbonated water", "sugar", "sodium benzoate", "flavours"
            ],
            "optional_ingredients": ["acidity regulator", "citric acid", "sodium citrate", "natural flavoring substances", "natural flavours"],
            "negative_markers": ["caffeine", "caramel color", "orange pulp", "cocoa", "milk", "vegetable oil"],
            "taste_profile": "Carbonated lemon-lime flavored soft drink.",
            "pros": ["Caffeine-free formulation listed for the India Sprite product"],
            "cons": ["Contains added sugar in the regular formulation"],
            "overall": "This ingredient combination is a likely match for regular Sprite in India. Formulations vary by market and variant; check the exact pack.",
            "alternative": {
                "name": "Coca-Cola Original Taste",
                "brand": "Coca-Cola",
                "reason": "Another carbonated soft drink; it has a different flavor and ingredient profile."
            },
            "verified": False
        },
        {
            "id": "minute_maid_pulpy_orange",
            "name": "Minute Maid Pulpy Orange Fruit Drink",
            "brand": "Minute Maid (The Coca-Cola Company)",
            "category": "Orange Fruit Drinks",
            "primary_base": "water",
            "signature_ingredients": [
                "orange juice", "orange pulp", "sugar", "water"
            ],
            "optional_ingredients": [
                "acidity regulator", "citric acid", "antioxidant", "ascorbic acid", "flavour", "preservative"
            ],
            "negative_markers": ["carbonated water", "caffeine", "cocoa", "milk", "vegetable oil"],
            "taste_profile": "Orange fruit drink with juice and visible orange pulp.",
            "pros": ["Contains orange juice and orange pulp, as stated for the India product"],
            "cons": ["The standard formulation contains added sugar"],
            "overall": "This ingredient pattern is a likely match for Minute Maid Pulpy Orange. The juice percentage and formulation can vary; use the package label for exact details.",
            "alternative": {
                "name": "Minute Maid Pulpy Tropical Fruit Drink",
                "brand": "Minute Maid",
                "reason": "A related fruit drink variant; compare fruit ingredients and added sugar on the label."
            },
            "verified": False
        },
        {
            "id": "kelloggs_corn_flakes",
            "name": "Kellogg's Corn Flakes Original",
            "brand": "Kellogg's",
            "category": "Breakfast Cereals",
            "primary_base": "milled corn",
            "signature_ingredients": ["milled corn", "sugar", "barley malt extract", "salt", "vitamins and minerals"],
            "optional_ingredients": ["corn grits", "iron", "vitamin c", "vitamin b complex", "folic acid"],
            "negative_markers": ["cocoa", "chilli", "potato", "palm oil", "meat", "noodle"],
            "taste_profile": "Crisp, lightly toasted golden corn flakes with subtle malty sweetness.",
            "pros": [
                "Virtually fat-free (99% fat free)",
                "Fortified with essential B-vitamins, Vitamin C, and Iron",
                "Simple crispy breakfast staple"
            ],
            "cons": [
                "High Glycemic Index (GI > 80)",
                "Moderate added sugars in coating",
                "Low natural dietary fiber compared to oats/bran"
            ],
            "overall": "A classic morning cereal fortified with essential micronutrients. Quick and light, but lower in satiety fiber compared to whole grain cereals.",
            "alternative": {
                "name": "Quaker Rolled Wholegrain Oats",
                "brand": "Quaker (PepsiCo)",
                "reason": "100% whole grain providing natural beta-glucan soluble fiber for sustained energy, heart health, and zero added sugar."
            },
            "verified": True
        },
        {
            "id": "kissan_tomato_ketchup",
            "name": "Kissan Fresh Tomato Ketchup",
            "brand": "Kissan (Hindustan Unilever)",
            "category": "Condiments & Sauces",
            "primary_base": "tomato paste",
            "signature_ingredients": ["water", "tomato paste", "sugar", "salt", "acidity regulator", "preservative", "spices and condiments"],
            "optional_ingredients": ["e260", "e211", "onion powder", "garlic powder", "stabilizer", "e415", "sodium benzoate"],
            "negative_markers": ["cocoa", "potato", "palm oil", "refined wheat flour", "chocolate"],
            "taste_profile": "Sweet, tangy, smooth ripe-tomato glaze with subtle spice notes.",
            "pros": [
                "Made with 100% real ripe farm tomatoes",
                "Source of tomato lycopene antioxidant",
                "Zero fat content"
            ],
            "cons": [
                "High added sugar content (approx. 25-30%)",
                "Contains synthetic chemical preservatives (INS 211)",
                "High sodium level per tablespoon"
            ],
            "overall": "A ubiquitous sweet-tangy condiment made with real tomatoes. Enhances snacks easily, but users watching sugar intake should monitor portion size.",
            "alternative": {
                "name": "Heinz No Added Sugar Tomato Ketchup",
                "brand": "Heinz",
                "reason": "Crafted from sun-ripened tomatoes without added refined sugar, cutting calories by over 50%."
            },
            "verified": True
        }
    ]

    # Ingredient Normalization Dictionary
    SYNONYMS = {
        "palmolein": "palm oil",
        "edible vegetable oil (palmolein)": "palm oil",
        "edible vegetable oil (palm)": "palm oil",
        "refined palmolein": "palm oil",
        "palmolein oil": "palm oil",
        "fractionated palm oil": "palm oil",
        "palm kernel oil": "palm oil",
        "edible vegetable oil": "vegetable oil",
        "vegetable fat": "vegetable oil",
        "refined vegetable oil": "vegetable oil",
        "cottonseed oil": "vegetable oil",
        "sunflower oil": "vegetable oil",
        "refined wheat flour (maida)": "refined wheat flour",
        "maida": "refined wheat flour",
        "all purpose flour": "refined wheat flour",
        "wheat flour": "refined wheat flour",
        "enriched wheat flour": "refined wheat flour",
        "wheat starch": "wheat starch",
        "wheat gluten": "wheat gluten",
        "atta": "whole wheat flour",
        "whole wheat flour (atta)": "whole wheat flour",
        "whole wheat flour": "whole wheat flour",
        "iodised salt": "salt",
        "iodized salt": "salt",
        "common salt": "salt",
        "sodium chloride": "salt",
        "table salt": "salt",
        "black salt": "black salt",
        "sucrose": "sugar",
        "cane sugar": "sugar",
        "liquid glucose": "sugar",
        "invert sugar syrup": "invert sugar",
        "invert syrup": "invert sugar",
        "invert sugar": "invert sugar",
        "maltodextrin": "maltodextrin",
        "cocoa solids": "cocoa solids",
        "cocoa": "cocoa solids",
        "cocoa powder": "cocoa solids",
        "fat-reduced cocoa powder": "cocoa solids",
        "fat-reduced cocoa": "cocoa solids",
        "cocoa mass": "cocoa solids",
        "cocoa butter": "cocoa butter",
        "unbleached enriched flour": "refined wheat flour",
        "soybean andor canola oil": "vegetable oil",
        "high fructose corn syrup": "high fructose corn syrup",
        "natural and artificial flavor": "natural and artificial flavor",
        "chocolate": "chocolate",
        "coffee powder": "coffee powder",
        "sucralose": "sucralose",
        "acesulfame potassium": "acesulfame potassium",
        "potassium sorbate": "potassium sorbate",
        "dehydrated onion": "dehydrated onion",
        "garlic": "garlic",
        "nature identical flavouring substances": "nature identical flavouring substances",
        "milk solids": "milk solids",
        "skimmed milk powder": "skimmed milk powder",
        "skim milk powder": "skimmed milk powder",
        "whole milk powder": "milk solids",
        "whey protein isolate": "whey protein isolate",
        "whey powder": "milk solids",
        "sweet whey powder": "milk solids",
        "pasteurized milk": "pasteurized milk",
        "double toned milk": "pasteurized milk",
        "milk fat": "butter",
        "pasteurized cream": "butter",
        "soya lecithin": "soy lecithin",
        "soy lecithin (e322)": "soy lecithin",
        "soy lecithin (ins 322)": "soy lecithin",
        "lecithin": "soy lecithin",
        "e322": "soy lecithin",
        "ins 322": "soy lecithin",
        "ins 322(i)": "soy lecithin",
        "e500": "leavening agents",
        "211": "sodium benzoate",
        "e211": "sodium benzoate",
        "ins 211": "sodium benzoate",
        "sodium benzoate": "sodium benzoate",
        "ins 500(ii)": "leavening agents",
        "ins 500": "leavening agents",
        "e503": "leavening agents",
        "ins 503(ii)": "leavening agents",
        "ins 503": "leavening agents",
        "baking soda": "leavening agents",
        "sodium bicarbonate": "leavening agents",
        "ammonium bicarbonate": "leavening agents",
        "raising agents": "leavening agents",
        "spices & condiments": "spices and condiments",
        "mixed spices": "spices and condiments",
        "spices and condiments": "spices and condiments",
        "onion powder": "onion powder",
        "garlic powder": "garlic powder",
        "chilli powder": "chilli powder",
        "red chilli powder": "red chilli powder",
        "red chilli powder (1.1%)": "red chilli powder",
        "dry mango powder": "dry mango powder",
        "amchur": "dry mango powder",
        "turmeric powder": "turmeric powder",
        "coriander powder": "coriander powder",
        "black pepper": "black pepper",
        "ginger powder": "ginger powder",
        "cardamom": "cardamom",
        "tomato powder": "tomato powder",
        "citric acid": "acidity regulator",
        "e330": "acidity regulator",
        "ins 330": "acidity regulator",
        "e260": "acidity regulator",
        "ins 260": "acidity regulator",
        "e338": "acidity regulator",
        "ins 338": "acidity regulator",
        "phosphoric acid": "acidity regulator",
        "flavour enhancer (627)": "flavour enhancers",
        "flavour enhancer (631)": "flavour enhancers",
        "flavour enhancer (ins 508)": "flavour enhancers",
        "flavour enhancer": "flavour enhancers",
        "ins 508": "flavour enhancers",
        "ins 627": "flavour enhancers",
        "ins 631": "flavour enhancers",
        "ins 635": "flavour enhancers",
        "e627": "flavour enhancers",
        "e631": "flavour enhancers",
        "msg": "monosodium glutamate",
        "hydrolysed groundnut protein": "hydrolysed groundnut protein",
        "hydrolyzed vegetable protein": "hydrolysed vegetable protein",
        "hydrolysed vegetable protein": "hydrolysed vegetable protein",
        "hvp": "hydrolysed vegetable protein",
        "rice meal": "rice meal",
        "rice grits": "rice meal",
        "corn meal": "corn meal",
        "degermed corn grits": "corn meal",
        "corn grits": "milled corn",
        "milled corn": "milled corn",
        "gram meal": "gram meal",
        "bengal gram grits": "gram meal",
        "gram flour": "gram meal",
        "besan": "gram meal",
        "tepary bean flour": "tepary bean flour",
        "moth flour": "tepary bean flour",
        "hazelnuts": "hazelnuts",
        "hazelnut paste": "hazelnuts",
        "vanillin": "vanillin",
        "ethyl vanillin": "vanillin",
        "caffeine": "caffeine",
        "carbonated water": "carbonated water",
        "caramel color": "caramel color",
        "ins 150d": "caramel color",
        "e150d": "caramel color",
        "tomato paste": "tomato paste",
        "tomato puree": "tomato paste",
        "cheese powder": "cheese powder",
        "active lactic cultures": "active lactic cultures",
        "potato": "potato",
        "potatoes": "potato",
        "dried potatoes": "dried potatoes"
    }

    @classmethod
    def normalize_ingredient(cls, raw_name):
        """Normalizes an ingredient string, stripping packaging notes, percentages, and alias codes."""
        if not raw_name:
            return ""
        
        cleaned = raw_name.lower().strip()
        additive_code = re.fullmatch(r"(?:e|ins\s*)?\s*(\d{3,4}[a-z]?)\s*(?:\([ivx]+\))?", cleaned)
        if additive_code:
            code = additive_code.group(1)
            code_aliases = {
                "150d": "caramel color", "211": "sodium benzoate",
                "296": "acidity regulator", "300": "antioxidant",
                "330": "acidity regulator", "331": "acidity regulator",
                "334": "acidity regulator", "338": "acidity regulator",
                "508": "flavour enhancers", "551": "anticaking agent",
                "621": "monosodium glutamate", "627": "flavour enhancers",
                "631": "flavour enhancers"
            }
            return code_aliases.get(code, code)
        # Remove parenthetical details like (12%), (E322), etc.
        cleaned = re.sub(r"\s*[\(\[\{][^\)\]\}]*[\)\]\}]", "", cleaned).strip()
        # Remove leading bullets, numbers, dashes, carets
        cleaned = re.sub(r"^[\d\.\-\*\•\^\s]+", "", cleaned).strip()
        # Remove percentage notations
        cleaned = re.sub(r"\d+(\.\d+)?%", "", cleaned).strip()
        # Remove punctuation except spaces
        cleaned = re.sub(r"[^\w\s]", "", cleaned).strip()
        
        # Check synonyms dictionary directly
        if cleaned in cls.SYNONYMS:
            return cls.SYNONYMS[cleaned]
        
        # Substring mapping
        # Match full phrases only. Substring aliases such as `flour` can
        # incorrectly turn oat flour or chickpea flour into wheat flour.
        for syn_key, syn_val in sorted(cls.SYNONYMS.items(), key=lambda pair: len(pair[0]), reverse=True):
            if re.search(rf"(?<!\w){re.escape(syn_key)}(?!\w)", cleaned):
                return syn_val
                
        return cleaned

    @classmethod
    def _extract_ingredient_section(cls, input_text):
        """Prefer the ingredient declaration when OCR returns the whole pack."""
        raw_text = str(input_text or "").replace("\r", "\n")
        # Prefer a real label heading at the start of a line. This avoids
        # mistaking marketing copy such as "Ingredients and Allergen Info"
        # for the beginning of the list.
        heading = re.search(
            r"(?im)^[ \t]*(?:ingredients?|composition)(?:[ \t]+list)?(?:[ \t]*[:\-][ \t]*|[ \t]+|$)",
            raw_text
        )
        if heading:
            preview = raw_text[heading.end():].lstrip().split(None, 1)[0].lower().strip(" ,:;-.") if raw_text[heading.end():].strip() else ""
            if preview in {"and", "information", "allergen", "are", "may", "list"}:
                heading = None
        if not heading:
            # Some OCR engines put the heading and body mid-line, but retain
            # its colon or dash.
            heading = re.search(r"\b(?:ingredients?|composition)(?:\s+list)?\s*[:\-]\s*", raw_text, re.IGNORECASE)
        if not heading:
            return " ".join(raw_text.splitlines())

        section = " ".join(raw_text[heading.end():].splitlines())
        stop = re.search(
            r"\b(?:nutrition(?:al)?\s+(?:facts|information)|allergen\s+(?:information|advice)|"
            r"may\s+contain|contains\s+(?:milk|wheat|soy|peanut|nuts|traces)|"
            r"storage\s+instructions|manufactured\s+by|marketed\s+by|net\s+(?:quantity|weight)|"
            r"best\s+before|fssai|mrp\s*[:\-])\b",
            section,
            re.IGNORECASE
        )
        if stop:
            section = section[:stop.start()]
        return section.strip(" \t\n:;-.") or text

    @classmethod
    def _match_product_name_in_label(cls, input_text):
        """Recognize a catalog product name printed above the ingredient panel."""
        raw_text = str(input_text or "").replace("\r", "\n")
        heading = re.search(
            r"(?im)^[ \t]*(?:ingredients?|composition)(?:[ \t]+list)?(?:[ \t]*[:\-][ \t]*|[ \t]+|$)",
            raw_text
        )
        if heading:
            prefix = raw_text[:heading.start()]
        else:
            prefix = raw_text.split("Ingredients:", 1)[0]
        normalized_prefix = re.sub(r"[^a-z0-9]+", " ", prefix.lower()).strip()
        if not normalized_prefix:
            return None

        aliases = {
            "lays_magic_masala": ["lays india magic masala", "lays magic masala"],
            "lays_classic": ["lays classic", "lays original"],
            "kurkure_masala_munch": ["kurkure masala munch", "kurkure masala"],
            "bingo_tedhe_medhe_masala_tadka": ["bingo tedhe medhe", "tedhe medhe masala tadka"],
            "bingo_original": ["bingo original style", "bingo potato chips"],
            "oreo_original": ["oreo original", "oreo sandwich cookies", "oreo"],
            "coca_cola_original": ["coca cola original"],
            "coca_cola_coffee_vanilla": ["coca cola coffee vanilla", "coffee vanilla"],
            "sprite_lemon_lime": ["sprite lemon lime", "sprite"],
            "minute_maid_pulpy_orange": ["minute maid pulpy orange", "pulpy orange"],
            "maggi_masala_noodles": ["maggi 2 minute noodles", "maggi masala noodles"],
            "yippee_magic_masala": ["sunfeast yippee magic masala noodles", "sunfeast yippee", "yippee magic masala"],
            "cadbury_dairy_milk": ["cadbury dairy milk", "dairy milk"],
            "kissan_tomato_ketchup": ["kissan tomato ketchup", "kissan ketchup"],
            "haldirams_bhujia_sev": ["haldiram bhujia", "haldirams bhujia sev"]
        }
        by_id = {product.get("id"): product for product in cls.PRODUCT_DATABASE}
        matches = []
        for product_id, product_aliases in aliases.items():
            product = by_id.get(product_id)
            if not product:
                continue
            for alias in product_aliases:
                normalized_alias = re.sub(r"[^a-z0-9]+", " ", alias.lower()).strip()
                if re.search(rf"(?<!\w){re.escape(normalized_alias)}(?!\w)", normalized_prefix):
                    matches.append((len(normalized_alias.split()), len(normalized_alias), product))
        return max(matches, key=lambda match: (match[0], match[1]))[2] if matches else None

    @classmethod
    def parse_input_ingredients(cls, input_text):
        """
        Extracts and normalizes a list of ingredients from text.
        Accurately extracts both top-level names and nested parenthetical sub-ingredients
        (e.g., 'Spices and Condiments (Onion, Garlic, Chilli)' -> 'spices and condiments', 'onion', 'garlic', 'chilli').
        """
        if isinstance(input_text, list):
            text = ", ".join(str(x) for x in input_text)
        else:
            text = cls._extract_ingredient_section(input_text)
            
        # Strip prefix like "Ingredients:", "INGREDIENTS :", "Contains:", etc.
        text = re.sub(r"^(ingredients|ingredient list|contains)\s*[:\-]\s*", "", text, flags=re.IGNORECASE).strip()
        
        extracted_raw = []
        
        # Extract sub-ingredients in parentheses / brackets
        paren_matches = re.findall(r"[\(\[\{]([^\)\]\}]+)[\)\]\}]", text)
        for match in paren_matches:
            sub_items = re.split(r"[,;/]+", match)
            for sub in sub_items:
                sub_clean = sub.strip()
                if sub_clean and not re.match(r"^\d+(\.\d+)?%$", sub_clean):
                    extracted_raw.append(sub_clean)

        # Extract top-level items
        top_text = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", "", text)
        top_items = re.split(r"[,;\n\r\•\t]+", top_text)
        for item in top_items:
            item_clean = item.strip()
            if item_clean:
                extracted_raw.append(item_clean)
            
        normalized = []
        seen = set()
        for item in extracted_raw:
            norm = cls.normalize_ingredient(item)
            if norm and len(norm) > 1 and norm not in seen:
                normalized.append(norm)
                seen.add(norm)
                
        return normalized

    @staticmethod
    def _ingredient_matches(candidate, ingredients):
        """Match a complete ingredient phrase inside a normalized label item.

        Requiring phrase boundaries avoids broad false matches such as `oil`
        satisfying a `palm oil` signature or `salt` matching `salted`.
        """
        phrase = re.escape(str(candidate).strip().lower())
        if not phrase:
            return False
        return any(
            re.search(rf"(?<!\w){phrase}(?!\w)", str(ingredient).lower())
            for ingredient in ingredients
        )

    @staticmethod
    def _organic_alternative(product):
        """Return several category-specific organic food choices, not a spec-upgrade."""
        category = (product.get("category") or "").lower()
        catalog = [
            (("snack", "namkeen", "chips", "tortilla"), ["Organic roasted chana", "Organic roasted makhana", "Organic millet and lentil puffs", "Organic baked multigrain crackers", "Organic dried fruit and nut mix"]),
            (("cookie", "biscuit"), ["Organic oats and date biscuits", "Organic wholegrain crackers", "Organic dried fruit and nut bars", "Organic ragi cookies", "Organic unsweetened fruit-and-oat bites"]),
            (("noodle", "soup"), ["Organic whole-wheat noodles", "Organic millet noodles", "Organic lentil pasta", "Organic vegetable soup", "Organic brown-rice noodles"]),
            (("chocolate", "confectionery"), ["Organic dark chocolate", "Organic cocoa nibs", "Organic date-and-cocoa bites", "Organic nut-and-cocoa spread", "Organic dried fruit"]),
            (("soft drink", "carbonated", "fruit drink"), ["Organic unsweetened herbal infusion", "Organic sparkling water with citrus", "Organic coconut water", "Organic unsweetened fruit drink", "Organic whole-fruit smoothie"]),
            (("cereal", "breakfast"), ["Organic rolled oats", "Organic unsweetened muesli", "Organic millet porridge mix", "Organic wholegrain cereal", "Organic chia-and-oat breakfast mix"]),
            (("spread", "condiment", "sauce"), ["Organic tomato salsa", "Organic hummus", "Organic peanut or almond butter", "Organic herb pesto", "Organic unsweetened tomato puree"]),
            (("dairy", "yogurt"), ["Organic plain yogurt", "Organic plain kefir", "Organic unsweetened soy yogurt", "Organic unsweetened oat yogurt", "Organic cottage cheese"]),
        ]
        choices = next((items for terms, items in catalog if any(term in category for term in terms)), [
            "Organic wholegrain crackers", "Organic roasted pulses", "Organic plain oats", "Organic dried fruit and nuts", "Organic unsweetened herbal infusion"
        ])
        reason = (
            "These are different food options to explore. Check the package for a recognized organic certification, "
            "and compare added sugar, sodium, fiber, and allergens. Organic certification alone does not guarantee better nutrition."
        )
        items = [{"name": name, "brand": "Choose a locally certified organic brand", "reason": reason} for name in choices]
        return {**items[0], "alternatives": items}

    @classmethod
    def identify_product(cls, input_text):
        """
        Main Engine Method:
        1. Normalizes input ingredients and resolves synonyms.
        2. Determines likely food category.
        3. Prioritizes primary base ingredient hierarchy (e.g. Potato 60% vs Wheat Flour base).
        4. Compares combination against known food products.
        5. Identifies closest matching commercial product with match confidence:
           Exact, Strong, Likely, Possible, Insufficient.
        6. Formulates evidence-based review.
        7. Recommends specific finished food product alternative (never raw ingredients).
        8. Returns JSON conforming to exact specification.
        """
        normalized_ingredients = cls.parse_input_ingredients(input_text)
        
        # --- Safety Against Hallucination Check ---
        generic_only = set(["salt", "water", "sugar", "oil", "vegetable oil", "refined wheat flour"])
        input_set = set(normalized_ingredients)
        
        if len(normalized_ingredients) < 2 or (len(normalized_ingredients) <= 2 and input_set.issubset(generic_only)):
            return {
                "input_ingredients": normalized_ingredients,
                "identified_product": {
                    "name": None,
                    "brand": None,
                    "category": None,
                    "match_level": "Insufficient",
                    "verified": False
                },
                "reasoning_summary": "The provided ingredient list contains insufficient specific signature markers to reliably identify a commercial packaged food product without guessing.",
                "review": {
                    "taste_profile": "Insufficient information to establish taste profile.",
                    "pros": [],
                    "cons": [],
                    "overall": "Cannot provide a balanced product review because the ingredients are too generic to determine the specific commercial food item."
                },
                "alternative_product": {
                    "name": None,
                    "brand": None,
                    "reason": "Provide a complete ingredient list from the product label to receive verified finished-product recommendations."
                },
                "accuracy_note": "Factual accuracy prioritized: Generic or insufficient ingredient combinations are not matched to arbitrary commercial brands."
            }

        # Detect primary base from the input text
        # (The very first ingredient listed in packaging order)
        ingredient_text = cls._extract_ingredient_section(input_text)
        raw_first_match = re.split(r"[,;\n\r\•\t\(]+", re.sub(r"^(ingredients|ingredient list|contains)\s*[:\-]\s*", "", ingredient_text, flags=re.IGNORECASE).strip())
        first_ing_raw = raw_first_match[0] if raw_first_match else ""
        first_ing_norm = cls.normalize_ingredient(first_ing_raw)

        best_match = None
        best_score = 0.0
        best_matched_sigs = []

        for product in cls.PRODUCT_DATABASE:
            signatures = product["signature_ingredients"]
            optionals = product.get("optional_ingredients", [])
            negatives = product.get("negative_markers", [])
            primary_base = product.get("primary_base")
            
            # 1. Check negative markers (disqualifiers)
            # If any negative marker is present in the normalized ingredients, disqualify
            has_negative = False
            for neg in negatives:
                if cls._ingredient_matches(neg, normalized_ingredients):
                    has_negative = True
                    break
            if has_negative:
                continue

            # 2. Check primary base alignment
            base_bonus = 0.0
            if primary_base and first_ing_norm:
                if cls._ingredient_matches(primary_base, [first_ing_norm]):
                    base_bonus = 0.25 # Substantial bonus for primary base match!
                
            # 3. Match signatures
            matched_signatures = []
            for sig in signatures:
                if cls._ingredient_matches(sig, normalized_ingredients):
                    matched_signatures.append(sig)
                    
            matched_optionals = []
            for opt in optionals:
                if cls._ingredient_matches(opt, normalized_ingredients):
                    matched_optionals.append(opt)
            
            # Calculate match score
            sig_coverage = len(matched_signatures) / len(signatures) if signatures else 0
            opt_bonus = (len(matched_optionals) / len(optionals)) * 0.15 if optionals else 0
            
            total_matches = len(matched_signatures) + len(matched_optionals)
            input_precision = total_matches / len(normalized_ingredients) if normalized_ingredients else 0
            
            final_score = (sig_coverage * 0.55) + (input_precision * 0.2) + opt_bonus + base_bonus
            
            # Keep a viable candidate when the ordered base ingredient and at
            # least one signature agree, or when multiple signature markers
            # agree. A full ingredient list often contains many extras, so a
            # strict percentage of the catalog's signatures hid good matches.
            generic_signatures = {"salt", "sugar", "water", "palm oil", "vegetable oil", "edible vegetable oil"}
            distinctive_matches = [item for item in matched_signatures if item not in generic_signatures]
            evidence_supports_candidate = (
                (base_bonus > 0 and len(matched_signatures) >= 1)
                or len(distinctive_matches) >= 2
            )
            if final_score > best_score and evidence_supports_candidate:
                best_score = final_score
                best_match = product
                best_matched_sigs = matched_signatures

        # Determine Match Confidence Level
        if not best_match or best_score < 0.30:
            return {
                "input_ingredients": normalized_ingredients,
                "identified_product": {
                    "name": None,
                    "brand": None,
                    "category": cls._infer_category_fallback(normalized_ingredients),
                    "match_level": "Insufficient",
                    "verified": False
                },
                "reasoning_summary": f"Detected ingredients ({', '.join(normalized_ingredients[:5])}...) suggest a general food category, but lack distinct signature markers to confidently identify a specific commercial product brand.",
                "review": {
                    "taste_profile": "Unknown commercial formulation.",
                    "pros": ["Ingredient combination observed"],
                    "cons": ["Cannot verify specific nutritional claims without confirmed commercial identity"],
                    "overall": "Product identity cannot be verified with sufficient confidence based on the provided ingredients alone."
                },
                "alternative_product": {
                    "name": None,
                    "brand": None,
                    "reason": "Specific brand matching requires more distinctive label ingredients."
                },
                "accuracy_note": "Factual accuracy prioritized. Product identity unverified to avoid hallucination."
            }

        # Categorize confidence
        if best_score >= 0.70 and len(best_matched_sigs) >= len(best_match["signature_ingredients"]) - 1:
            match_level = "Strong"
        elif best_score >= 0.55:
            match_level = "Strong"
        elif best_score >= 0.40:
            match_level = "Likely"
        else:
            match_level = "Possible"

        reasoning = (
            f"Matches {len(best_matched_sigs)} of {len(best_match['signature_ingredients'])} signature ingredients "
            f"for {best_match['name']} ({', '.join(best_matched_sigs)}). "
            f"Primary ingredient base aligns with '{best_match['category']}'."
        )

        return {
            "input_ingredients": normalized_ingredients,
            "identified_product": {
                "name": best_match["name"],
                "brand": best_match["brand"],
                "category": best_match["category"],
                "match_level": match_level,
                "verified": best_match.get("verified", False)
            },
            "reasoning_summary": reasoning,
            "review": {
                "taste_profile": best_match["taste_profile"],
                "pros": best_match["pros"],
                "cons": best_match["cons"],
                "overall": best_match["overall"]
            },
            "alternative_product": {
                **cls._organic_alternative(best_match)
            },
            "accuracy_note": "Best fit from the local ingredient-signature catalog. Brand and formulation are not independently verified; check the package."
        }

    @classmethod
    def _infer_category_fallback(cls, normalized_ingredients):
        text = " ".join(normalized_ingredients).lower()
        if any(term in text for term in ["potato", "palm oil", "namkeen", "besan", "sev", "chips"]):
            return "Potato Chips & Savory Snacks"
        elif any(term in text for term in ["flour", "wheat", "biscuit", "cookie", "cocoa"]):
            return "Cookies & Sweet Biscuits"
        elif any(term in text for term in ["noodle", "tastemaker", "soup"]):
            return "Instant Noodles & Pasta"
        elif any(term in text for term in ["cocoa butter", "chocolate", "milk solids"]):
            return "Chocolates & Confectionery"
        elif any(term in text for term in ["carbonated", "syrup", "cola", "caffeine"]):
            return "Carbonated Soft Drinks"
        elif any(term in text for term in ["hazelnut", "spread", "peanut butter", "butter"]):
            return "Spreads & Condiments"
        elif any(term in text for term in ["yogurt", "curd", "lactic"]):
            return "Dairy & Yogurts"
        return "Packaged Food Product"

    @classmethod
    def identify_with_ai_enhancement(cls, input_text):
        """
        Return the evidence-backed catalog result. Ingredient lists alone do not
        establish an exact brand or SKU, so a language model must not replace a
        catalog match with an unverified product identity or product facts.
        """
        result = cls.identify_product(input_text)
        named_product = cls._match_product_name_in_label(input_text)
        if named_product:
            # The printed product name is direct evidence from the label. It
            # resolves recipe collisions such as two brands of masala noodles.
            result["identified_product"] = {
                "name": named_product["name"],
                "brand": named_product["brand"],
                "category": named_product["category"],
                "match_level": "Strong",
                "verified": False
            }
            result["review"] = {
                "taste_profile": named_product["taste_profile"],
                "pros": named_product["pros"],
                "cons": named_product["cons"],
                "overall": named_product["overall"]
            }
            result["alternative_product"] = {
                **cls._organic_alternative(named_product)
            }
            result["reasoning_summary"] = (
                f"Recognized '{named_product['name']}' in the package text before the ingredient panel. "
                "The ingredient list was also analyzed for profile screening."
            )
            result["accuracy_note"] = (
                "Product name recognized from the uploaded label text. Confirm the exact flavor and current formulation on the package."
            )
        product = result.get("identified_product", {})
        if product.get("name"):
            # The local catalog has no linked source URL or SKU evidence, so
            # do not label its candidate as a verified packaging match.
            product["verified"] = False
            if product.get("match_level") == "Exact":
                product["match_level"] = "Strong"
            result["accuracy_note"] = (
                "Candidate matched against the local ingredient-signature catalog; "
                "brand and formulation are not independently verified. Check the package."
            )
        return result
