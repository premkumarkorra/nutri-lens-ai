import os
import re
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

class OCRService:
    # Tesseract configuration for food label recognition
    TESSERACT_CONFIG = r'--oem 3 --psm 6 -l eng'
    
    @staticmethod
    def allowed_file(filename):
        from config import Config
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def apply_otsu_binarization(cv_image):
        """
        Apply Otsu's binary thresholding for high contrast text extraction.
        Converts image to pure black and white for better OCR accuracy.
        """
        try:
            if len(cv_image.shape) == 3:
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv_image
            
            # Apply Otsu's thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        except Exception as e:
            print(f"Binarization error: {e}")
            return cv_image

    @staticmethod
    def detect_and_correct_skew(cv_image):
        """
        Advanced skew detection and correction using Hough line transformation.
        More accurate than simple angle rotation.
        """
        try:
            if len(cv_image.shape) == 3:
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv_image
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Hough line detection
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
            
            if lines is not None and len(lines) > 0:
                # Calculate average angle
                angles = []
                for line in lines[:10]:  # Use first 10 lines
                    rho, theta = line[0]
                    angle = (theta * 180 / np.pi) - 90
                    angles.append(angle)
                
                if angles:
                    avg_angle = np.median(angles)
                    
                    # Only rotate if angle is significant
                    if abs(avg_angle) > 0.5:
                        h, w = gray.shape
                        center = (w // 2, h // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                        rotated = cv2.warpAffine(cv_image, rotation_matrix, (w, h), 
                                                 borderMode=cv2.BORDER_REPLICATE)
                        return rotated
            
            return cv_image
        except Exception as e:
            print(f"Skew correction error: {e}")
            return cv_image

    @staticmethod
    def remove_noise(cv_image):
        """
        Advanced noise removal using morphological operations.
        """
        try:
            # Apply bilateral filter for edge-preserving smoothing
            denoised = cv2.bilateralFilter(cv_image, 9, 75, 75)
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            return denoised
        except Exception as e:
            print(f"Noise removal error: {e}")
            return cv_image

    @staticmethod
    def enhance_contrast_adaptive(cv_image):
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        for better local contrast enhancement.
        """
        try:
            if len(cv_image.shape) == 3:
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv_image
            
            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            return enhanced
        except Exception as e:
            print(f"CLAHE error: {e}")
            return cv_image

    @staticmethod
    def preprocess_image_advanced(image_path, enhancement_level=2.0):
        """
        ADVANCED 18-step preprocessing pipeline for maximum OCR accuracy on ingredient labels.
        Uses OpenCV for professional-grade image processing optimized for food labels.
        """
        try:
            # Step 1: Load image
            img = cv2.imread(image_path)
            if img is None:
                return image_path
            
            # Step 2: Handle EXIF rotation
            try:
                pil_img = Image.open(image_path)
                pil_img = ImageOps.exif_transpose(pil_img)
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except:
                pass
            
            # Step 3: Denoise using bilateral filter
            img = OCRService.remove_noise(img)
            
            # Step 4: Detect and correct skew
            img = OCRService.detect_and_correct_skew(img)
            
            # Step 5: Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Step 6: Apply CLAHE for adaptive contrast
            gray = OCRService.enhance_contrast_adaptive(gray)
            
            # Step 7: Apply Gaussian blur to smooth
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Step 8: Apply morphological operations to connect text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel, iterations=1)
            morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Step 9: Apply Otsu's binary thresholding
            binary = OCRService.apply_otsu_binarization(morph)
            
            # Step 10: Dilate to strengthen text strokes
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            # Step 11: Apply erosion to remove small artifacts
            eroded = cv2.erode(dilated, kernel, iterations=1)
            
            # Step 12: Upscale if needed (minimum 1500px width for ingredient labels)
            h, w = eroded.shape
            if w < 1500 or h < 800:
                scale_factor = max(2, int(1500 / max(w, 1)))
                eroded = cv2.resize(eroded, (w * scale_factor, h * scale_factor), 
                                   interpolation=cv2.INTER_CUBIC)
            
            # Step 13: Apply adaptive thresholding for better text clarity
            adaptive = cv2.adaptiveThreshold(eroded, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
            
            # Step 14: Apply median filter to remove remaining noise
            denoised = cv2.medianBlur(adaptive, 3)
            
            # Step 15: Sharpen edges for crispier text
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # Step 16: Apply unsharp mask for additional edge enhancement
            gaussian = cv2.GaussianBlur(sharpened, (0, 0), 2.0)
            sharpened = cv2.addWeighted(sharpened, 1.5, gaussian, -0.5, 0)
            
            # Step 17: Final contrast boost
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            final = clahe.apply(sharpened.astype(np.uint8))
            
            # Step 18: Save optimized image
            dir_name = os.path.dirname(image_path)
            base_name = os.path.basename(image_path)
            prep_path = os.path.join(dir_name, "prep_" + base_name)
            cv2.imwrite(prep_path, final, [cv2.IMWRITE_JPEG_QUALITY, 98])
            
            return prep_path
        except Exception as e:
            print(f"Advanced preprocessing error: {e}")
            return image_path

    @staticmethod
    def preprocess_image(image_path, enhancement_level=2.0):
        """
        Use a gentle preprocessing pass that preserves small label characters.
        """
        try:
            pil_image = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            height, width = image.shape[:2]
            if max(height, width) < 1800:
                scale = 1800 / max(height, width)
                image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8)).apply(gray)
            output_path = os.path.join(
                os.path.dirname(image_path), "ocr_" + os.path.basename(image_path)
            )
            cv2.imwrite(output_path, gray, [cv2.IMWRITE_JPEG_QUALITY, 98])
            return output_path
        except Exception as e:
            print(f"Gentle preprocessing error: {e}")
            return image_path

    @classmethod
    def extract_text_with_confidence(cls, image_path, psm=3):
        """Return Tesseract text and its native average word confidence."""
        from config import Config

        if Config.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

        config = f"--psm {psm} --oem 3 -l eng"
        with Image.open(image_path) as image:
            data = pytesseract.image_to_data(
                image, config=config, output_type=pytesseract.Output.DICT
            )
        words = []
        lines = {}
        confidences = []
        for index, (word, confidence) in enumerate(zip(data["text"], data["conf"])):
            if word.strip():
                words.append(word)
                line_key = tuple(
                    data[key][index]
                    for key in ("page_num", "block_num", "par_num", "line_num")
                )
                lines.setdefault(line_key, []).append(word)
                try:
                    value = float(confidence)
                    if value >= 0:
                        confidences.append(value)
                except (TypeError, ValueError):
                    continue
        # image_to_data already contains the recognized words. Reuse them in
        # reading order instead of running the OCR engine a second time.
        text = "\n".join(" ".join(line_words) for _, line_words in sorted(lines.items()))
        if not text.strip():
            text = " ".join(words)
        native_confidence = sum(confidences) / len(confidences) if confidences else 0
        return text, native_confidence

    @staticmethod
    def score_ocr_candidate(text, native_confidence):
        """Rank OCR output using native confidence and label-specific signals."""
        normalized = text.lower()
        score = native_confidence
        score += min(12, sum(
            2 for keyword in ("ingredients", "contains", "salt", "flour", "sugar", "milk", "wheat", "soy")
            if keyword in normalized
        ))
        score += min(8, text.count(",") * 0.5)
        score -= min(20, len(re.findall(r"[^a-zA-Z0-9\s,().%'-]", text)) * 2)
        return score

    @classmethod
    def calculate_confidence(cls, raw_text, is_fallback=False):
        """
        Calculates OCR confidence score based on text quality indicators.
        Returns a confidence percentage (0-100).
        """
        if is_fallback:
            return 45  # Low confidence for fallback/mock data
        
        confidence = 100
        text_length = len(raw_text.strip())
        
        # Strong penalty if text is too short
        if text_length < 20:
            confidence -= 50
        elif text_length < 50:
            confidence -= 25
        
        # Check for excessive special characters (indicating OCR noise)
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s,\-()%.]', raw_text))
        if special_chars > text_length * 0.10:
            confidence -= 25
        
        # Check for common ingredient list structure
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        if len(lines) < 2:
            confidence -= 25
        
        # Bonus if common ingredient keywords found
        ingredient_keywords = ['ingredient', 'contains', 'may contain', 'allergen', 'nutrition', 'potato', 'flour', 'salt', 'protein']
        found_keywords = sum(1 for keyword in ingredient_keywords if keyword.lower() in raw_text.lower())
        if found_keywords >= 2:
            confidence += 10
        
        # Bonus if reasonable percentage values found (e.g., "60.0%")
        if re.search(r'\d+\.?\d*%', raw_text):
            confidence += 5
        
        # Check for common E-number additives or ingredient patterns
        if re.search(r'E\d{3,4}', raw_text) or re.search(r'\(\d+\.?\d*%\)', raw_text):
            confidence += 5
        
        return max(0, min(100, confidence))

    @classmethod
    def clean_text_professional(cls, raw_text):
        """
        Advanced post-processing to clean and normalize extracted text.
        Removes noise and improves accuracy for ingredient labels.
        """
        # Keep line boundaries because they help separate ingredients from warnings.
        text = raw_text.replace('\r', '')
        
        # Fix common OCR mistakes for ingredient labels
        corrections = {
            r'\bl{3,}\b': 'Ill',  # Multiple l's
            r',+': ',',      # Multiple commas to single
            r'\.+': '.',     # Multiple periods to single
            r'[ \t]+': ' ',  # Multiple spaces to single without flattening lines
            r'O\.O': '0.0',  # OCR confusion: O.O -> 0.0 (percentage)
            r'\)\s+\(': ') (', # Fix spacing in parentheses
            r'(\w)\s+%': r'\1%', # Remove space before %
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Expand common abbreviations that OCR might misread
        abbreviations = {
            r'\bMAIDA\b': 'MAIDA',  # Refined wheat flour
            r'\bINS\b': 'INS',      # Food additive code prefix
            r'\bE(\d+)': r'E\1',    # E-number additives
        }
        
        for pattern, replacement in abbreviations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Split by common delimiters and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Clean each line
        cleaned_lines = []
        for line in lines:
            # Preserve important characters for ingredient lists
            # Keep: alphanumeric, spaces, commas, periods, parentheses, hyphens, %, and E-numbers
            line = re.sub(r'[^\w\s,\-()%.\']', '', line)
            
            # Fix spacing around punctuation
            line = re.sub(r'\s+', ' ', line)
            line = line.strip()
            
            # Keep lines with meaningful content (at least 3 characters)
            if line and len(line) > 2:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    @classmethod
    def extract_text_with_psm(cls, image_path, psm=6):
        """
        Attempts text extraction with specific PSM (Page Segmentation Mode).
        Uses optimized Tesseract configuration for ingredient labels.
        
        PSM modes:
        - 3: Fully automatic (default)
        - 4: Assume a single column of text of variable sizes
        - 6: Assume a single uniform block of text
        - 11: Sparse text, find as much as possible
        - 13: Raw line. Treat the image as a single text line
        """
        try:
            from config import Config
            
            # Optimized Tesseract config for ingredient labels
            # --oem: OCR Engine Mode (0=Legacy, 1=Neural Nets, 2=Legacy+Neural, 3=Default)
            # --psm: Page Segmentation Mode
            # -l: Language (eng for English)
            config = f'--psm {psm} --oem 3 -l eng'
            
            # Additional Tesseract parameters for better accuracy
            # --dpi doesn't help much with preprocessed images
            # Using direct config
            
            # Additional OCR parameters for better accuracy on food labels
            if Config.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
            
            text = pytesseract.image_to_string(Image.open(image_path), config=config)
            return text
        except Exception as e:
            print(f"Error with PSM {psm}: {e}")
            return ""

    @classmethod
    def extract_text(cls, image_path):
        """
        Extract label text from the best-scoring image/layout combination.
        """
        from config import Config
        
        # Configure Tesseract path if set in environment
        if Config.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

        ocr_confidence_warning = False
        raw_text = ""
        error_msg = ""
        confidence_score = 0
        extraction_strategy = "native confidence"
        generated_paths = []
        
        try:
            prep_path = cls.preprocess_image(image_path)
            if prep_path != image_path:
                generated_paths.append(prep_path)

            candidates = []
            for candidate_path, candidate_name in ((image_path, "original"), (prep_path, "gentle enhancement")):
                stop_search = False
                for psm in (3, 4, 6, 11):
                    text, native_confidence = cls.extract_text_with_confidence(candidate_path, psm=psm)
                    if not text.strip() and psm == 4:
                        text = cls.extract_text_with_psm(prep_path, psm=4)
                    if text.strip():
                        candidates.append((
                            cls.score_ocr_candidate(text, native_confidence) + (4 if candidate_name == "original" else 0),
                            native_confidence,
                            text,
                            f"{candidate_name}, PSM {psm}"
                        ))
                        if (
                            native_confidence >= 92
                            and len(text) >= 100
                            and text.count(",") >= 4
                            and re.search(r"\bingredients?\b", text, re.IGNORECASE)
                        ):
                            stop_search = True
                            break
                if stop_search:
                    break

            if not candidates:
                raise ValueError("Tesseract returned no text from any OCR candidate.")

            _, native_confidence, raw_text, extraction_strategy = max(candidates, key=lambda candidate: candidate[0])
            if len(raw_text.strip()) < 15:
                raise ValueError("Tesseract returned minimal output after all PSM attempts.")
            
            raw_text = cls.clean_text_professional(raw_text)
            heuristic_confidence = cls.calculate_confidence(raw_text, is_fallback=False)
            confidence_score = round((native_confidence * 0.75) + (heuristic_confidence * 0.25))
                
        except (pytesseract.TesseractNotFoundError, Exception) as e:
            # Never substitute demo/mock label text for an uploaded image.
            error_msg = str(e)
            print(f"OCR Error: {error_msg}.")
            ocr_confidence_warning = True
            confidence_score = 0
            extraction_strategy = "unavailable"
            raw_text = ""

        for generated_path in generated_paths:
            if os.path.exists(generated_path):
                try:
                    os.remove(generated_path)
                except OSError:
                    pass

        # Normalize final text
        clean_lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        result_text = '\n'.join(clean_lines)

        # STEP 11: Build user message with detailed feedback
        message = f"OCR completed with {confidence_score}% confidence using {extraction_strategy}."
        if ocr_confidence_warning:
            if "tesseract" in error_msg.lower() or "not found" in error_msg.lower():
                message = "⚠️ Tesseract binary not found. Running in Simulation Mode (mock text loaded). Please install Tesseract for accurate OCR."
            else:
                message = f"⚠️ OCR processing encountered issues. Running in Simulation Mode."

        return {
            "text": result_text,
            "confidence": confidence_score,
            "is_fallback": ocr_confidence_warning,
            "message": message,
            "strategy": extraction_strategy
        }


