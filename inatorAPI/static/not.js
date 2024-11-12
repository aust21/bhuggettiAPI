document.addEventListener("DOMContentLoaded", function () {
  const emailSearch = document.getElementById("emailSearch");
  const inputGroup = document.querySelector("#group");
  const btn = document.querySelector("#btn");
  const emailDropdown = document.getElementById("emailDropdown");
  const selectedEmails = document.getElementById("selectedEmails");
  const selectedEmailsInput = document.getElementById("selectedEmailsInput");
  const checkboxes = document.querySelectorAll(".email-checkbox");
  let selectedEmailsArray = [];

  // Show dropdown when clicking on the container
  document
    .querySelector(".selected-emails-container")
    .addEventListener("click", function () {
      emailDropdown.style.display = "block";
      btn.style.display = "none";
      inputGroup.classList.add("hidden");
    });

  // Hide dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".email-selector-container")) {
      btn.style.display = "block";
      emailDropdown.style.display = "none";
      inputGroup.classList.remove("hidden");
    }
  });

  // Search functionality
  emailSearch.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    const options = document.querySelectorAll(".email-option");

    options.forEach((option) => {
      const email = option.querySelector("span").textContent.toLowerCase();
      if (email.includes(searchTerm)) {
        option.style.display = "block";
      } else {
        option.style.display = "none";
      }
    });
  });

  // Handle checkbox changes
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const email = this.value;

      if (this.checked) {
        if (!selectedEmailsArray.includes(email)) {
          selectedEmailsArray.push(email);
          addEmailTag(email);
        }
      } else {
        selectedEmailsArray = selectedEmailsArray.filter((e) => e !== email);
        removeEmailTag(email);
      }

      updateSelectedEmailsInput();
    });
  });

  function addEmailTag(email) {
    const tag = document.createElement("div");
    tag.className = "email-tag";
    tag.innerHTML = `
        ${email}
        <span class="remove-email" data-email="${email}">&times;</span>
    `;
    selectedEmails.appendChild(tag);

    // Add click handler for remove button
    tag.querySelector(".remove-email").addEventListener("click", function (e) {
      e.stopPropagation();
      const emailToRemove = this.dataset.email;
      const checkbox = document.querySelector(
        `input[value="${emailToRemove}"]`
      );
      if (checkbox) checkbox.checked = false;
      selectedEmailsArray = selectedEmailsArray.filter(
        (e) => e !== emailToRemove
      );
      removeEmailTag(emailToRemove);
      updateSelectedEmailsInput();
    });
  }

  function removeEmailTag(email) {
    const tag = selectedEmails.querySelector(
      `[data-email="${email}"]`
    ).parentNode;
    if (tag) tag.remove();
  }

  function updateSelectedEmailsInput() {
    selectedEmailsInput.value = JSON.stringify(selectedEmailsArray);
  }
});
