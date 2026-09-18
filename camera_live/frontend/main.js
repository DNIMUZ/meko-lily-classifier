let currentFacing = "user";

function onRender(event) {
  if (window.rendered) {
    return;
  }

  const { height, width, debounceMs, showControls, startLabel, stopLabel, facing } = event.detail.args;
  currentFacing = facing === "environment" ? "environment" : "user";

  if (showControls) {
    Streamlit.setFrameHeight(45);
  }

  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const button = document.getElementById("button");
  const flipButton = document.getElementById("flip");

  let running = true;

  video.setAttribute("width", width);
  video.setAttribute("height", height);
  canvas.setAttribute("width", width);
  canvas.setAttribute("height", height);

  function stopStream() {
    running = false;
    if (video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
    }
  }

  function startStream(facingMode) {
    if (video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
    }
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: { ideal: facingMode } } })
      .then(function (stream) {
        video.srcObject = stream;
        video.play();
        if (running) {
          sendPicture();
        }
      })
      .catch(function (error) {
        console.log("Camera error:", error);
      });
  }

  function sendPicture() {
    if (!running) {
      return;
    }
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, width, height);
    Streamlit.setComponentValue(canvas.toDataURL("image/jpeg", 0.85));
  }

  flipButton.addEventListener("click", function () {
    currentFacing = currentFacing === "user" ? "environment" : "user";
    if (running) {
      startStream(currentFacing);
    }
  });

  button.addEventListener("click", function () {
    if (running) {
      stopStream();
    } else {
      running = true;
      startStream(currentFacing);
    }
    button.textContent = running ? stopLabel : startLabel;
  });
  button.textContent = running ? stopLabel : startLabel;

  startStream(currentFacing);
  setInterval(function () {
    if (running) {
      sendPicture();
    }
  }, debounceMs);

  window.rendered = true;
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(0);