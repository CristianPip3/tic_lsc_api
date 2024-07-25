const socket = io("http://127.0.0.1:5000");
let isSender = true;

socket.on("message", function (msg) {
  const item = document.createElement("div");
  item.textContent = msg;
  item.classList.add("message");
  item.classList.add(isSender ? "sender" : "receiver");
  document.getElementById("chat").appendChild(item);
  isSender = !isSender; // Alternar entre emisor y receptor
});

let mediaRecorder;
let audioChunks = [];
document.getElementById("record").addEventListener("click", function () {
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.addEventListener("dataavailable", (event) => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks);
      const formData = new FormData();
      formData.append("audio", audioBlob);

      fetch("http://127.0.0.1:5000/transcribe", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data.text);
          socket.send(data.text); // Enviar el texto transcrito al chat
        });

      audioChunks = [];
    });

    setTimeout(() => {
      mediaRecorder.stop();
    }, 5000); // Grabar por 5 segundos
  });
});
