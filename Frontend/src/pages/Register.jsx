import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function LogIn() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    setError("");

    // Symulacja logowania front-end
    if (email && password) {
      console.log("Logging completed:", email);
      navigate("/"); // powrót do strony głównej / tłumacza
    } else {
      setError("Fill in all fields.");
    }
  };

  const handleGoogleLogin = () => {
    console.log("Pressed Google login button");
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Register</h2>

        <form onSubmit={handleLogin} className="auth-form">
          <div className="form-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="twoj@email.com"
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">Repeat Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="btn btn-primary full-width">
            Register
          </button>
        </form>

        <div className="auth-separator">
          <span>or</span>
        </div>

        <button
          type="button"
          onClick={handleGoogleLogin}
          className="btn btn-secondary full-width"
        >
          Continue with Google
        </button>
      </div>
    </div>
  );
}