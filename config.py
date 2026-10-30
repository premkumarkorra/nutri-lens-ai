import os
import shutil
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "nutrilens_default_secret_key_123890123")
    
    # Database selection: "mysql" or "sqlite"
    DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
    
    # SQLite Configuration
    SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "nutrilens.db")
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "nutrilens")
    
    # File upload configurations
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 8 * 1024 * 1024))  # 8MB max size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Tesseract OCR path if custom binary path is required (Windows users often need this)
    _configured_tesseract = os.environ.get("TESSERACT_CMD", "").strip()
    _windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    TESSERACT_CMD = (
        _configured_tesseract
        or shutil.which("tesseract")
        or (_windows_tesseract if os.path.isfile(_windows_tesseract) else "")
    )

    # Optional LLM configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    @staticmethod
    def init_app():
        # Ensure upload folder exists
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
            print(f"Created uploads folder at: {Config.UPLOAD_FOLDER}")

        # Ensure static/images folder exists
        images_dir = os.path.join("static", "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            print(f"Created static images folder at: {images_dir}")

        # Generate mock label images if they don't exist
        Config.generate_mock_labels(images_dir)

    @staticmethod
    def generate_mock_labels(images_dir):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            print("Pillow is not installed yet. Mock image generation skipped.")
            return

        labels = {
            "label_milk.jpg": (
                "Milk Allergen Label",
                "Ingredients: Whey Protein Isolate,\nMilk solids, Sugar, Soy Lecithin (E322),\nMaltodextrin, Gelatin,\nArtificial flavors."
            ),
            "label_peanut.jpg": (
                "Peanut Allergen Label",
                "Ingredients: Peanut Flour, Wheat Flour,\nCitric Acid, Carmine, Sodium Benzoate,\nSugar, High Fructose Corn Syrup."
            ),
            "label_soy.jpg": (
                "Soy Allergen Label",
                "Ingredients: Soy Lecithin, Wheat Flour,\nSodium Benzoate (E211), Rice Flour,\nSugar, Palm Oil."
            ),
            "label_generic.jpg": (
                "Generic Compound Label",
                "INGREDIENTS: Wheat Flour,\nWhey Protein Isolate, Soy Lecithin (E322),\nGelatin, Carmine (E120), Citric Acid (E330),\nSodium Benzoate, Maltodextrin,\nHigh Fructose Corn Syrup, Salt."
            )
        }

        for filename, (title, text) in labels.items():
            path = os.path.join(images_dir, filename)
            if not os.path.exists(path):
                try:
                    # Create 500x300 image
                    img = Image.new('RGB', (500, 300), color='#151B24')
                    draw = ImageDraw.Draw(img)
                    
                    # Draw header bar
                    draw.rectangle([0, 0, 500, 50], fill='#10151D')
                    draw.text((20, 18), f"NutriLens AI Sample - {title}", fill='#00D4A8')
                    
                    # Draw body
                    draw.text((20, 80), "INGREDIENTS LIST:", fill='#94A3B8')
                    
                    lines = text.split('\n')
                    y = 110
                    for line in lines:
                        draw.text((20, y), line, fill='#F8FAFC')
                        y += 24
                        
                    # Draw thin border
                    draw.rectangle([0, 0, 499, 299], outline='#27303C', width=2)
                    img.save(path, quality=95)
                    print(f"Generated mock label image at: {path}")
                except Exception as e:
                    print(f"Failed to generate mock label {filename}: {e}")

