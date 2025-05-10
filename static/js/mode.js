
  document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const icon = document.querySelector('#themeBtn i');
    if (localStorage.getItem('theme') === 'dark') {
      body.classList.add('dark-mode');
      icon.classList.remove('bi-moon');
      icon.classList.add('bi-sun');
    }
  });
  function toggleTheme() {
    const body = document.body;
    const icon = document.querySelector('#themeBtn i');
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
      icon.classList.remove('bi-moon');
      icon.classList.add('bi-sun');
      localStorage.setItem('theme', 'dark');
    } else {
      icon.classList.remove('bi-sun');
      icon.classList.add('bi-moon');
      localStorage.setItem('theme', 'light');
    }
  }
