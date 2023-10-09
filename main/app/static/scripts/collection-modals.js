function showCollectionModal(packageId) {
  document.getElementById(`collect-${packageId}`).style.display = "block";
}

function showNominationModal(packageId) {
  document.getElementById(`nomination-${packageId}`).style.display = "block";
}

function closeNominationModal(packageId) {
  document.getElementById(`nomination-${packageId}`).style.display = "none";
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
