import React from "react";
import { useAuth } from "../contexts/AuthContext";

export default function RoleGate({ allowed = [], children }) {
  const { user } = useAuth();

  if (!user || !user.role) return null;

  if (allowed.includes(user.role)) return <>{children}</>;

  return null;
}
