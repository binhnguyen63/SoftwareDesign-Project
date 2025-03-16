function reactivateAccount() {
  // Get the user's email from the page, assuming it's in a hidden input or elsewhere
  const userEmail = "{{ user.email }}"; // You can pass this dynamically from Flask

  // Send a POST request with the email
  fetch("/reactivate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: userEmail }), // Send the email in the request body
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Your account has been reactivated.");
        location.reload(); // Optionally reload the page to update the status
      } else {
        alert("Error reactivating the account.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred.");
    });
}
