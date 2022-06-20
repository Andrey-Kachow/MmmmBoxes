function showCollectionModal(packageId) {
  document.getElementById(`collect-${packageId}`).style.display = "block";
}

function closeCollectionModal(packageId) {
  document.getElementById(`collect-${packageId}`).style.display = "none";
}

function showDeletionModal(packageId) {
  document.getElementById(`delete-${packageId}`).style.display = "block";
}

function closeDeletionModal(packageId) {
  document.getElementById(`delete-${packageId}`).style.display = "none";
}
