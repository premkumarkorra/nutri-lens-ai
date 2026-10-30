/**
 * Advanced UI Features for NutriLens AI
 * Includes: Image manipulation, confidence display, text editing, animations
 */

// Global state for image manipulation
const imageState = {
    rotation: 0,
    brightness: 100,
    contrast: 100,
    originalFile: null
};

// Initialize Advanced Features
document.addEventListener('DOMContentLoaded', function() {
    initializeImageManipulation();
    initializeAdvancedAnimations();
    initializeTooltips();
});

/**
 * Image Manipulation Features
 */
function initializeImageManipulation() {
    const imagePreview = document.getElementById('image-preview');
    
    if (!imagePreview) return;
    
    // Add image manipulation controls
    const preview = imagePreview.closest('.preview-container');
    if (!preview) return;
    
    // Create image controls container
    const controlsHTML = `
        <div class="image-controls" style="padding: 1rem; border-top: 1px solid var(--border-color); display: flex; gap: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 150px;">
                <label style="display: block; font-size: 0.85rem; margin-bottom: 0.5rem;">Rotate: <span id="rotation-value">0°</span></label>
                <input type="range" id="rotation-slider" min="-180" max="180" value="0" style="width: 100%;">
            </div>
            <div style="flex: 1; min-width: 150px;">
                <label style="display: block; font-size: 0.85rem; margin-bottom: 0.5rem;">Brightness: <span id="brightness-value">100%</span></label>
                <input type="range" id="brightness-slider" min="50" max="150" value="100" style="width: 100%;">
            </div>
            <div style="flex: 1; min-width: 150px;">
                <label style="display: block; font-size: 0.85rem; margin-bottom: 0.5rem;">Contrast: <span id="contrast-value">100%</span></label>
                <input type="range" id="contrast-slider" min="50" max="150" value="100" style="width: 100%;">
            </div>
            <button class="btn btn-outline" id="reset-image-controls" style="align-self: flex-end;">
                <i class="fa-solid fa-rotate-right"></i> Reset
            </button>
        </div>
    `;
    
    preview.insertAdjacentHTML('beforeend', controlsHTML);
    
    // Setup event listeners for image controls
    const rotationSlider = document.getElementById('rotation-slider');
    const brightnessSlider = document.getElementById('brightness-slider');
    const contrastSlider = document.getElementById('contrast-slider');
    const resetButton = document.getElementById('reset-image-controls');
    
    if (rotationSlider) {
        rotationSlider.addEventListener('input', function() {
            imageState.rotation = parseInt(this.value);
            updateImageFilters();
            document.getElementById('rotation-value').textContent = imageState.rotation + '°';
        });
    }
    
    if (brightnessSlider) {
        brightnessSlider.addEventListener('input', function() {
            imageState.brightness = parseInt(this.value);
            updateImageFilters();
            document.getElementById('brightness-value').textContent = imageState.brightness + '%';
        });
    }
    
    if (contrastSlider) {
        contrastSlider.addEventListener('input', function() {
            imageState.contrast = parseInt(this.value);
            updateImageFilters();
            document.getElementById('contrast-value').textContent = imageState.contrast + '%';
        });
    }
    
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            imageState.rotation = 0;
            imageState.brightness = 100;
            imageState.contrast = 100;
            document.getElementById('rotation-slider').value = 0;
            document.getElementById('brightness-slider').value = 100;
            document.getElementById('contrast-slider').value = 100;
            document.getElementById('rotation-value').textContent = '0°';
            document.getElementById('brightness-value').textContent = '100%';
            document.getElementById('contrast-value').textContent = '100%';
            updateImageFilters();
            showNotification('Image filters reset', 'info');
        });
    }
}

function updateImageFilters() {
    const imagePreview = document.getElementById('image-preview');
    if (!imagePreview) return;
    
    const filters = [
        `brightness(${imageState.brightness}%)`,
        `contrast(${imageState.contrast}%)`,
        `rotate(${imageState.rotation}deg)`
    ];
    
    imagePreview.style.filter = filters.join(' ');
    imagePreview.style.transform = `rotate(${imageState.rotation}deg)`;
}

/**
 * Display OCR Confidence Score
 */
function displayConfidenceScore(confidence) {
    const container = document.getElementById('ocr-review-container');
    if (!container) return;
    
    // Remove existing confidence badge if present
    const existingBadge = container.querySelector('.confidence-badge');
    if (existingBadge) {
        existingBadge.remove();
    }
    
    const confidence_val = Math.round(confidence);
    const color = confidence_val >= 75 ? 'success' : 
                  confidence_val >= 50 ? 'warning' : 'danger';
    
    const badgeHTML = `
        <div class="confidence-badge" style="margin-bottom: 1rem;">
            <i class="fa-solid fa-chart-pie"></i>
            <span>OCR Confidence: <strong>${confidence_val}%</strong></span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-bar-fill" style="width: ${confidence_val}%; background: ${
                color === 'success' ? 'linear-gradient(90deg, #22C55E, #10B981)' :
                color === 'warning' ? 'linear-gradient(90deg, #F59E0B, #FBBF24)' :
                'linear-gradient(90deg, #EF4444, #F97316)'
            };"></div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', badgeHTML);
    
    // Add helpful message based on confidence
    if (confidence_val < 60) {
        const warningHTML = `
            <div class="alert-box warning" style="margin-bottom: 1rem;">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <div>
                    <strong>Lower Confidence Detected</strong>
                    <p>Consider reviewing and manually editing the extracted text below for accuracy.</p>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('afterbegin', warningHTML);
    }
}

/**
 * Enable Manual Text Editing
 */
function enableManualTextEditing() {
    const textContainer = document.getElementById('ocr-text-content');
    if (!textContainer) return;
    
    // Get current text
    const currentText = textContainer.textContent.trim();
    
    // Create editable textarea
    const editButtonHTML = `
        <button class="btn btn-outline" id="btn-edit-text" style="margin-bottom: 1rem;">
            <i class="fa-solid fa-pen"></i> Edit Text
        </button>
    `;
    
    textContainer.insertAdjacentHTML('beforebegin', editButtonHTML);
    
    const editButton = document.getElementById('btn-edit-text');
    if (!editButton) return;
    
    editButton.addEventListener('click', function() {
        if (this.classList.contains('editing')) {
            // Save edited text
            const textarea = document.getElementById('ocr-text-editor');
            if (textarea) {
                const editedText = textarea.value;
                // Update the display
                textContainer.innerHTML = editedText.split('\n').map(line => 
                    `<p>${escapeHtml(line)}</p>`
                ).join('');
                
                // Replace textarea with text display
                textarea.remove();
                this.innerHTML = '<i class="fa-solid fa-pen"></i> Edit Text';
                this.classList.remove('editing');
                showNotification('Text updated successfully', 'success');
            }
        } else {
            // Enable edit mode
            const editorHTML = `
                <textarea id="ocr-text-editor" class="ocr-text-editor">${currentText}</textarea>
            `;
            textContainer.innerHTML = editorHTML;
            this.innerHTML = '<i class="fa-solid fa-check"></i> Save Changes';
            this.classList.add('editing');
        }
    });
}

/**
 * Advanced Animations
 */
function initializeAdvancedAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideUp 0.5s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all panel cards
    document.querySelectorAll('.panel-card').forEach(card => {
        card.style.opacity = '0';
        observer.observe(card);
    });
    
    // Animate ingredient tags
    animateIngredientTags();
}

function animateIngredientTags() {
    const tags = document.querySelectorAll('.tag');
    tags.forEach((tag, index) => {
        tag.style.animation = `slideUp 0.4s ease ${index * 0.05}s forwards`;
        tag.style.opacity = '0';
    });
}

/**
 * Initialize Tooltips
 */
function initializeTooltips() {
    // Add tooltips to elements with data-tooltip attribute
    const elementsWithTooltips = document.querySelectorAll('[data-tooltip]');
    elementsWithTooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this);
        });
        element.addEventListener('mouseleave', function() {
            hideTooltip(this);
        });
    });
}

function showTooltip(element) {
    const tooltipText = element.getAttribute('data-tooltip');
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-popup';
    tooltip.textContent = tooltipText;
    tooltip.style.cssText = `
        position: fixed;
        background: rgba(0, 212, 168, 0.95);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        z-index: 10000;
        pointer-events: none;
        animation: slideUp 0.2s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
    
    element._tooltip = tooltip;
}

function hideTooltip(element) {
    if (element._tooltip) {
        element._tooltip.style.animation = 'slideOutDown 0.2s ease forwards';
        setTimeout(() => {
            element._tooltip.remove();
            element._tooltip = null;
        }, 200);
    }
}

/**
 * Notification System
 */
function showNotification(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-triangle-exclamation',
        info: 'fa-info-circle'
    };
    
    const colors = {
        success: '#22C55E',
        error: '#EF4444',
        warning: '#F59E0B',
        info: '#4F8CFF'
    };
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
            <i class="fa-solid ${icons[type]}" style="color: ${colors[type]};"></i>
            <span>${message}</span>
        </div>
    `;
    
    toast.style.cssText = `
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        border: 1px solid var(--glass-border);
        border-left: 4px solid ${colors[type]};
        color: var(--text-primary);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: var(--shadow-lg);
    `;
    
    toast.classList.remove('hidden');
    toast.classList.add('show');
    
    // Auto hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 400);
    }, 4000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Export Functions for Use in Main Script
 */
window.AdvancedUI = {
    displayConfidenceScore,
    enableManualTextEditing,
    updateImageFilters,
    showNotification,
    animateIngredientTags
};
