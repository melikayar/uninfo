function sendToWhatsApp() {
  const message = document.getElementById("chatMessage").value;
  const phone = "905366005851";
  if (!message.trim()) {
    alert("Lütfen bir mesaj yazın.");
    return;
  }
  const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
  window.open(url, "_blank");
}
