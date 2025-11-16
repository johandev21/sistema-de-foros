document.addEventListener('DOMContentLoaded', function () {
  const menuIcons = document.querySelectorAll('[data-popover-target]');

  menuIcons.forEach((menuIcon) => {
    const menuId = menuIcon.getAttribute('data-popover-target');
    const menu = document.querySelector(`[data-popover="${menuId}"]`);

    menuIcon.addEventListener('click', (event) => {
      event.stopPropagation();
      menu.classList.toggle('hidden');
    });

    if (menu) {
      menu.addEventListener('click', (event) => {
        event.stopPropagation();
      });
    }
  });

  document.addEventListener('click', (event) => {
    menuIcons.forEach((menuIcon) => {
      const menuId = menuIcon.getAttribute('data-popover-target');
      const menu = document.querySelector(`[data-popover="${menuId}"]`);
      if (menu && !menu.contains(event.target) && !menuIcon.contains(event.target)) {
        menu.classList.add('hidden');
      }
    });
  });

  // Código para el modal de eliminación
  const deleteButtons = document.querySelectorAll('.delete-post-btn');
  const deleteModal = document.getElementById('deleteModal');
  const cancelButton = document.getElementById('cancelButton');
  const confirmDeleteButton = document.getElementById('confirmDeleteButton');
  const modalMessage = document.getElementById('modalMessage');
  let currentDeleteUrl = '';

  deleteButtons.forEach(button => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      currentDeleteUrl = button.getAttribute('data-url');
      const tituloPublicacion = button.getAttribute('data-titulo');
      modalMessage.textContent = `Estás a punto de eliminar la publicación "${tituloPublicacion}". Esta acción no se puede deshacer.`;
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