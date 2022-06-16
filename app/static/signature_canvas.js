// globals

let signatureProcessingUrl = null
let signatureResidentName = null
let signaturePackageTitle = null
let signaturePackageId = null

// function definitions

function initializeSignatureProcessingUrl(url) {
  signatureProcessingUrl = url
}

function resizeCanvas(canvas) {
  const ratio = Math.max(window.devicePixelRatio || 1, 1);
  canvas.width = canvas.offsetWidth * ratio
  canvas.height = canvas.offsetHeight * ratio
  canvas.getContext("2d").scale(ratio, ratio)
}

function initializeSignatureLabels(ownerFullName, packageTitle, packageId) {
  signatureResidentName = ownerFullName
  signaturePackageTitle = packageTitle
  signaturePackageId = packageId
  document.getElementById("package_owner_placeholder").textContent = ownerFullName
  document.getElementById("package_title_placeholder").textContent = packageTitle
}

function openSignatureCanvas(ownerFullName, packageTitle) {
  signaturePad.clear()
  initializeSignatureLabels(ownerFullName, packageTitle)
  document.getElementById("signature_canvas_wrapper").classList.remove("hidden_signature")
}

function closeSignatureCanvas() {
  document.getElementById("signature_canvas_wrapper").classList.add("hidden_signature")
}

function sendSignatureToServer() {
  alert("was sent")
  $.ajax({
    type: "POST",
    url: signatureProcessingUrl,
    data: JSON.stringify({
      fullname: signatureResidentName,
      title: signaturePackageTitle,
      pid: signaturePackageId,
      dataUrl: signaturePad.toDataURL(),
    }),
    contentType: "application/json",
    dataType: 'json',
    success: () => notifySuccessfulSignature(),
    failure: () => notifyFailedSignature()
  });
  closeSignatureCanvas()
}

function notifySuccessfulSignature() {
  alert("success")
}

function notifyFailedSignature() {
  alert("failure")
}

// Initializing Canvas, SignaturePad

const signatureCanvas = document.getElementById("signature-pad")

window.onresize = () => {
  resizeCanvas(signatureCanvas)
}
resizeCanvas(signatureCanvas)

let signaturePad = new SignaturePad(signatureCanvas, {
  backgroundColor: 'rgb(250,250,250)',
  penColor: "rgb(69, 144, 259)"
});

// Adding events to the signature pad buttons

document.getElementById("signature-clear-btn").addEventListener('click', () => signaturePad.clear())
document.getElementById("signature-cancel-btn").addEventListener('click', () => closeSignatureCanvas())
document.getElementById("signature-submit-btn").addEventListener('click', () => sendSignatureToServer())
