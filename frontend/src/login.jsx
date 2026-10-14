import { useState } from "react";

function Login({ onLogin, onSwitch }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    console.log("LOGIN BUTTON CLICKED");
    console.log("Email:", email);

    setMessage("Logging in...");

    try {
      const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password: password,
        }),
      });

      console.log("STATUS:", response.status);

      const data = await response.json();

      console.log("BACKEND RESPONSE:", data);

      if (response.ok && data.success) {
        setMessage("Login successful!");

        onLogin(data.user);
      } else {
        setMessage(data.error || "Login failed");
      }
    } catch (error) {
      console.error("LOGIN ERROR:", error);
      setMessage("Unable to connect to server");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">

        <h1>Welcome Back</h1>

        <p>
          Login to your AI Resume Analyzer
        </p>

        <form onSubmit={handleLogin}>

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">
            Login
          </button>

        </form>

        {message && (
          <p className="auth-message">
            {message}
          </p>
        )}

        <p className="switch-auth">
          Don't have an account?

          <button
            type="button"
            onClick={onSwitch}
          >
            Sign Up
          </button>
        </p>

      </div>
    </div>
  );
}

export default Login;