document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addItemForm');
    const suggestionsBtn = document.getElementById('getSuggestionsBtn');
    const locationFilter = document.getElementById('locationFilter');
    const sortBy = document.getElementById('sortBy');

    if (suggestionsBtn) {
        suggestionsBtn.addEventListener('click', handleSuggestions);
    }

    if (form) {
        form.addEventListener('submit', handleSubmit);
    }

    if (locationFilter && sortBy) {
        locationFilter.addEventListener('change', updateItems);
        sortBy.addEventListener('change', updateItems);
    }

    loadLocations();
});

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    let searchTimeout;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.length > 0) {
                    searchResults.innerHTML = data.map(item => `
                        <a href="/item/${item.id}" class="search-result-item">
                            <div class="search-result-title">${item.title}</div>
                            <div class="search-result-location">${item.location}</div>
                        </a>
                    `).join('');
                } else {
                    searchResults.innerHTML = '<div class="search-no-results">No items found</div>';
                }
                
                searchResults.style.display = 'block';
            } catch (error) {
                console.error('Search error:', error);
                searchResults.innerHTML = '<div class="search-error">Error performing search</div>';
            }
        }, 300);
    });

    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const addItemForm = document.getElementById('addItemForm');
    if (addItemForm) {
        const submitButton = addItemForm.querySelector('button[type="submit"]');
        
        addItemForm.onsubmit = function() {
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
            }
            return true; // Allow form to submit normally
        };
    }
});

async function handleSuggestions() {
    const titleInput = document.getElementById('title');
    const spinner = document.getElementById('loadingSpinner');
    const container = document.getElementById('suggestionsContainer');

    if (!titleInput.value) {
        alert('Please enter a title first');
        return;
    }

    try {
        spinner.classList.remove('d-none');
        container.innerHTML = '';

        const response = await fetch('/get_suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ title: titleInput.value })
        });

        const data = await response.json();
        displaySuggestions(data);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    } finally {
        spinner.classList.add('d-none');
    }
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestionsContainer');
    container.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${suggestion.title}</h5>
                <p class="card-text">${suggestion.description}</p>
                <div class="suggestion-image-container" style="height: 200px; width: 100%; background: #f8f9fa; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                    <img src="${suggestion.image_url}" 
                         class="img-fluid suggestion-image" 
                         style="max-height: 200px; width: auto; object-fit: contain; opacity: 0; transition: opacity 0.3s ease;"
                         onerror="this.src='https://via.placeholder.com/400x300?text=${encodeURIComponent(suggestion.title)}'; this.style.opacity = '1';"
                         onload="this.style.opacity = '1';"
                         alt="${suggestion.title}">
                </div>
                <button type="button" class="btn btn-sm btn-primary" onclick="applySuggestion(${index})">
                    Use This
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

function applySuggestion(index) {
    const suggestions = document.querySelectorAll('#suggestionsContainer .card');
    const selected = suggestions[index];
    
    document.getElementById('title').value = selected.querySelector('.card-title').textContent;
    document.getElementById('description').value = selected.querySelector('.card-text').textContent;
    
    document.getElementById('suggestionsContainer').innerHTML = '';
}

async function handleSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/add-item', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: formData
        });

        // First check if the response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const result = await response.json();
            if (result.success) {
                window.location.href = '/';  // Redirect to home page
                return;
            } else {
                throw new Error(result.error || 'Failed to add item');
            }
        } else {
            // If not JSON, the server probably returned a redirect
            window.location.href = '/';
            return;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add item: ' + error.message);
    }

    // Save location if needed
    const locationInput = document.getElementById('location').value;
    if (locationInput) {
        try {
            await fetch('/locations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ name: locationInput })
            });
        } catch (error) {
            console.error('Error saving location:', error);
        }
    }
}

function toggleForm(show) {
    const form = document.getElementById('itemFormContainer');
    form.style.display = show ? 'block' : 'none';
}

function incrementQuantity() {
    const input = document.getElementById('quantity');
    input.value = parseInt(input.value) + 1;
}

function decrementQuantity() {
    const input = document.getElementById('quantity');
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

async function loadLocations() {
    try {
        const response = await fetch('/locations');
        const locations = await response.json();
        
        const dropdown = document.getElementById('locationsDropdown');
        const datalist = document.getElementById('locationsList');
        
        // Clear existing options
        dropdown.innerHTML = '';
        datalist.innerHTML = '';
        
        locations.forEach(location => {
            // Add to dropdown
            const item = document.createElement('a');
            item.className = 'dropdown-item';
            item.href = '#';
            item.textContent = location;
            item.onclick = (e) => {
                e.preventDefault();
                document.getElementById('location').value = location;
            };
            dropdown.appendChild(item);
            
            // Add to datalist
            const option = document.createElement('option');
            option.value = location;
            datalist.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

function updateItems() {
    const location = document.getElementById('locationFilter').value;
    const sort = document.getElementById('sortBy').value;
    const currentUrl = new URL(window.location);
    
    currentUrl.searchParams.set('location', location);
    currentUrl.searchParams.set('sort', sort);
    
    window.location = currentUrl;
}

async function previewImageUrl() {
    const urlInput = document.getElementById('image_url');
    const preview = document.getElementById('imagePreview');
    const previewImg = preview.querySelector('img');
    
    if (!urlInput.value) {
        alert('Please enter an image URL');
        return;
    }
    
    try {
        previewImg.src = urlInput.value;
        preview.style.display = 'block';
        
        previewImg.onerror = () => {
            alert('Failed to load image from URL');
            preview.style.display = 'none';
        };
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to preview image');
    }
}

// Clear file input when URL is entered and vice versa
document.getElementById('image_url').addEventListener('input', function() {
    if (this.value) document.getElementById('image').value = '';
});

document.getElementById('image').addEventListener('change', function() {
    if (this.value) document.getElementById('image_url').value = '';
});