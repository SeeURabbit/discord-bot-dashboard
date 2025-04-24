document.addEventListener('DOMContentLoaded', () => {
	const newsList = document.getElementById('news-list');

	// Sample data
	const articles = [
		{
			title: 'New Study Reveals Climate Change Impact',
			date: '2025-04-20',
			summary: 'A recent study shows the significant effects of climate change on global weather patterns.'
		},
		{
			title: 'Tech Giants Release Joint AI Statement',
			date: '2025-04-19',
			summary: 'Leading technology companies have released a joint statement on the ethical use of AI.'
		},
		{
			title: 'Breakthrough in Renewable Energy Storage',
			date: '2025-04-18',
			summary: 'Scientists have developed a new method for storing renewable energy more efficiently.'
		}
	];

	const toggleTheme = document.getElementById('toggleTheme');
	const savedTheme = localStorage.getItem('theme');

	if (savedTheme === 'light') {
		document.body.classList.add('light-mode');
		if (toggleTheme) toggleTheme.checked = true;
	}

	toggleTheme?.addEventListener('change', () => {
		document.body.classList.toggle('light-mode');
		localStorage.setItem('theme', document.body.classList.contains('light-mode') ? 'light' : 'dark');
	});

	articles.forEach(article => {
		const item = document.createElement('div');
		item.className = 'news-item';

		const title = document.createElement('h2');
		title.textContent = article.title;

		const date = document.createElement('time');
		date.textContent = new Date(article.date).toLocaleDateString();

		const summary = document.createElement('p');
		summary.textContent = article.summary;

		item.appendChild(title);
		item.appendChild(date);
		item.appendChild(summary);

		newsList.appendChild(item);
	});
});
