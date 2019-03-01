//handle homepage hash code submits

document.getElementById('btn').addEventListener('click', (e) => {
  e.preventDefault()
  const field = document.getElementById('hashcode');
  window.location.href = `/stream/${field.value}`;
})

