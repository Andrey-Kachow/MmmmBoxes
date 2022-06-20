// globals

let signatureProcessingUrl = null;
let signatureRequestUrl = null;
let signatureResidentName = null;
let signaturePackageTitle = null;
let signaturePackageId = null;

// function definitions

function initializeSignatureProcessingUrl(url) {
  signatureProcessingUrl = url;
}

function initializeSignatureRequestUrl(url) {
  signatureRequestUrl = url;
}

function resizeCanvas(canvas) {
  const ratio = Math.max(window.devicePixelRatio || 1, 1);
  canvas.width = canvas.offsetWidth * ratio;
  canvas.height = canvas.offsetHeight * ratio;
  canvas.getContext("2d").scale(ratio, ratio);
}

function initializeSignatureLabels(ownerFullName, packageTitle, packageId) {
  signatureResidentName = ownerFullName;
  signaturePackageTitle = packageTitle;
  signaturePackageId = packageId;
  document.getElementById("package-owner-placeholder").textContent =
    ownerFullName;
  document.getElementById("package-title-placeholder").textContent =
    packageTitle;
}

function openSignatureCanvas(ownerFullName, packageTitle, packageId) {
  closeRequestedSignatureDisplay();
  signaturePad.clear();
  initializeSignatureLabels(ownerFullName, packageTitle, packageId);
  document
    .getElementById("signature-canvas-wrapper")
    .classList.remove("hidden-signature");
}

function closeSignatureCanvas() {
  signatureResidentName = null;
  signaturePackageTitle = null;
  signaturePackageId = null;
  document
    .getElementById("signature-canvas-wrapper")
    .classList.add("hidden-signature");
}

function sendSignatureToServer() {
  alert("was sent");
  $.ajax({
    type: "POST",
    url: signatureProcessingUrl,
    data: JSON.stringify({
      fullname: signatureResidentName,
      title: signaturePackageTitle,
      packageId: signaturePackageId,
      dataUrl: signaturePad.toDataURL(),
    }),
    contentType: "application/json",
    dataType: "json",
    success: () => notifySuccessfulSignature(),
    error: () => notifyFailedSignature(),
  });
  closeSignatureCanvas();
}

function requestSignatureFromServer(packageId) {
  openRequestedSignatureDisplay();
  $.ajax({
    type: "POST",
    url: signatureRequestUrl,
    data: JSON.stringify({ packageId: packageId }),
    contentType: "application/json",
    dataType: "json",
    success: (response) => showRequestedSignature(response),
    error: () => notifyFailedSignature(),
  });
}

function showRequestedSignature(response) {
  document.getElementById("signature-display").src = response.dataUrl;
  document.getElementById("signature-loading-info").textContent =
    "received OK!";
}

function openRequestedSignatureDisplay() {
  closeSignatureCanvas();
  document.getElementById("signature-loading-info").textContent = "loading...";
  document
    .getElementById("requested-signature-display-wrapper")
    .classList.remove("hidden-signature");
}

function closeRequestedSignatureDisplay() {
  document
    .getElementById("requested-signature-display-wrapper")
    .classList.add("hidden-signature");
}

function notifySuccessfulSignature() {
  // alert("success")
}

function notifyFailedSignature() {
  // alert("failure")
}

// Initializing Canvas, SignaturePad

const signatureCanvas = document.getElementById("signature-pad");

window.onresize = () => {
  resizeCanvas(signatureCanvas);
};

resizeCanvas(signatureCanvas);

let signaturePad = new SignaturePad(signatureCanvas, {
  backgroundColor: "rgb(250,250,250)",
  penColor: "rgb(69, 144, 259)",
});

// Adding events to the signature pad buttons

document
  .getElementById("signature-clear-btn")
  .addEventListener("click", () => signaturePad.clear());
document
  .getElementById("signature-cancel-btn")
  .addEventListener("click", () => closeSignatureCanvas());
document
  .getElementById("signature-submit-btn")
  .addEventListener("click", () => sendSignatureToServer());
