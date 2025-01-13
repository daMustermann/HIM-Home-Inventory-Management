async function getSuggestions() {
    const title = document.getElementById('title').value;
    if (!title) {
        alert('Please enter a title first');
        return;
    }

    try {
        const response = await fetch('/get_suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: title })
        });

        const suggestions = await response.json();
        displaySuggestions(suggestions);
    } catch (error) {
        console.error('Error:', error);
    }
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestionsContainer');
    const cardsContainer = document.getElementById('suggestionCards');
    cardsContainer.innerHTML = '';

    suggestions.forEach((suggestion, index) => {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-3';
        card.innerHTML = `
            <div class="card h-100" style="cursor: pointer" onclick="applySuggestion(${index})">
                <img src="${suggestion.image_url}" class="card-img-top" alt="Suggested image">
                <div class="card-body">
                    <h6 class="card-title">${suggestion.title}</h6>
                    <p class="card-text small">${suggestion.description}</p>
                </div>
            </div>
        `;
        cardsContainer.appendChild(card);
    });

    container.style.display = 'block';
}

function applySuggestion(index) {
    // Get the suggestion data
    const suggestionCards = document.getElementById('suggestionCards');
    const selectedCard = suggestionCards.children[index];
    
    // Apply the suggestion to the form
    document.getElementById('title').value = selectedCard.querySelector('.card-title').textContent;
    document.getElementById('description').value = selectedCard.querySelector('.card-text').textContent;
    document.getElementById('imagePreview').src = selectedCard.querySelector('.card-img-top').src;
    document.getElementById('imageUrl').value = selectedCard.querySelector('.card-img-top').src;
    
    // Hide suggestions
    document.getElementById('suggestionsContainer').style.display = 'none';
}