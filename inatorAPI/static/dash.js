const select = document.getElementById("field");
let options = Array.from(select.options);

// Remove the "Select" option from sorting
const selectOption = options.shift();

// Sort options alphabetically by their text
options.sort((a, b) => a.text.localeCompare(b.text));

// Add the "Select" option back at the beginning
options.unshift(selectOption);

// Rebuild the select options
select.innerHTML = "";
options.forEach((option) => select.add(option));

function addOptions() {
  const choice = document.getElementById("field").value;
  const newFieldDiv = document.getElementById("newField");

  if (choice == "Other") {
    newFieldDiv.style.display = "block";
  } else {
    newFieldDiv.style.display = "none";
  }
}
