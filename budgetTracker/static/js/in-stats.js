let myChart = null;

const renderChart = (data, labels) => {
  if (myChart !== null) {
    myChart.destroy();
  }
  var ctx = document.getElementById("myChart").getContext("2d");
  var canvasRect = ctx.canvas.getBoundingClientRect();
  const textX = canvasRect.width - 20; // Position X (right side with a margin of 20px)
  const textY = 30; // Position Y (top side with a margin of 20px)
  myChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Income for the month",
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Income per Source'
        }
      },
      animation: {
        onComplete: () => {
          // Show a message if the data is empty
          if (data.length === 0) {
            ctx.font = "16px Arial"; // Set the font size and family
            ctx.fillStyle = "red"; // Set the text color
            ctx.textAlign = "end"; // Align the text to the end of the textX position (right-aligned)
            ctx.textBaseline = "top"; // Align the text to the top of the textY position
            ctx.fillText("No Income for the selected Date", textX, textY);
          }
        }
      }
    }
  });
};

const updateTable = (data) => {
  const tableBody = document.querySelector(".app-table tbody");
  tableBody.innerHTML = "";

  Object.keys(data).forEach((source) => {
    const { amount_earned, budget } = data[source];

    const row = document.createElement("tr");
    const sourceCell = document.createElement("td");
    sourceCell.textContent = source;
    const amountEarnedCell = document.createElement("td");
    amountEarnedCell.textContent = amount_earned;
    const budgetCell = document.createElement("td");
    budgetCell.textContent = budget;

    row.appendChild(sourceCell);
    row.appendChild(amountEarnedCell);
    row.appendChild(budgetCell);

    if (amount_earned < budget) {
      row.classList.add("table-danger");
    } else {
      row.classList.add("table-success");
    }

    tableBody.appendChild(row);
  });
};

const getChartData = (year, month) => {
  console.log("fetching");
  fetch(`/income/income_source_summary/${year}/${month}`)
    .then((res) => res.json())
    .then((results) => {
      console.log("results", results);
      const source_data = results.income_source_data;
      const [labels, data] = [
        Object.keys(source_data),
        Object.values(source_data).map((item) => item.amount_earned),
      ];
      console.log(data);
      renderChart(data, labels);
      updateTable(source_data);

    });
};

document.addEventListener("DOMContentLoaded", () => {
  // Get the current date
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;

  // Get the select elements
  const yearSelect = document.getElementById("yearSelect");
  const monthSelect = document.getElementById("monthSelect");

  // Set the default selected values to the current year and month
  yearSelect.value = currentYear;
  monthSelect.value = currentMonth;

  // Call getChartData with the default selected values
  getChartData(currentYear, currentMonth);

  // Listen for changes in the select elements
  yearSelect.addEventListener("change", () => {
    const selectedYear = yearSelect.value;
    const selectedMonth = monthSelect.value;
    getChartData(selectedYear, selectedMonth);
  });

  monthSelect.addEventListener("change", () => {
    const selectedYear = yearSelect.value;
    const selectedMonth = monthSelect.value;
    getChartData(selectedYear, selectedMonth);
  });
});
document.onload = getChartData();
