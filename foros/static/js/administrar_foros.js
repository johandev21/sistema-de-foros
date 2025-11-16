document.addEventListener('DOMContentLoaded', function () {
  const deleteButtons = document.querySelectorAll('.delete-foro-btn');
  const deleteModal = document.getElementById('deleteModal');
  const cancelButton = document.getElementById('cancelButton');
  const confirmDeleteButton = document.getElementById('confirmDeleteButton');
  let currentDeleteUrl = '';

  deleteButtons.forEach(button => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      currentDeleteUrl = button.getAttribute('data-url');
      deleteModal.classList.remove('hidden');
    });
  });

  cancelButton.addEventListener('click', () => {
    deleteModal.classList.add('hidden');
  });

  confirmDeleteButton.addEventListener('click', () => {
    window.location.href = currentDeleteUrl;
  });

  window.addEventListener('click', (event) => {
    if (event.target === deleteModal) {
      deleteModal.classList.add('hidden');
    }
  });
});