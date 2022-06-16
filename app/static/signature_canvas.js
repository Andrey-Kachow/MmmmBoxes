function resizeCanvas(canvas) {
   const ratio = Math.max(window.devicePixelRatio || 1, 1);
   canvas.width = canvas.offsetWidth * ratio
   canvas.height = canvas.offsetHeight * ratio
   canvas.getContext("2d").scale(ratio, ratio)
}

function openSignatureCanvas() {
  document.getElementById("signature_canvas_wrapper").classList.remove("hidden_signature")
}

function closeSignatureCanvas() {
  document.getElementById("signature_canvas_wrapper").classList.add("hidden_signature")
  signaturePad.clear()
}


const signatureCanvas = document.getElementById("signature-pad")

window.onresize = () => {
  resizeCanvas(signatureCanvas)
}
resizeCanvas(signatureCanvas)

let signaturePad = new SignaturePad(signatureCanvas, {
  backgroundColor: 'rgb(250,250,250)',
  penColor: "rgb(69, 144, 259)"
});

document.getElementById("signature-clear-btn").addEventListener('click', () => signaturePad.clear())
document.getElementById("signature-cancel-btn").addEventListener('click', () => closeSignatureCanvas())
