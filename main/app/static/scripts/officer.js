function showResidents() {
  document.getElementById("dropdown-residents").style.display = "block";
}

function hideResidents() {
  document.getElementById("dropdown-residents").style.display = "none";
}

function nonButtonFocusHide() {
  const target = event.relatedTarget;
  if (target != null) {
    if (target.classList.contains("dropdown-content-button")) {
      return;
    }
  }
  hideResidents();
}

function selectResidentName(name) {
  document.getElementById("resident-name-inp").value = name;
  hideResidents();
}

function selectResidentId(id, name) {
  document.getElementById("resident-id-inp").value = id + ": " + name;
  hideResidents();
}

function filteredSearchDisplayAlter(
  inputId,
  containerId,
  listItemTagName,
  textGetter
) {
  const filter = document.getElementById(inputId).value;
  const items = document
    .getElementById(containerId)
    .getElementsByTagName(listItemTagName);
  Object.values(items).forEach((item, i) => {
    const text = textGetter(item);
    if (filterSatisfied(filter, text)) {
      item.style.display = "";
    } else {
      item.style.display = "none";
    }
  });
}

function filterResidents() {
  filteredSearchDisplayAlter(
    "resident-name-inp",
    "dropdown-residents",
    "button",
    (elem) => elem.textContent
  );
}

function filterListOfresidents() {
  filteredSearchDisplayAlter(
    "resident-list-name-inp",
    "list-of-residents",
    "li",
    (elem) => elem.textContent
  );
}
