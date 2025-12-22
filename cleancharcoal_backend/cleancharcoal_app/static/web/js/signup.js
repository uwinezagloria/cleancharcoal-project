document.addEventListener("DOMContentLoaded", () => {
  const panel1 = document.getElementById("step1Panel");
  const donePanel = document.getElementById("donePanel");

  function showSuccess() {
    panel1.classList.add("d-none");
    donePanel.classList.remove("d-none");
  }

  document.getElementById("signupForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const errBox = document.getElementById("signupError");
    errBox.classList.add("d-none");
    errBox.innerText = "";

    // Get form values
    const email = document.getElementById("signupEmail").value.trim();
    const pw = document.getElementById("signupPassword").value;
    const cpw = document.getElementById("confirmPassword").value;
    const phone = document.getElementById("phone").value.trim();
    const fullName = document.getElementById("fullName").value.trim();
    const province = document.getElementById("province").value;
    const district = document.getElementById("district").value.trim();
    const sector = document.getElementById("sector").value.trim();
    const cell = document.getElementById("cell").value.trim();
    const village = document.getElementById("village").value.trim();

    // Validate required fields
    if (!email || !pw || !cpw || !phone || !fullName || !province || !district || !sector) {
      errBox.classList.remove("d-none");
      errBox.innerText = "Please fill in all required fields.";
      return;
    }

    if (pw !== cpw) {
      errBox.classList.remove("d-none");
      errBox.innerText = "Passwords do not match";
      return;
    }

    if (pw.length < 6) {
      errBox.classList.remove("d-none");
      errBox.innerText = "Password must be at least 6 characters long.";
      return;
    }

    // Split name - ensure we have at least first_name
    const nameParts = fullName.split(" ").filter(part => part.length > 0);
    const firstName = nameParts[0] || fullName || "User";
    const lastName = nameParts.slice(1).join(" ") || "";

    try {
      // Helper function to get CSRF token
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }

      // Get CSRF token
      const csrftoken = getCookie('csrftoken') || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      
      // Register user (OTP verification removed)
      const headers = {
        "Content-Type": "application/json"
      };
      
      if (csrftoken) {
        headers['X-CSRFToken'] = csrftoken;
      }
      
      const response = await fetch("/api/register/", {
        method: "POST",
        headers: headers,
        credentials: 'include',
        body: JSON.stringify({
          email: email,
          password: pw,
          confirm_password: cpw,
          phone: phone,
          first_name: firstName,
          last_name: lastName,
          province: province,
          district: district,
          sector: sector,
          cell: cell || "",
          village: village || ""
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle validation errors
        let errorMsg = data.error || data.detail || "Registration failed";
        
        // If there are field-specific errors, show them
        if (data.first_name) errorMsg = `First name: ${data.first_name[0]}`;
        else if (data.last_name) errorMsg = `Last name: ${data.last_name[0]}`;
        else if (data.email) errorMsg = `Email: ${data.email[0]}`;
        else if (data.phone) errorMsg = `Phone: ${data.phone[0]}`;
        else if (data.province) errorMsg = `Province: ${data.province[0]}`;
        else if (data.district) errorMsg = `District: ${data.district[0]}`;
        else if (data.sector) errorMsg = `Sector: ${data.sector[0]}`;
        else if (data.password) errorMsg = `Password: ${data.password[0]}`;
        else if (data.details) errorMsg = `${errorMsg}: ${data.details}`;
        
        throw new Error(errorMsg);
      }

      // Show success panel directly (skip OTP)
      showSuccess();
    } catch (err) {
      errBox.classList.remove("d-none");
      errBox.innerText = err.message || "Registration failed. Please try again.";
      console.error("Registration error:", err);
    }
  });
});
