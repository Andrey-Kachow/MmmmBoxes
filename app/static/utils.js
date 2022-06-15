function filterSatisfied(filterQuery, text) {
  return text.toLowerCase().indexOf(filterQuery.toLowerCase()) > -1
}
