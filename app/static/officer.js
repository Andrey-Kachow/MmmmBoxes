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
