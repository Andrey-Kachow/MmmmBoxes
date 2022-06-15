function showResidents() {
  document.getElementById("dropdown_residents").style.display = 'block'
}

function hideResidents() {
  document.getElementById("dropdown_residents").style.display = 'none'
}

function nonButtonFocusHide() {
  if (event.relatedTarget != null){
    if (event.relatedTarget.tagName == 'BUTTON'){
      return
    }
  }
  hideResidents()
}

function selectResidentName(name) {
  document.getElementById("resident_name_inp").value = name
  hideResidents();
}

function filteredSearchDisplayAlter(inputId, containerId, listItemTagName, obtainTextFromItem) {
  const filter = document.getElementById(inputId).value
  const items = document.getElementById(containerId).getElementsByTagName(listItemTagName)
  Object.values(items).forEach((item, i) => {
    const text = obtainTextFromItem(item)
    if (filterSatisfied(filter, text)) {
      item.style.display = ""
    } else {
      item.style.display = "none"
    }
  });
}

function filterResidents() {
  const input = document.getElementById("resident_name_inp")
  const filter = input.value.toLowerCase()
  const buttons = document.getElementById("dropdown_residents").getElementsByTagName("button")
  Object.values(buttons).forEach((button, i) => {
    const text = button.textContent
    if (filterSatisfied(filter, text)) {
      button.style.display = ""
    } else {
      button.style.display = "none"
    }
  });
}

function filterListOfresidents() {
  const input = document.getElementById("resident_list_name_inp")
  const filter = input.value.toLowerCase()
  const listElems = document.getElementById("list_of_residents").getElementsByTagName("li")
  Object.values(listElems).forEach((li, i) => {
    const text = li.textContent
    if (filterSatisfied(filter, text)) {
      li.style.display = ""
    } else {
      li.style.display = "none"
    }
  });
}
