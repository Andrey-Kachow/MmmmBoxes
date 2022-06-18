function showResidents() {
  document.getElementById("dropdown-residents").style.display = "block";
}

function hideResidents() {
  document.getElementById("dropdown-residents").style.display = "none";
}

function nonButtonFocusHide() {
  if (relatedTarget != null) {
    if (relatedTarget.tagName == "BUTTON") {
      return;
    }
  }
  hideResidents();
}

function selectResidentName(name) {
  document.getElementById("resident-name-inp").value = name;
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
