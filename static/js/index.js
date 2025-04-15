function reactivateAccount() {
  const userEmail = "{{ user.email }}";

  fetch("/reactivate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: userEmail }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Your account has been reactivated.");
        location.reload();
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
    document.getElementById("public-info-container").classList.add("hidden");
    document.getElementById("early_withdrawal-container").classList.add("hidden");
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
    document.getElementById("public-info-container").classList.add("hidden");
    document.getElementById("early_withdrawal-container").classList.add("hidden");
  });

document
  .getElementById("public-info")
  .addEventListener("click", () => {
    document
      .getElementById("graduate-petition-form-container")
      .classList.add("hidden");
    document
      .getElementById("undergraduate-transfer-form-container")
      .classList.add("hidden");
    document.getElementById("public-info-container").classList.remove("hidden");
    document.getElementById("early_withdrawal-container").classList.add("hidden");
  });

document
  .getElementById("early_withdrawal")
  .addEventListener("click", () => {
    document
      .getElementById("graduate-petition-form-container")
      .classList.add("hidden");
    document
      .getElementById("undergraduate-transfer-form-container")
      .classList.add("hidden");
    document.getElementById("public-info-container").classList.add("hidden");
    document.getElementById("early_withdrawal-container").classList.remove("hidden");
  });

function viewForm(formId, userEmail) {
  event.preventDefault();
  fetch("/show_pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ formId, userEmail }),
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      window.open(url);
    })
    .catch((error) => {
      console.log("Error: ", error);
    });
}

function viewForm(formId, userEmail) {
  event.preventDefault();
  fetch("/show_pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ formId, userEmail }),
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      window.open(url);
    })
    .catch((error) => {
      console.log("Error: ", error);
    });
}
