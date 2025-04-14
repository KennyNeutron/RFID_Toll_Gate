function fetchLatestTransaction() {
  fetch('/latest_transaction')
    .then(res => res.json())
    .then(data => {
      if (data.status === "no_logs") {
        document.getElementById("latest-transaction").innerHTML =
          "<p>No transactions yet.</p>";
      } else if (data.status === "error") {
        document.getElementById("latest-transaction").innerHTML =
          "<p>Error fetching latest transaction.</p>";
      } else {
        document.getElementById("name").textContent = data.name;
        document.getElementById("course").textContent = data.course;
        document.getElementById("year_level").textContent = data.year_level;
        document.getElementById("vehicle_type").textContent = data.vehicle_type;
        document.getElementById("plate_number").textContent = data.plate_number;
        document.getElementById("entry_type").textContent = data.entry_type;
        document.getElementById("timestamp").textContent = data.timestamp;
      }
    })
    .catch(err => {
      console.error("Fetch error:", err);
      document.getElementById("latest-transaction").innerHTML =
        "<p>Error loading data.</p>";
    });
}

// Refresh every second
setInterval(fetchLatestTransaction, 1000);
fetchLatestTransaction(); // initial call

function fetchCounts() {
  fetch('/current_counts')
    .then(res => res.json())
    .then(data => {
      document.getElementById("motorcycle-count").textContent = data.motorcycles;
      document.getElementById("car-count").textContent = data.cars;
    })
    .catch(err => {
      console.error("Count fetch error:", err);
      document.getElementById("motorcycle-count").textContent = "Error";
      document.getElementById("car-count").textContent = "Error";
    });
}

setInterval(fetchCounts, 1000);
fetchCounts(); // Initial fetch

