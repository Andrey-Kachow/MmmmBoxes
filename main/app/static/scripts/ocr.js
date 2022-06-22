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
  if (data.name == null) {
    notifyCouldNotReadRecipientName();
    return;
  }
  else if (data.title == null) {
    notifyCouldNotReadPackageTitle();
    return;
  }
  document.getElementById("package-title").value = data.title;

  if (!residentNames.includes(data.name)) {
    notifyResidentNameDoesNotMatchExistingOne();
    return;
  }
  document.getElementById("resident-name-inp").value = data.name;
}

function notifyCouldNotGetResponse() {
  alert("Could not process uploaded image!");
}

function notifyCouldNotReadRecipientName() {
  alert("Could not read package recipient name");
}

function notifyCouldNotReadPackageTitle() {
  alert("Could not read package title");
}

function notifyFileTooLarge() {
  alert("File too large!");
}

function notifyResidentNameDoesNotMatchExistingOne() {
  alert("The read package recipient name does not match any existing resident!");
}
