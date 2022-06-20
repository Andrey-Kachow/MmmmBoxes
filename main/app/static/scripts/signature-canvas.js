// globals
const loadingUrl = "https://media3.giphy.com/media/3oEjI6SIIHBdRxXI40/200.gif";

let signatureProcessingUrl = null;
let signatureRequestUrl = null;
let signatureResidentName = null;
let signaturePackageTitle = null;
let signaturePackageId = null;
let signatureBtnTableCell = null;

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

function openSignatureCanvas(signBtn, ownerFullName, packageTitle, packageId) {
  closeRequestedSignatureDisplay();
  signaturePad.clear();
  signatureBtnTableCell = signBtn.parentElement;
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
  const pid = signaturePackageId;
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
    success: () => notifySuccessfulSignature(pid),
    error: () => notifyFailedSignatureSent(),
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
    error: () => notifyFailedSignatureRequest(),
  });
}

function showRequestedSignature(response) {
  setTimeout(() => {
    document.getElementById("signature-display").src = response.dataUrl;
    document.getElementById("signature-loading-info").textContent =
      "received OK!";
  }, 500);
}

function openRequestedSignatureDisplay() {
  closeSignatureCanvas();
  document.getElementById("signature-loading-info").textContent = "loading...";
  document.getElementById("signature-display").src = loadingUrl;
  document
    .getElementById("requested-signature-display-wrapper")
    .classList.remove("hidden-signature");
}

function closeRequestedSignatureDisplay() {
  document
    .getElementById("requested-signature-display-wrapper")
    .classList.add("hidden-signature");
}

function notifySuccessfulSignature(pid) {
  updateSignatureSubmittedCell(signatureBtnTableCell, pid);
}

function notifyFailedSignatureSent() {
  alert("Could not submit signature!");
}

function notifyFailedSignatureRequest() {
  alert("Could not get signature!");
}

function updateSignatureSubmittedCell(cell, pid) {
  removeAllChildNodes(cell);
  const span = document.createElement("span");
  const button = document.createElement("button");
  span.textContent = "Signed";
  button.textContent = "View";
  button.addEventListener("click", () => requestSignatureFromServer(pid));
  cell.appendChild(span);
  cell.appendChild(button);
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
