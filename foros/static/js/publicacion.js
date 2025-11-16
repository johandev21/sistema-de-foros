document.addEventListener('DOMContentLoaded', () => {
  // Código para el menú de la publicación
  const menuIcon = document.querySelector('[data-popover-target="postMenu"]');
  if (menuIcon) {
    const menuId = menuIcon.getAttribute('data-popover-target');
    const menu = document.querySelector(`[data-popover="${menuId}"]`);

    menuIcon.addEventListener('click', (event) => {
      event.stopPropagation();
      menu.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
      menu.classList.add('hidden');
    });
  }

  // Código para el modal de eliminación de publicación
  const deleteButton = document.querySelector('.delete-post-btn');
  const deleteModal = document.getElementById('deleteModal');
  const cancelButton = document.getElementById('cancelButton');
  const confirmDeleteButton = document.getElementById('confirmDeleteButton');
  const modalMessage = document.getElementById('modalMessage');
  let currentDeleteUrl = '';

  if (deleteButton) {
    deleteButton.addEventListener('click', (event) => {
      event.preventDefault();
      currentDeleteUrl = deleteButton.getAttribute('data-url');
      const tituloPublicacion = deleteButton.getAttribute('data-titulo');
      modalMessage.textContent = `Estás a punto de eliminar la publicación "${tituloPublicacion}". Esta acción no se puede deshacer.`;
      deleteModal.classList.remove('hidden');
    });
  }

  if (cancelButton) {
    cancelButton.addEventListener('click', () => {
      deleteModal.classList.add('hidden');
    });
  }

  if (confirmDeleteButton) {
    confirmDeleteButton.addEventListener('click', () => {
      window.location.href = currentDeleteUrl;
    });
  }

  window.addEventListener('click', (event) => {
    if (event.target === deleteModal) {
      deleteModal.classList.add('hidden');
    }
  });

  // Código para los menús de las respuestas
  const respuestaMenuIcons = document.querySelectorAll('[data-popover-target^="respuestaMenu"]');

  respuestaMenuIcons.forEach((menuIcon) => {
    const menuId = menuIcon.getAttribute('data-popover-target');
    const menu = document.querySelector(`[data-popover="${menuId}"]`);

    menuIcon.addEventListener('click', (event) => {
      event.stopPropagation();
      menu.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
      menu.classList.add('hidden');
    });
  });

  // Código para el modal de eliminación de respuesta
  const deleteRespuestaButtons = document.querySelectorAll('.delete-respuesta-btn');
  const deleteRespuestaModal = document.getElementById('deleteRespuestaModal');
  const cancelRespuestaButton = document.getElementById('cancelRespuestaButton');
  const confirmDeleteRespuestaButton = document.getElementById('confirmDeleteRespuestaButton');
  const modalRespuestaMessage = document.getElementById('modalRespuestaMessage');
  let currentDeleteRespuestaUrl = '';

  deleteRespuestaButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      currentDeleteRespuestaUrl = button.getAttribute('data-url');
      const textoRespuesta = button.getAttribute('data-texto');
      modalRespuestaMessage.textContent = `Estás a punto de eliminar la respuesta: "${textoRespuesta}". Esta acción no se puede deshacer.`;
      deleteRespuestaModal.classList.remove('hidden');
    });
  });

  if (cancelRespuestaButton) {
    cancelRespuestaButton.addEventListener('click', () => {
      deleteRespuestaModal.classList.add('hidden');
    });
  }

  if (confirmDeleteRespuestaButton) {
    confirmDeleteRespuestaButton.addEventListener('click', () => {
      window.location.href = currentDeleteRespuestaUrl;
    });
  }

  window.addEventListener('click', (event) => {
    if (event.target === deleteRespuestaModal) {
      deleteRespuestaModal.classList.add('hidden');
    }
  });

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
      window.location.reload();
    }
  });
});
