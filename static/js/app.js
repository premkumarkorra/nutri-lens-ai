// NutriScan AI - Ingredient-to-Food-Product Identification & Recommendation Engine Logic

// Application State
let state = {
    user: null,
    currentScanImage: null,
    profileAvoidList: [],
    videoStream: null,
    currentResultData: null // Cache current JSON response for modal/copy
};

// Preset Ingredient Signatures for Instant 1-Click Testing
const PRESETS = {
    lays: "Ingredients: Potato, Edible Vegetable Oil (Palmolein), Salt",
    kurkure: "Ingredients: Rice Meal, Edible Vegetable Oil (Palmolein), Corn Meal, Gram Meal, Spices and Condiments (Chilli Powder, Onion Powder, Garlic Powder, Amchur), Salt, Sugar, Citric Acid",
    maggi: "Ingredients: Refined Wheat Flour (Maida), Palm Oil, Salt, Wheat Gluten, Mineral (Calcium Carbonate), Hydrolysed Groundnut Protein, Onion Powder, Garlic Powder, Spices and Condiments (Coriander, Turmeric, Cumin)",
    oreo: "Ingredients: Refined Wheat Flour, Sugar, Fractionated Palm Oil, Cocoa Solids (4.5%), Invert Sugar, Leavening Agents (INS 500(ii), INS 503(ii)), Salt, Emulsifier (INS 322)",
    cadbury: "Ingredients: Sugar, Milk Solids (20%), Cocoa Butter, Cocoa Solids (11%), Emulsifiers (INS 442, INS 476), Flavours",
    nutella: "Ingredients: Sugar, Palm Oil, Hazelnuts (13%), Skimmed Milk Powder (8.7%), Fat-Reduced Cocoa (7.4%), Emulsifier Lecithins (Soy), Vanillin",
    amul: "Ingredients: Butter, Common Salt, Permitted Natural Colour (Annatto)",
    ketchup: "Ingredients: Water, Tomato Paste (26%), Sugar, Salt, Acidity Regulator (INS 260), Preservative (INS 211), Spices and Condiments",
    insufficient: "Ingredients: Water, Salt"
};

// DOM Elements
const views = {
    landing: document.getElementById('view-landing'),
    auth: document.getElementById('view-auth'),
    scan: document.getElementById('view-scan'),
    analysis: document.getElementById('view-analysis'),
    history: document.getElementById('view-history'),
    profile: document.getElementById('view-profile')
};

// Toast Notification Controller
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.className = `toast ${type}`;
    const icon = document.createElement('i');
    icon.className = `fa-solid ${type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-circle-xmark' : 'fa-triangle-exclamation'}`;
    const text = document.createElement('span');
    text.textContent = String(message ?? '');
    toast.replaceChildren(icon, text);
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}

// Switch SPA views
function switchView(targetViewId) {
    // Auth Guard: scan, history, profile, and analysis require authentication
    const protectedViews = ['view-scan', 'view-history', 'view-profile', 'view-analysis'];
    if (!state.user && protectedViews.includes(targetViewId)) {
        targetViewId = 'view-auth';
        document.getElementById('tab-register')?.click();
        showToast("Please create an account or sign in to start scanning food products.", "info");
    }

    Object.values(views).forEach(view => {
        if (view) view.classList.add('hidden');
    });
    
    const key = targetViewId.replace('view-', '');
    const target = views[key];
    if (target) {
        target.classList.remove('hidden');
        window.scrollTo(0, 0);
    }
    
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('data-target') === targetViewId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    if (targetViewId === 'view-history' && state.user) {
        loadHistory();
    } else if (targetViewId === 'view-profile' && state.user) {
        loadProfile();
    }
}

// Navigation links bindings
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const target = item.getAttribute('data-target');
        if (target) switchView(target);
    });
});

document.getElementById('nav-logo')?.addEventListener('click', () => {
    if (state.user) switchView('view-scan');
    else switchView('view-landing');
});

document.getElementById('hero-get-started')?.addEventListener('click', () => {
    if (state.user) {
        switchView('view-scan');
    } else {
        switchView('view-auth');
        document.getElementById('tab-register')?.click();
    }
});

document.getElementById('hero-sign-in')?.addEventListener('click', () => {
    switchView('view-auth');
    document.getElementById('tab-login')?.click();
});

document.getElementById('btn-show-login')?.addEventListener('click', () => {
    switchView('view-auth');
    document.getElementById('tab-login')?.click();
});

document.getElementById('btn-show-register')?.addEventListener('click', () => {
    switchView('view-auth');
    document.getElementById('tab-register')?.click();
});

// --- SESSION & AUTHENTICATION ---

async function checkSession() {
    try {
        const response = await fetch('/api/auth/session');
        const data = await response.json();
        
        if (data.logged_in) {
            setAuthenticatedState(data.user);
            switchView('view-scan');
        } else {
            setGuestState();
        }
    } catch (e) {
        setGuestState();
    }
}

function setAuthenticatedState(user) {
    state.user = user;
    document.getElementById('guest-nav')?.classList.add('hidden');
    document.getElementById('auth-nav')?.classList.remove('hidden');
    const userDisplay = document.getElementById('username-display');
    if (userDisplay) userDisplay.innerText = `Hi, ${user.username}`;
}

function setGuestState() {
    state.user = null;
    document.getElementById('guest-nav')?.classList.remove('hidden');
    document.getElementById('auth-nav')?.classList.add('hidden');
    const userDisplay = document.getElementById('username-display');
    if (userDisplay) userDisplay.innerText = '';
}

// Auth Tabs Toggle
document.getElementById('tab-login')?.addEventListener('click', () => {
    document.getElementById('tab-login').classList.add('active');
    document.getElementById('tab-register').classList.remove('active');
    document.getElementById('form-login').classList.remove('hidden');
    document.getElementById('form-register').classList.add('hidden');
});

document.getElementById('tab-register')?.addEventListener('click', () => {
    document.getElementById('tab-register').classList.add('active');
    document.getElementById('tab-login').classList.remove('active');
    document.getElementById('form-register').classList.remove('hidden');
    document.getElementById('form-login').classList.add('hidden');
});

document.getElementById('link-to-register')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('tab-register').click();
});

document.getElementById('link-to-login')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('tab-login').click();
});

// Login submission
document.getElementById('form-login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast("Login successful. Welcome back!");
            setAuthenticatedState(data.user);
            switchView('view-scan');
            if (state.pendingPreset) {
                const textarea = document.getElementById('direct-ingredients-input');
                if (textarea) textarea.value = state.pendingPreset;
                state.pendingPreset = null;
            }
        } else {
            showToast(data.error || "Login failed.", "error");
        }
    } catch (err) {
        showToast("Server connection error.", "error");
    }
});

// Register Avoidance Tags Management
let regAvoidTags = [];

function renderRegAvoidTags() {
    const container = document.getElementById('reg-avoid-tags-container');
    if (!container) return;
    container.innerHTML = '';
    regAvoidTags.forEach((tag, idx) => {
        const span = document.createElement('span');
        span.className = 'tag-badge';
        const label = document.createElement('span');
        label.textContent = tag;
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'remove-tag-btn';
        button.dataset.index = idx;
        button.setAttribute('aria-label', `Remove ${tag}`);
        button.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
        span.append(label, button);
        container.appendChild(span);
    });

    container.querySelectorAll('.remove-tag-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = Number(e.currentTarget.dataset.index);
            regAvoidTags.splice(idx, 1);
            renderRegAvoidTags();
        });
    });
}

document.getElementById('btn-reg-add-avoid-tag')?.addEventListener('click', () => {
    const input = document.getElementById('reg-avoid-input');
    const val = input.value.trim();
    if (val && !regAvoidTags.includes(val)) {
        regAvoidTags.push(val);
        input.value = '';
        renderRegAvoidTags();
    }
});

document.getElementById('reg-avoid-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('btn-reg-add-avoid-tag')?.click();
    }
});

// Register submission with full health profile
document.getElementById('form-register')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const age_range = document.getElementById('reg-age')?.value || '25-34';
    const vegetarian = document.getElementById('reg-vegetarian')?.checked || false;
    const non_vegetarian = document.getElementById('reg-non-vegetarian')?.checked || false;
    
    // Collect selected allergies
    const allergyInputs = document.querySelectorAll('input[name="reg-allergies"]:checked');
    const allergies = Array.from(allergyInputs).map(cb => cb.value);

    // Collect selected preferences
    const prefInputs = document.querySelectorAll('input[name="reg-preferences"]:checked');
    const preferences = Array.from(prefInputs).map(cb => cb.value);

    // Collect avoid ingredients
    const avoid_ingredients = [...regAvoidTags];
    
    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username,
                password,
                age_range,
                vegetarian,
                non_vegetarian,
                allergies,
                preferences,
                avoid_ingredients
            })
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast("Registration successful! Your health profile is configured.");
            setAuthenticatedState(data.user);
            switchView('view-scan');
            if (state.pendingPreset) {
                const textarea = document.getElementById('direct-ingredients-input');
                if (textarea) textarea.value = state.pendingPreset;
                state.pendingPreset = null;
            }
        } else {
            showToast(data.error || "Registration failed.", "error");
        }
    } catch (err) {
        showToast("Server connection error.", "error");
    }
});

document.getElementById('reg-vegetarian')?.addEventListener('change', (e) => {
    if (e.currentTarget.checked) {
        const nonVeg = document.getElementById('reg-non-vegetarian');
        if (nonVeg) nonVeg.checked = false;
    }
});
document.getElementById('reg-non-vegetarian')?.addEventListener('change', (e) => {
    if (e.currentTarget.checked) {
        const veg = document.getElementById('reg-vegetarian');
        if (veg) veg.checked = false;
    }
});

// Logout
document.getElementById('btn-logout')?.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/auth/logout', { method: 'POST' });
        if (!response.ok) throw new Error('Logout request failed');
        showToast("You have been signed out.");
        setGuestState();
        switchView('view-landing');
    } catch (e) {
        showToast("Sign out failed.", "error");
    }
});

// --- INPUT MODE TABS (TEXT vs OCR) ---
const tabText = document.getElementById('tab-input-text');
const tabOcr = document.getElementById('tab-input-ocr');
const modeTextContainer = document.getElementById('mode-text-container');
const modeOcrContainer = document.getElementById('mode-ocr-container');

tabText?.addEventListener('click', () => {
    tabText.classList.add('active');
    tabOcr.classList.remove('active');
    modeTextContainer.classList.remove('hidden');
    modeOcrContainer.classList.add('hidden');
});

tabOcr?.addEventListener('click', () => {
    tabOcr.classList.add('active');
    tabText.classList.remove('active');
    modeOcrContainer.classList.remove('hidden');
    modeTextContainer.classList.add('hidden');
});

// --- PRESET CHIPS BINDINGS ---
function bindPresetButtons() {
    document.querySelectorAll('.btn-preset-chip').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const presetKey = btn.getAttribute('data-preset');
            const ingredientText = PRESETS[presetKey];
            if (ingredientText) {
                if (!state.user) {
                    state.pendingPreset = ingredientText;
                    switchView('view-auth');
                    document.getElementById('tab-register')?.click();
                    showToast("Please create an account or sign in to test product identification.", "info");
                    return;
                }

                // Switch to scan view and text mode
                switchView('view-scan');
                tabText?.click();
                
                const textarea = document.getElementById('direct-ingredients-input');
                if (textarea) {
                    textarea.value = ingredientText;
                    textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    textarea.classList.add('input-pulsing');
                    setTimeout(() => textarea.classList.remove('input-pulsing'), 800);
                }
                showToast(`Loaded preset: ${btn.innerText.trim()}`);
            }
        });
    });
}
bindPresetButtons();

// --- OCR FILE UPLOAD & CAMERA ---
let selectedFile = null;
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-upload');

['dragenter', 'dragover'].forEach(eventName => {
    dropZone?.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone?.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
    }, false);
});

dropZone?.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) handleSelectedFile(files[0]);
});

fileInput?.addEventListener('change', () => {
    if (fileInput.files.length) handleSelectedFile(fileInput.files[0]);
});

function handleSelectedFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        showToast("Please upload a supported image file (PNG, JPG, WEBP or GIF).", "error");
        return;
    }
    if (file.size > 8 * 1024 * 1024) {
        showToast("This image is larger than 8 MB. Choose a smaller file.", "error");
        if (fileInput) fileInput.value = '';
        return;
    }
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('image-preview').src = e.target.result;
        dropZone.classList.add('hidden');
        document.getElementById('image-preview-container').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

document.getElementById('btn-remove-image')?.addEventListener('click', () => {
    selectedFile = null;
    if (fileInput) fileInput.value = '';
    document.getElementById('image-preview').src = '';
    dropZone.classList.remove('hidden');
    document.getElementById('image-preview-container').classList.add('hidden');
    state.currentScanImage = null;
});

// CAMERA
const webcamEl = document.getElementById('webcam');
const cameraContainer = document.getElementById('camera-container');

document.getElementById('btn-use-camera')?.addEventListener('click', async () => {
    try {
        if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera is unavailable in this browser context');
        state.videoStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        webcamEl.srcObject = state.videoStream;
        dropZone.classList.add('hidden');
        cameraContainer.classList.remove('hidden');
    } catch (err) {
        showToast("Webcam access denied or unavailable.", "error");
    }
});

document.getElementById('btn-cancel-camera')?.addEventListener('click', () => {
    stopWebcam();
    cameraContainer.classList.add('hidden');
    dropZone.classList.remove('hidden');
});

function stopWebcam() {
    if (state.videoStream) {
        state.videoStream.getTracks().forEach(track => track.stop());
        state.videoStream = null;
    }
    if (webcamEl) webcamEl.srcObject = null;
}

document.getElementById('btn-capture-photo')?.addEventListener('click', () => {
    if (!webcamEl?.videoWidth || !webcamEl?.videoHeight) {
        showToast("The camera is still starting. Try again in a moment.", "warning");
        return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = webcamEl.videoWidth;
    canvas.height = webcamEl.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcamEl, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
        if (!blob) {
            showToast("Could not capture an image. Please try again.", "error");
            return;
        }
        const file = new File([blob], "captured_label.jpg", { type: "image/jpeg" });
        stopWebcam();
        cameraContainer.classList.add('hidden');
        handleSelectedFile(file);
    }, 'image/jpeg');
});

// Run OCR text extraction
document.getElementById('btn-run-ocr')?.addEventListener('click', async () => {
    if (!selectedFile) return;

    const ocrLoading = document.getElementById('ocr-loading');
    const imageContainer = document.getElementById('image-preview-container');
    const statusText = document.getElementById('loading-status');
    
    imageContainer.classList.add('hidden');
    ocrLoading.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            body: formData
        });
        ocrLoading.classList.add('hidden');
        imageContainer.classList.remove('hidden');
        
        const data = await res.json();
        if (res.ok) {
            state.currentScanImage = data.image_path;
            
            // Populate text input and switch to text view so user can review/edit
            const textarea = document.getElementById('direct-ingredients-input');
            if (textarea) textarea.value = data.raw_text;
            
            tabText?.click();
            showToast("Text extracted! Review ingredients and click Identify.");
        } else {
            showToast(data.error || "OCR Extraction failed.", "error");
        }
    } catch (e) {
        ocrLoading.classList.add('hidden');
        imageContainer.classList.remove('hidden');
        showToast("Connection error during image scan.", "error");
    }
});

// --- TRIGGER PRODUCT IDENTIFICATION & RECOMMENDATION ---
document.getElementById('btn-trigger-identification')?.addEventListener('click', async () => {
    const ingredientsInput = document.getElementById('direct-ingredients-input').value.trim();
    if (!ingredientsInput) {
        showToast("Please enter an ingredient list or select a preset.", "warning");
        return;
    }
    
    const btn = document.getElementById('btn-trigger-identification');
    const originalBtnHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Identifying Commercial Product...`;
    
    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ingredients: ingredientsInput,
                image_path: state.currentScanImage
            })
        });
        const data = await res.json();
        
        btn.disabled = false;
        btn.innerHTML = originalBtnHTML;

        if (res.ok) {
            state.currentResultData = data;
            renderIdentificationResults(data);
            switchView('view-analysis');
            showToast("Product identified successfully!");
        } else {
            showToast(data.reasoning_summary || data.error || "Identification failed.", "error");
        }
    } catch (err) {
        btn.disabled = false;
        btn.innerHTML = originalBtnHTML;
        showToast("Server connection error during identification.", "error");
    }
});

// --- RENDER IDENTIFICATION & RECOMMENDATION RESULTS ---
function renderIdentificationResults(data) {
    // /api/analyze returns the product report nested alongside personalized screening.
    // History can still contain the older product-only response, so support both shapes.
    const report = data.product_identification || data;
    const prod = report.identified_product || data.identified_product || {};
    const review = report.review || data.review || {};
    const alt = report.alternative_product || data.alternative_product || {};

    // 1. Identified Product Top Card
    const nameEl = document.getElementById('res-product-name');
    const brandEl = document.getElementById('res-product-brand');
    const categoryEl = document.getElementById('res-category');
    const matchEl = document.getElementById('res-match-level');
    const verifiedEl = document.getElementById('res-verified-badge');
    const reasoningEl = document.getElementById('res-reasoning-text');

    const matchLevel = prod.match_level || 'Insufficient';
    
    // Product Name & Brand
    if (prod.name) {
        nameEl.innerText = prod.name;
        brandEl.innerText = `Brand: ${prod.brand || 'Commercial Brand'}`;
        categoryEl.innerText = prod.category || 'Packaged Food';
        categoryEl.classList.remove('hidden');
    } else {
        const likelyCategory = prod.category || 'General packaged food';
        nameEl.innerText = `Likely product type: ${likelyCategory}`;
        brandEl.innerText = "Exact brand needs more distinctive ingredients or a clearer label";
        categoryEl.innerText = "Category match";
        categoryEl.classList.remove('hidden');
    }

    // Match Level Badge
    matchEl.innerText = !prod.name && prod.category ? 'Category Match' : `${matchLevel} Match`;
    matchEl.className = 'match-badge';
    if (matchLevel === 'Exact') matchEl.classList.add('exact', 'badge-exact');
    else if (matchLevel === 'Strong') matchEl.classList.add('strong', 'badge-strong');
    else if (matchLevel === 'Likely') matchEl.classList.add('likely', 'badge-likely');
    else if (matchLevel === 'Possible') matchEl.classList.add('possible', 'badge-possible');
    else matchEl.classList.add('insufficient', 'badge-insufficient');

    // Verified badge
    if (prod.verified) {
        verifiedEl.innerHTML = `<i class="fa-solid fa-shield-check"></i> Verified Packaging Source`;
        verifiedEl.className = 'verification-badge verified';
    } else {
        verifiedEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Unverified Packaging`;
        verifiedEl.className = 'verification-badge unverified';
    }

    // Reasoning
    reasoningEl.innerText = report.reasoning_summary || data.reasoning_summary || "Ingredient combination evaluated against known commercial signatures.";

    // 2. Product Review Left Column
    document.getElementById('res-taste-profile').innerText = review.taste_profile || "Taste profile not reliably known.";
    
    // Pros
    const prosList = document.getElementById('res-pros-list');
    prosList.innerHTML = '';
    const pros = review.pros || [];
    if (pros.length) {
        pros.forEach(item => {
            const row = document.createElement('li');
            const icon = document.createElement('i');
            icon.className = 'fa-solid fa-check-circle';
            const text = document.createElement('span');
            text.textContent = String(item);
            row.append(icon, text);
            prosList.appendChild(row);
        });
    } else {
        prosList.innerHTML = `<li class="text-muted">No specific verified advantages noted.</li>`;
    }

    // Cons
    const consList = document.getElementById('res-cons-list');
    consList.innerHTML = '';
    const cons = review.cons || [];
    if (cons.length) {
        cons.forEach(item => {
            const row = document.createElement('li');
            const icon = document.createElement('i');
            icon.className = 'fa-solid fa-circle-exclamation';
            const text = document.createElement('span');
            text.textContent = String(item);
            row.append(icon, text);
            consList.appendChild(row);
        });
    } else {
        consList.innerHTML = `<li class="text-muted">No major specific concerns identified.</li>`;
    }

    // Overall Review
    document.getElementById('res-overall-review').innerText = review.overall || "Balanced review unavailable.";

    // 3. Finished Product Alternative Card (Right Column)
    const altCard = document.getElementById('res-alternative-card');
    const altNameEl = document.getElementById('res-alt-name');
    const altBrandEl = document.getElementById('res-alt-brand');
    const altReasonEl = document.getElementById('res-alt-reason');
    const altOptionsEl = document.getElementById('res-alt-options');

    if (alt && alt.name) {
        altCard.classList.remove('hidden');
        altNameEl.innerText = alt.name;
        altBrandEl.innerText = alt.brand ? `Brand: ${alt.brand}` : "Commercial Food Brand";
        altReasonEl.innerText = alt.reason || "Provides a cleaner, balanced nutritional formulation.";
        if (altOptionsEl) {
            altOptionsEl.replaceChildren();
            (alt.alternatives || []).filter(option => option && option.name && option.name !== alt.name).forEach(option => {
                const item = document.createElement('li');
                item.textContent = option.name;
                altOptionsEl.appendChild(item);
            });
        }
    } else {
        altNameEl.innerText = "No Specific Alternative Needed / Identified";
        altBrandEl.innerText = "";
        altReasonEl.innerText = alt.reason || "Provide a complete ingredient list to receive finished food product recommendations.";
        if (altOptionsEl) altOptionsEl.replaceChildren();
    }

    // Accuracy Note
    document.getElementById('res-accuracy-note').innerText = report.accuracy_note || data.accuracy_note || "Factual accuracy prioritized. Never invent product claims or reviews.";

    // Normalized Ingredient Chips
    const chipsContainer = document.getElementById('res-ingredient-chips');
    const countEl = document.getElementById('res-ing-count');
    chipsContainer.innerHTML = '';
    const ingredients = report.input_ingredients || data.input_ingredients || [];
    countEl.innerText = ingredients.length;
    
    ingredients.forEach(ing => {
        const chip = document.createElement('span');
        chip.className = 'ing-chip';
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-tag';
        const text = document.createTextNode(` ${String(ing)}`);
        chip.append(icon, text);
        chipsContainer.appendChild(chip);
    });

    // Present the backend's personalized allergy, dietary, and ingredient-avoid findings.
    const safetySummary = document.getElementById('personal-safety-summary');
    const safetyStatus = document.getElementById('res-safety-status');
    const safetyText = document.getElementById('res-safety-summary');
    const findingsContainer = document.getElementById('res-safety-findings');
    if (safetySummary && data.status) {
        safetySummary.className = `personal-safety-summary safety-${String(data.status).toLowerCase()}`;
        safetySummary.classList.remove('hidden');
        safetyStatus.textContent = `${String(data.status).charAt(0)}${String(data.status).slice(1).toLowerCase()} for your profile`;
        const summary = data.overall_summary;
        safetyText.textContent = (typeof summary === 'string' ? summary : summary?.description) || 'Your ingredients were checked against your saved health and dietary profile.';
        if (typeof summary === 'object' && summary?.recommended_action) {
            safetyText.textContent += ` ${summary.recommended_action}`;
        }
        findingsContainer.replaceChildren();
        (data.ingredients || []).forEach(item => {
            const finding = document.createElement('div');
            finding.className = `safety-finding finding-${String(item.status || 'info').toLowerCase()}`;
            const name = document.createElement('strong');
            name.textContent = item.detected_name || item.ingredient || 'Ingredient';
            const detail = document.createElement('span');
            detail.textContent = item.reason || item.status || 'Reviewed';
            finding.append(name, detail);
            findingsContainer.appendChild(finding);
        });
    } else if (safetySummary) {
        safetySummary.classList.add('hidden');
    }
}

// Back to Scan View
document.getElementById('btn-back-to-scan')?.addEventListener('click', () => {
    switchView('view-scan');
});

// --- RAW JSON MODAL & COPY ---
const jsonModal = document.getElementById('json-modal');
const jsonModalCode = document.getElementById('json-modal-code');

document.getElementById('btn-view-json')?.addEventListener('click', () => {
    if (!state.currentResultData) return;
    jsonModalCode.textContent = JSON.stringify(state.currentResultData, null, 2);
    jsonModal.classList.remove('hidden');
});

document.getElementById('btn-close-json-modal')?.addEventListener('click', () => {
    jsonModal.classList.add('hidden');
});

document.getElementById('btn-modal-close')?.addEventListener('click', () => {
    jsonModal.classList.add('hidden');
});

document.getElementById('btn-copy-json')?.addEventListener('click', () => {
    if (!state.currentResultData) return;
    const jsonStr = JSON.stringify(state.currentResultData, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
        showToast("JSON copied to clipboard!");
    }).catch(() => {
        showToast("Could not copy JSON.", "error");
    });
});

document.getElementById('btn-modal-copy-json')?.addEventListener('click', () => {
    if (!state.currentResultData) return;
    const jsonStr = JSON.stringify(state.currentResultData, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
        showToast("JSON copied to clipboard!");
    });
});

// --- HISTORY & PROFILE ---

async function loadHistory() {
    try {
        const res = await fetch('/api/history');
        if (!res.ok) throw new Error();
        
        const data = await res.json();
        const container = document.getElementById('history-list-container');
        const emptyState = document.getElementById('history-empty-state');
        
        container.innerHTML = '';
        
        if (data.history.length === 0) {
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
            
            data.history.forEach(scan => {
                const card = document.createElement('article');
                card.className = 'history-card';
                const header = document.createElement('div');
                header.className = 'history-card-header';
                const date = document.createElement('span');
                date.className = 'history-date';
                const parsedDate = new Date(scan.created_at);
                date.textContent = Number.isNaN(parsedDate.getTime()) ? 'Date unavailable' : parsedDate.toLocaleDateString();
                const status = document.createElement('span');
                status.className = `history-status-badge ${String(scan.status || '').toLowerCase()}`;
                status.textContent = String(scan.status || 'Reviewed');
                header.append(date, status);
                const warning = document.createElement('div');
                warning.className = 'history-warning';
                warning.textContent = scan.main_warning || 'Product Scan Record';
                const button = document.createElement('button');
                button.className = 'btn btn-outline btn-sm btn-block';
                button.type = 'button';
                const icon = document.createElement('i');
                icon.className = 'fa-solid fa-chart-simple';
                button.append(icon, document.createTextNode(' View Report'));
                button.addEventListener('click', () => window.viewHistoryDetail(scan.id));
                card.append(header, warning, button);
                container.appendChild(card);
            });
        }
    } catch (e) {
        showToast("Error loading scan history.", "error");
    }
}

window.viewHistoryDetail = async function(scanId) {
    try {
        const res = await fetch(`/api/history/${scanId}`);
        if (!res.ok) {
            showToast("Failed to retrieve historic report.", "error");
            return;
        }
        
        const data = await res.json();
        // The history API stores the product report under recommendations.
        // Reuse it with persisted screening findings instead of re-running analysis.
        const savedReport = data.product_identification || data.recommendations;
        if (savedReport && !Array.isArray(savedReport)) {
            state.currentResultData = {
                product_identification: savedReport,
                status: data.status,
                ingredients: data.ingredients || []
            };
            renderIdentificationResults(state.currentResultData);
        } else {
            // Re-run identification on parsed/raw text
            const reIdentifyRes = await fetch('/api/identify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ ingredients: data.parsed_text || data.raw_text })
            });
            const identData = await reIdentifyRes.json();
            state.currentResultData = identData;
            renderIdentificationResults(identData);
        }
        switchView('view-analysis');
    } catch (e) {
        showToast("Connection error loading scan.", "error");
    }
};

// Profile Load & Save
// Profile Load & Save
async function loadProfile() {
    try {
        const res = await fetch('/api/profile');
        if (!res.ok) return;
        const data = await res.json();
        const prof = data.profile || data;
        
        // Age range
        const ageVal = prof.age_range || data.age_range || '25-34';
        const ageSelect = document.getElementById('profile-age');
        if (ageSelect) ageSelect.value = ageVal;

        // Vegetarian & Vegan
    const isVeg = prof.is_vegetarian ?? prof.vegetarian ?? prof.vegetarian_status ?? data.vegetarian_status;
        
        const vegEl = document.getElementById('profile-vegetarian');
        const nonVegEl = document.getElementById('profile-non-vegetarian');
        if (vegEl) vegEl.checked = !!isVeg;
        if (nonVegEl) nonVegEl.checked = !isVeg;
        
        // Allergies
        const allergiesContainer = document.getElementById('profile-allergies-container');
        if (allergiesContainer) {
            allergiesContainer.innerHTML = '';
            const allAllergens = data.all_allergens || data.system_allergens || [
                {name: "Milk"}, {name: "Egg"}, {name: "Peanut"}, {name: "Tree nuts"},
                {name: "Soy"}, {name: "Wheat/gluten"}, {name: "Fish"}, {name: "Shellfish"}, {name: "Sesame"}
            ];
            const userAllergies = prof.allergies || prof.allergens || data.user_allergies || [];
            
            allAllergens.forEach(allergen => {
                const aName = allergen.name || allergen;
                const isChecked = userAllergies.some(ua => ua.toLowerCase() === aName.toLowerCase());
                const label = document.createElement('label');
                label.className = 'checkbox-pill';
                const input = document.createElement('input');
                input.type = 'checkbox';
                input.name = 'allergies';
                input.value = aName;
                input.checked = isChecked;
                const text = document.createElement('span');
                text.textContent = aName;
                label.append(input, text);
                allergiesContainer.appendChild(label);
            });
        }
        
        // Health Goals / Preferences
        const userPrefs = prof.preferences || data.preferences || [];
        document.querySelectorAll('input[name="preferences"]').forEach(prefInput => {
            prefInput.checked = userPrefs.includes(prefInput.value);
        });

        // Avoid list
        state.profileAvoidList = (prof.avoid_ingredients || data.avoid_ingredients || []).map(x => String(x));
        renderAvoidTags();
    } catch (e) {
        console.error("Profile load failed", e);
    }
}

function renderAvoidTags() {
    const container = document.getElementById('profile-avoid-tags-container');
    if (!container) return;
    container.innerHTML = '';
    state.profileAvoidList.forEach((tag, idx) => {
        const span = document.createElement('span');
        span.className = 'tag-badge';
        const label = document.createElement('span');
        label.textContent = tag;
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'remove-tag-btn';
        button.dataset.index = idx;
        button.setAttribute('aria-label', `Remove ${tag}`);
        button.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
        span.append(label, button);
        container.appendChild(span);
    });

    container.querySelectorAll('.remove-tag-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = Number(e.currentTarget.dataset.index);
            state.profileAvoidList.splice(idx, 1);
            renderAvoidTags();
        });
    });
}

document.getElementById('btn-add-avoid-tag')?.addEventListener('click', () => {
    const input = document.getElementById('profile-avoid-input');
    const val = input.value.trim();
    if (val && !state.profileAvoidList.includes(val)) {
        state.profileAvoidList.push(val);
        input.value = '';
        renderAvoidTags();
    }
});

document.getElementById('profile-avoid-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('btn-add-avoid-tag')?.click();
    }
});

document.getElementById('profile-vegetarian')?.addEventListener('change', (e) => {
    if (e.currentTarget.checked) {
        const nonVegEl = document.getElementById('profile-non-vegetarian');
        if (nonVegEl) nonVegEl.checked = false;
    }
});

document.getElementById('profile-non-vegetarian')?.addEventListener('change', (e) => {
    if (e.currentTarget.checked) {
        const vegEl = document.getElementById('profile-vegetarian');
        if (vegEl) vegEl.checked = false;
    }
});

document.getElementById('form-profile')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const selectedAllergies = Array.from(document.querySelectorAll('input[name="allergies"]:checked')).map(el => el.value);
    const selectedPrefs = Array.from(document.querySelectorAll('input[name="preferences"]:checked')).map(el => el.value);
    
    const payload = {
        age_range: document.getElementById('profile-age').value,
        vegetarian: document.getElementById('profile-vegetarian').checked,
        non_vegetarian: document.getElementById('profile-non-vegetarian').checked,
        allergies: selectedAllergies,
        preferences: selectedPrefs,
        avoid_ingredients: state.profileAvoidList
    };
    
    try {
        const res = await fetch('/api/profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            showToast("Health & dietary profile saved successfully!");
        } else {
            showToast("Failed to save profile.", "error");
        }
    } catch (err) {
        showToast("Connection error saving profile.", "error");
    }
});

// App init
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
});
