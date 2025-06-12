// Butona tıklanınca popup aç/kapa
console.log("Chat.js başarıyla yüklendi");

document.addEventListener("DOMContentLoaded", function () {
    const chatButton = document.getElementById("chatButton");
    const chatPopup = document.getElementById("chatPopup");

    if (chatButton && chatPopup) {
        chatButton.addEventListener("click", () => {
            chatPopup.style.display = chatPopup.style.display === "none" ? "block" : "none";
        });
    }
});

function sendToWhatsApp() {
    const message = document.getElementById("chatMessage").value;
    const phone = "905366005851";
    if (!message.trim()) {
        alert("لطفاً یک پیام بنویسید.");
        return;
    }
    const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
    window.open(url, "_blank");
}
