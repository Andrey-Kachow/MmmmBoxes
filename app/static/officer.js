function showResidents() {
  document.getElementById("dropdown_residents").style.display = "block";
}

function hideResidents() {
  document.getElementById("dropdown_residents").style.display = "none";
}

function nonButtonFocusHide() {
  if (event.relatedTarget != null) {
    if (event.relatedTarget.tagName == "BUTTON") {
      return;
    }
  }
  hideResidents();
}

function selectResidentName(name) {
  document.getElementById("resident_name_inp").value = name;
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
    "resident_name_inp",
    "dropdown_residents",
    "button",
    (elem) => elem.textContent
  );
}

function filterListOfresidents() {
  filteredSearchDisplayAlter(
    "resident_list_name_inp",
    "list_of_residents",
    "li",
    (elem) => elem.textContent
  );
}
