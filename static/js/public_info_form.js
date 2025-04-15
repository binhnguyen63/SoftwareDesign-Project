// Signature preview (optional canvas)
document.getElementById("signature").addEventListener("change", function (event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const img = new Image();
      img.onload = function () {
        const canvas = document.createElement("canvas");
        canvas.width = 300;
        canvas.height = 100;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.dataset.signature = e.target.result;
        document.body.appendChild(canvas); // Optional visual preview
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
});

// LaTeX content builder
function generateLaTeX_PublicInfo(studentId, requestType) {
  const fullName = document.getElementById("full_name").value;
  const email = document.getElementById("email").value;

  return `
  \\documentclass{article}
  \\usepackage{geometry}
  \\usepackage{graphicx}
  \\geometry{margin=1in}
  \\begin{document}

  \\title{Request to Withhold or Release Public Information}
  \\maketitle

  \\section*{Student Information}
  Full Name: ${fullName} \\\\
  Email: ${email} \\\\
  SSN or Student ID: ${studentId} \\\\

  \\section*{Request Type}
  ${requestType === "A" ? "I request that my public information NOT be released." : "I am terminating my previous request and allow the release."} \\\\

  \\section*{Signature}
  \\includegraphics[width=7cm]{signature.png}

  \\end{document}
  `;
}

// Form submission
document.getElementById("publicInfoForm").addEventListener("submit", async function (event) {
  event.preventDefault();

  const studentId = document.getElementById("id").value;
  const requestType = document.getElementById("request_type").value;
  const texContent = generateLaTeX_PublicInfo(studentId, requestType);

  const fileInput = document.getElementById("signature");
  const file = fileInput.files[0];

  let signatureBase64 = "";
  if (file) {
    signatureBase64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  try {
    const response = await fetch("/submit-public-info-js", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        formName: "public info form",
        content: texContent,
        signature: signatureBase64,
        id: studentId,
        option: requestType,
      }),
    });

    if (response.ok) {
      alert("Form submitted successfully!");
      window.location.href = "/public-info-form";
    } else {
      alert("Submission failed.");
    }
  } catch (err) {
    console.error("Submission error:", err);
    alert("An error occurred during submission.");
  }
});
