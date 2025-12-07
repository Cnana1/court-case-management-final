import React, { useState } from "react";
import { postJSON } from "../services/api";
import { useAuth } from "../contexts/AuthContext";   // <-- FIXED
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();   // <-- FIXED
  const nav = useNavigate();
  const [err, setErr] = useState(null);

  async function submit(e) {
    e.preventDefault();

    const res = await postJSON("/auth/login", { email, password });

    if (res.token) {
      login(res.token, res.user);  // login() comes from useAuth()
      nav("/");
    } else {
      setErr(res.message || "Login failed");
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div>
          <input
            placeholder="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div>
          <input
            placeholder="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button type="submit">Login</button>
      </form>

      {err && <div style={{ color: "red" }}>{err}</div>}
    </div>
  );
}
