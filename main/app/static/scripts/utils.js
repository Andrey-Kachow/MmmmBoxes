function filterSatisfied(filterQuery, text) {
  return text.toLowerCase().indexOf(filterQuery.toLowerCase()) > -1;
}

function removeAllChildNodes(parent) {
  while (parent.firstChild) {
    parent.removeChild(parent.firstChild);
  }
}
