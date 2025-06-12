// static/chat.js

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

// Butona tıklayınca popup'ı aç/kapat
document.addEventListener("DOMContentLoaded", function () {
  const chatButton = document.getElementById("chatButton");
  const chatPopup = document.getElementById("chatPopup");

  if (chatButton && chatPopup) {
    chatButton.addEventListener("click", function () {
      chatPopup.style.display =
        chatPopup.style.display === "none" ? "block" : "none";
    });
  }
});
