import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";


export default function LogIn() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      console.log("Logging in:", { email, password });
      
      setTimeout(() => {
        setIsSubmitting(false);
        navigate("/");
      }, 1000);
    } catch (err) {
      setIsSubmitting(false);
      setError("Invalid email or password.");
    }
  };

  const handleGoogleLogin = () => {
    console.log("Logging in with Google...");
    // Google login logic, possibly using a library like react-google-login or Firebase Authentication.
  };

  return (
    <div className="auth-page">
      <section className="auth-card">
        <h2 className="auth-title">Logging in to your account</h2>

        <form onSubmit={handleEmailLogin} className="auth-form">
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
              placeholder="twoj@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Passord
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-input"
              placeholder="••••••••"
              required
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Logging in..." : "Log in"}
          </button>
        </form>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <button
          type="button"
          onClick={handleGoogleLogin}
          className="btn btn-google"
        >
          Continue with Google
        </button>

        <p className="auth-footer-text">
          Don't have an account?{" "}
          <Link to="/register" className="auth-link">
            Register
          </Link>
        </p>
      </section>
    </div>
  );
}