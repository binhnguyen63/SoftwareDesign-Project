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

document
  .getElementById("graduate-petition-form")
  .addEventListener("click", () => {
    document
      .getElementById("graduate-petition-form-container")
      .classList.remove("hidden");
    document
      .getElementById("undergraduate-transfer-form-container")
      .classList.add("hidden");
  });

document
  .getElementById("undergraduate-transfer-form")
  .addEventListener("click", () => {
    document
      .getElementById("graduate-petition-form-container")
      .classList.add("hidden");
    document
      .getElementById("undergraduate-transfer-form-container")
      .classList.remove("hidden");
  });
1;
function viewForm(formId, userEmail) {
  event.preventDefault();
  console.log("fetching user pdf: ", userEmail);
  fetch("/show_pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ formId, userEmail }),
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      window.open(url); // Opens the PDF in a new tab
    })
    .catch((error) => {
      console.log("Error: ", error);
    });
}

function viewForm(formId, userEmail) {
  event.preventDefault();
  console.log("fetching user pdf: ", userEmail);
  fetch("/show_pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ formId, userEmail }),
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      window.open(url); // Opens the PDF in a new tab
    })
    .catch((error) => {
      console.log("Error: ", error);
    });
}
