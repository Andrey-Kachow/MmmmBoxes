let ocrUrl = null;

function initializeOcrUrl(url) {
  ocrUrl = url;
}

function ocrSend() {
  const formData = new FormData();
  const input = document.getElementById("ocr-image-upload-input");
  if (hasNoFiles(input)) {
    return;
  }
  formData.append('file', input.files[0]);
  $.ajax({
    url: ocrUrl,
    data: formData,
    processData: false,
    contentType: false,
    type: 'POST',
    success: (data) => alert(data),
    error: () => alert("oops!")
  });
}
