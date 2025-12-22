// Helper function to get CSRF token from cookie
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

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const errBox = document.getElementById("loginError");
    errBox.classList.add("d-none");
    errBox.innerText = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
      errBox.classList.remove("d-none");
      errBox.innerText = "Email and password are required.";
      return;
    }

    try {
      // Get CSRF token from cookie or meta tag
      let csrftoken = getCookie('csrftoken');
      if (!csrftoken) {
        // Try to get from meta tag as fallback
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
          csrftoken = metaTag.getAttribute('content');
        }
      }
      
      // Login endpoint - include credentials to set session cookie
      const headers = {
        "Content-Type": "application/json",
      };
      
      // Add CSRF token if available
      if (csrftoken) {
        headers["X-CSRFToken"] = csrftoken;
      }
      
      const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: headers,
        credentials: "include", // Important: include cookies for session authentication
        body: JSON.stringify({
          email: email,
          password: password
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || "Login failed");
      }

      // Store token for API requests
      if (data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("role", data.role);
        
        // Redirect based on user role
        const role = data.role || "burner";
        let redirectUrl = "/dashboard/";
        
        if (role === "admin") {
          redirectUrl = "/admin/dashboard/";
        } else if (role === "leader") {
          redirectUrl = "/leader/dashboard/";
        } else if (role === "burner") {
          redirectUrl = "/burner/dashboard/";
        }
        
        window.location.href = redirectUrl;
      } else {
        throw new Error("No token received from server");
      }
    } catch (err) {
      errBox.classList.remove("d-none");
      errBox.innerText = err.message || "Login failed. Please check your credentials.";
      console.error("Login error:", err);
    }
  });
});
