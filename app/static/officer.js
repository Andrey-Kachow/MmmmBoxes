function showResidents() {
  document.getElementById("dropdown_residents").style.display = 'block'
}

function hideResidents() {
  document.getElementById("dropdown_residents").style.display = 'none'
}

function selectResidentName(name) {
  document.getElementById("resident_name_inp").value = name
}

function filterResidents() {
  const input = document.getElementById("resident_name_inp")
  const filter = input.value.toLowerCase()
  const buttons = document.getElementById("dropdown_residents").getElementsByTagName("button")
  Object.values(buttons).forEach((button, i) => {
    const text = button.textContent
    if (text.toLowerCase().indexOf(filter) > -1) {
      button.style.display = ""
    } else {
      button.style.display = "none"
    }
  });
}
