function copyLink() {
    let a = document.getElementById("link");
  
    navigator.clipboard.writeText(a.href);
  
    alert("Ссылка скопирована в буфер обмена");
}