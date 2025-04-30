document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const fetchButton = document.getElementById('fetchButton');
    const messageArea = document.getElementById('messageArea');
    const repoList = document.getElementById('repoList');

    fetchButton.addEventListener('click', async () => {
        const username = usernameInput.value.trim();

        if (!username) {
            messageArea.textContent = 'Please enter a GitHub username.';
            return;
        }

        messageArea.textContent = 'Loading...';
        repoList.innerHTML = ''; // Clear previous results

        try {
            const response = await fetch(`https://api.github.com/users/${username}/repos`);

            if (!response.ok) {
                throw new Error(`GitHub API Error: ${response.status}`);
            }

            const repos = await response.json();

            messageArea.textContent = ''; // Clear loading message

            if (repos.length === 0) {
                messageArea.textContent = 'No public repositories found for this user.';
                return;
            }

            repos.forEach(repo => {
                const repoDiv = document.createElement('div');
                repoDiv.innerHTML = `<div class="repo-name">${repo.name}</div>
                                     <div class="repo-description">${repo.description ? repo.description : 'No description available.'}</div>
                                     <div class="repo-language">Language: ${repo.language ? repo.language : 'Not specified'}</div>`;
                repoList.appendChild(repoDiv);
            });

        } catch (error) {
            messageArea.textContent = `Error: ${error.message}`;
        }
    });
});