const recordButton = document.getElementById("record");
const chat = document.getElementById("chat");
let mediaRecorder;
let audioChunks = [];
let audioContext;
let analyser;
let dataArray;
let bufferLength;
let canvas;
let canvasCtx;

recordButton.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    recordButton.textContent = "Record";
  } else {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        recordButton.textContent = "Stop";

        mediaRecorder.addEventListener('dataavailable', event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        });

        mediaRecorder.addEventListener('stop', () => {
            if (audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const downloadLink = document.createElement('a');
                downloadLink.href = audioUrl;
                downloadLink.download = 'recording.wav';
                downloadLink.textContent = 'Download recording';
                document.body.appendChild(downloadLink);

                const formData = new FormData();
                formData.append('audio', audioBlob);

                fetch('http://127.0.0.1:5000/transcribe', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data.text);
                });

                audioChunks = [];
            } else {
                console.error('No audio data available.');
            }
        });
        setTimeout(() => {
          mediaRecorder.stop();
        }, 60000); // Grabar por 5 segundos
      })
      .catch((error) => {
        console.error("Error accessing media devices.", error);
      });
  }
});
