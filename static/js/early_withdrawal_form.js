document.addEventListener("DOMContentLoaded", function () {
    const step1 = document.getElementById("step1_option");
    const drop = document.getElementById("dropCoursesField");
    const step3 = document.getElementById("step3_option");
    const returnDate = document.getElementById("return_date");
  
    step1.addEventListener("change", () => {
      drop.classList.toggle("hidden", step1.value !== "2");
    });
  
    step3.addEventListener("change", () => {
      returnDate.classList.toggle("hidden", step3.value !== "1");
    });
  
    document.getElementById("earlyWithdrawalForm").addEventListener("submit", async function (e) {
      e.preventDefault();
  
      const id = document.getElementById("id").value.trim();
      const step1Val = document.getElementById("step1_option").value;
      const step2Val = document.getElementById("step2_option").value;
      const step3Val = document.getElementById("step3_option").value;
      const departureDate = document.getElementById("departure_date").value;
      const returnDateVal = document.getElementById("return_date").value;
      const ack1 = document.getElementById("ack1").checked;
      const ack2 = document.getElementById("ack2").checked;
      const file = document.getElementById("signature").files[0];
  
      if (!id || !step1Val || !step2Val || !step3Val || !departureDate || !ack1 || !ack2 || !file) {
        return alert("Please complete all required fields.");
      }
  
      if (step1Val === "2") {
        const c1 = document.getElementById("drop_course1").value.trim();
        const c2 = document.getElementById("drop_course2").value.trim();
        const c3 = document.getElementById("drop_course3").value.trim();
        if (!c1 && !c2 && !c3) return alert("Enter at least one course.");
      }
  
      const signatureBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
  
      const fullName = document.getElementById("first_name").value + " " + document.getElementById("last_name").value;
      const email = document.getElementById("email").value;
  
      const tex = `
      \\documentclass{article}
      \\usepackage{geometry}
      \\usepackage{graphicx}
      \\geometry{margin=1in}
      \\begin{document}
      \\title{Authorized Early Withdrawal}
      \\maketitle
      Name: ${fullName} \\\\
      Email: ${email} \\\\
      ID: ${id} \\\\
      Departure: ${departureDate} (${step1Val}), Return: ${step3Val} ${returnDateVal} \\\\
      \\includegraphics[width=7cm]{signature.png}
      \\end{document}
      `;
  
      const response = await fetch("/submit-early-withdrawal-js", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          formName: "early withdrawal form",
          content: tex,
          signature: signatureBase64,
        }),
      });
  
      if (response.ok) {
        alert("Form submitted!");
        window.location.href = "/early-withdrawal-form";
      } else {
        alert("Submission failed.");
      }
    });
  });
  
  function autofillEarlyWithdrawalForm() {
    document.getElementById("id").value = "12345678";
    document.getElementById("step1_option").value = "2";
    document.getElementById("drop_course1").value = "HIST101";
    document.getElementById("departure_date").value = "2025-05-01";
    document.getElementById("step2_option").value = "1";
    document.getElementById("step3_option").value = "1";
    document.getElementById("return_date").value = "2025-09-01";
    document.getElementById("ack1").checked = true;
    document.getElementById("ack2").checked = true;
  
    document.getElementById("step1_option").dispatchEvent(new Event("change"));
    document.getElementById("step3_option").dispatchEvent(new Event("change"));
  }
  
