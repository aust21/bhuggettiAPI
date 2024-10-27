const data = {
  labels: ["Culture Fit", "Technical"],
  datasets: [
    {
      label: "Question Types",
      backgroundColor: ["#3e95cd", "#8e5ea2"],
      data: [cultCount, techCount],
    },
  ],
};

new Chart("myChart", {
  type: "pie",
  data: data,
  options: {
    title: {
      display: true,
      text: "Culture Fit vs Technical Questions",
    },
  },
});
