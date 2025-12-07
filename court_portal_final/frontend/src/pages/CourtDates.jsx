import React, { useEffect, useState } from "react";
import { getJSON } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import CourtDateEditor from "./CourtDateEditor";

export default function CourtDates({ refreshCases }) {
  const { token, user } = useAuth();
  const [courtDates, setCourtDates] = useState([]);
  const [err, setErr] = useState("");

  const loadCourtDates = async () => {
    try {
      const data = await getJSON("/courtdate/all", token);
      setCourtDates(data);
    } catch (e) {
      console.error(e);
      setErr("Failed to load court dates.");
    }
  };

  // Load initial court dates
  useEffect(() => {
    loadCourtDates();
  }, [token]);

  // After saving/deleting, refresh both court dates + cases UI
  const handleAfterSave = async () => {
    await loadCourtDates();
    if (refreshCases) refreshCases();
  };

  const canManage =
    user.role === "Clerk" ||
    user.role === "Judge" ||
    user.role === "Admin";

  if (!canManage) return null;

  return (
    <div>
      <h3>Court Dates</h3>
      {err && <div style={{ color: "red" }}>{err}</div>}

      {/* Add new date */}
      <CourtDateEditor onSaved={handleAfterSave} />

      {/* Existing court dates */}
      {courtDates.map((cd) => (
        <CourtDateEditor
          key={cd.CourtDateID}
          courtDate={cd}
          onSaved={handleAfterSave}
          onDeleted={handleAfterSave}
        />
      ))}
    </div>
  );
}
