function initializeResidentNames() {
  const residentButtons = document.getElementsByClassName("dropdown-content-button");
  return Array.from(residentButtons).map(it => it.textContent);
}

const MAX_OCR_FILE_SIZE = 67108864; // 64 MiB
const residentNames = initializeResidentNames();

let ocrUrl = null;

function initializeOcrUrl(url) {
  ocrUrl = url;
}

function fileTooLarge(input) {
  return input.files[0].size > MAX_OCR_FILE_SIZE;
}

function ocrSend() {
  const input = document.getElementById("ocr-image-upload-input");
  if (hasNoFiles(input)) {
    return;
  }
  if (fileTooLarge(input)) {
    notifyFileTooLarge();
    return;
  }
  ocrInfoClear();
  const formData = new FormData();
  formData.append('file', input.files[0]);
  $.ajax({
    url: ocrUrl,
    data: formData,
    dataType: "json",
    processData: false,
    contentType: false,
    type: 'POST',
    success: (data) => verifyAndAutoFill(data),
    error: () => notifyCouldNotGetResponse()
  });
}

function verifyAndAutoFill(data) {
  if (data.name == null && data.title == null) {
    notifyCouldNotReadAnything();
    return;
  }
  if (data.title == null) {
    notifyCouldNotReadPackageTitle();
    return;
  }
  document.getElementById("package-title").value = data.title;

  if (data.name == null) {
    notifyCouldNotReadRecipientName();
    return;
  }
  if (!residentNames.includes(data.name)) {
    notifyResidentNameDoesNotMatchExistingOne();
    return;
  }
  document.getElementById("resident-name-inp").value = data.name;
  notifySuccessfullOcr();
}

function notifyCouldNotGetResponse() {
  ocrStatusError();
  ocrInfo("Could not process uploaded image!");
}

function notifyCouldNotReadRecipientName() {
  ocrStatusError();
  ocrInfo("Could not read package recipient name");
}

function notifyCouldNotReadPackageTitle() {
  ocrStatusError();
  ocrInfo("Could not read package title");
}

function notifyFileTooLarge() {
  ocrStatusError();
  ocrInfo("File too large!");
}

function notifyResidentNameDoesNotMatchExistingOne() {
  ocrStatusError();
  ocrInfo("The read package recipient name does not match any existing resident!");
}

function notifySuccessfullOcr() {
  ocrStatusCorrect();
  ocrInfo("The uploaded image was processed successfully!")
}

function ocrInfo(msg) {
  document.getElementById("ocr-status-info-text").textContent = msg;
}

function ocrInfoClear() {
  ocrInfo("");
}

function ocrStatusCorrect() {
  const infoSpan = document.getElementById("ocr-status-info-text");
  infoSpan.classList.remove("ocr-error");
  infoSpan.classList.add("ocr-correct");
}

function ocrStatusError() {
  const infoSpan = document.getElementById("ocr-status-info-text");
  infoSpan.classList.remove("ocr-correct");
  infoSpan.classList.add("ocr-error");
}
