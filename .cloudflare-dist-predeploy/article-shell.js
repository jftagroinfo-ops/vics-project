async function loadArticleComponent(id, file) {
  try {
    const response = await fetch(file);
    const markup = await response.text();
    const target = document.getElementById(id);
    target.innerHTML = markup;
    target.querySelectorAll('script').forEach((oldScript) => {
      const script = document.createElement('script');
      Array.from(oldScript.attributes).forEach((attribute) => script.setAttribute(attribute.name, attribute.value));
      script.textContent = oldScript.textContent;
      oldScript.replaceWith(script);
    });
  } catch (error) {
    console.error('Unable to load site component:', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadArticleComponent('header-placeholder', 'header.html');
  loadArticleComponent('footer-placeholder', 'footer.html');
});

window.addEventListener('scroll', () => {
  const button = document.getElementById('backToTop');
  if (button) button.classList.toggle('show', window.scrollY > 400);
}, { passive: true });
