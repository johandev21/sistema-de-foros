const profileImage = document.querySelector('#profile-image')
const navigationMenu = document.querySelector('#navigation-menu')

profileImage.addEventListener('click', (event) => {
  navigationMenu.classList.toggle('hidden')
  event.stopPropagation()
})

window.addEventListener('click', (event) => {
  if (!navigationMenu.contains(event.target)) {
    navigationMenu.classList.add('hidden')
  }
})