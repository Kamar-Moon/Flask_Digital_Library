document.getElementById('search-box').addEventListener('input', function() {
    const query = this.value.trim();  // Get the input value
    if (query.length > 2) {  // Only search if query is longer than 2 characters
        fetch(`/search_book?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const resultsContainer = document.getElementById('search-results');
                resultsContainer.innerHTML = '';  // Clear previous results

                if (data.length === 0) {
                    resultsContainer.innerHTML = '<p>No results found.</p>';
                } else {
                    const resultsList = document.createElement('ul');
                    resultsList.className = 'list-group';

                    data.forEach(item => {
                        const listItem = document.createElement('li');
                        listItem.className = 'list-group-item';

                        const link = document.createElement('a');
                        link.href = `/edit_book/${item.id}`;
                        link.textContent = `${item.title} by ${item.author}`;
                        listItem.appendChild(link);

                        resultsList.appendChild(listItem);
                    });

                    resultsContainer.appendChild(resultsList);
                }
            })
            .catch(error => console.error('Error fetching search results:', error));
    }
});
