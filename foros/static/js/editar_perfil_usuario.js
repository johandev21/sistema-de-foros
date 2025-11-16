document.addEventListener('DOMContentLoaded', () => {
  const togglePasswordIcons = document.querySelectorAll('.toggle-password');

  togglePasswordIcons.forEach(icon => {
    icon.addEventListener('click', () => {
      const passwordInput = icon.previousElementSibling;
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('ri-eye-off-fill');
        icon.classList.add('ri-eye-fill');
      } else {
        passwordInput.type = 'password';
        icon.classList.remove('ri-eye-fill');
        icon.classList.add('ri-eye-off-fill');
      }
    });
  });
});