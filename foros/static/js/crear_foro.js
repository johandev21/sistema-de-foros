let fotoDePerfil = document.querySelector('#foto-de-perfil');
let inputFile = document.querySelector('#input-file');

inputFile.onchange = () => {
  fotoDePerfil.src = URL.createObjectURL(inputFile.files[0]);
}