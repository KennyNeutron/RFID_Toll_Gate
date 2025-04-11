function fetchUID() {
    fetch('/uid')
      .then(response => response.json())
      .then(data => {
        console.log("[DATA]", data);  // For debugging
        document.getElementById('rfid').textContent = data.rfid || "Waiting...";
        document.getElementById('transaction').textContent = data.transaction_type || "Waiting...";
      })
      .catch(() => {
        document.getElementById('rfid').textContent = "Error";
        document.getElementById('transaction').textContent = "Error";
      });
  }
  
  setInterval(fetchUID, 1000);
  fetchUID(); // Run on page load
  