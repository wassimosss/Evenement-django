
const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
registerBtn.addEventListener('click', () => {
container.classList.add("active");
 });
loginBtn.addEventListener('click', () => {
container.classList.remove("active");
  });
const togglePassword = document.getElementById('togglePassword');
const passwordField = document.getElementById('loginPassword');
togglePassword.addEventListener('click', function () {
const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
passwordField.setAttribute('type', type);
this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
  });
