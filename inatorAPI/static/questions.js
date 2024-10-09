document
  .getElementById("questionForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const question = document.getElementById("question").value;
    const category = document.getElementById("category").value;

    fetch("/api/questions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question, category }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          alert("Question posted successfully!");
        }
      })
      .catch((error) => console.error("Error:", error));
  });
