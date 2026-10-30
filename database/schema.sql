-- NutriLens AI Database Schema
-- Compatible with MySQL and SQLite

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User health profile table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INT PRIMARY KEY,
    age_range VARCHAR(50),
    vegetarian_status BOOLEAN DEFAULT 0,
    vegan_status BOOLEAN DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Allergens table (e.g. Milk, Egg, Peanut, Soy, Wheat, Gluten, Fish, Shellfish, Sesame, Sulfites)
CREATE TABLE IF NOT EXISTS allergens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 4. User Allergies mapping
CREATE TABLE IF NOT EXISTS user_allergies (
    user_id INT,
    allergen_id INT,
    PRIMARY KEY (user_id, allergen_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (allergen_id) REFERENCES allergens(id) ON DELETE CASCADE
);

-- 5. User dietary preferences / health goals
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    preference_tag VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, preference_tag)
);

-- 6. Explicit ingredients to avoid
CREATE TABLE IF NOT EXISTS user_avoid_ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    ingredient_name VARCHAR(150) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, ingredient_name)
);

-- 7. Ingredients Knowledge Base
CREATE TABLE IF NOT EXISTS ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    canonical_name VARCHAR(150) NOT NULL UNIQUE,
    category VARCHAR(100),
    explanation TEXT,
    vegan_status VARCHAR(20) DEFAULT 'UNKNOWN',
    vegetarian_status VARCHAR(20) DEFAULT 'UNKNOWN',
    dietary_tags TEXT,
    safer_alternatives TEXT
);

-- 8. Ingredient aliases (scientific names, E-codes, chemical terms)
CREATE TABLE IF NOT EXISTS ingredient_aliases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT,
    alias_name VARCHAR(150) NOT NULL UNIQUE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- 9. Ingredient allergens mapping
CREATE TABLE IF NOT EXISTS ingredient_allergens (
    ingredient_id INT,
    allergen_id INT,
    risk_level VARCHAR(50) DEFAULT 'DIRECT',
    PRIMARY KEY (ingredient_id, allergen_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    FOREIGN KEY (allergen_id) REFERENCES allergens(id) ON DELETE CASCADE
);

-- 10. Scans history
CREATE TABLE IF NOT EXISTS scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    image_path VARCHAR(255),
    raw_text TEXT,
    parsed_text TEXT,
    status VARCHAR(20) DEFAULT 'SAFE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 11. Scan ingredients results detail
CREATE TABLE IF NOT EXISTS scan_ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_id INT,
    ingredient_id INT NULL,
    detected_name VARCHAR(150) NOT NULL,
    match_status VARCHAR(20) DEFAULT 'SAFE',
    match_reason TEXT,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE SET NULL
);

-- 12. Recommendations generated
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_id INT UNIQUE,
    user_id INT,
    recommendations_text TEXT,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_ingredient_name ON ingredients(canonical_name);
CREATE INDEX idx_alias_name ON ingredient_aliases(alias_name);
CREATE INDEX idx_scans_user ON scans(user_id);
