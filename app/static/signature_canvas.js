function resizeCanvas(canvas) {
   const ratio = Math.max(window.devicePixelRatio || 1, 1);
   canvas.width = canvas.offsetWidth * ratio
   canvas.height = canvas.offsetHeight * ratio
   canvas.getContext("2d").scale(ratio, ratio)
}

const signatureCanvas = document.getElementById("signature-pad")

window.onresize = () => {
  resizeCanvas(signatureCanvas)
}
resizeCanvas(signatureCanvas)

let signaturePad = new SignaturePad(signatureCanvas, {
  backgroundColor: 'rgb(250,250,250)'
});

document.getElementById("signature-clear-btn").addEventListener('click', () => {signaturePad.clear()})
