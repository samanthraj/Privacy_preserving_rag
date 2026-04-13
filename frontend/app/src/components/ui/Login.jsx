import React, { useState } from "react";
import { Link } from "react-router-dom";

export const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please fill all fields");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      // 🔥 DEBUG: check response status
      console.log("Status:", res.status);

      const data = await res.json();
      console.log("Response:", data); // 🔥 VERY IMPORTANT

      if (res.ok && data.user_id) {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("username", data.username);

        window.location.href = "/chat";
      } else {
        alert(data.error || "Login failed");
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Server error - check backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="h-screen flex items-center justify-center bg-gray-900">
      <form
        onSubmit={handleLogin}
        className="bg-gray-800 p-6 rounded-lg w-80"
      >
        <h2 className="text-white text-xl mb-4">Login</h2>

        <input
          type="email"
          placeholder="Email"
          className="w-full p-2 mb-3 rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full p-2 mb-3 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          disabled={loading}
          className="bg-blue-600 w-full py-2 rounded disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>

        <p className="text-sm mt-3 text-gray-300">
          Don’t have an account?{" "}
          <Link to="/register" className="text-blue-400">
            Sign up
          </Link>
        </p>
      </form>
    </section>
  );
};