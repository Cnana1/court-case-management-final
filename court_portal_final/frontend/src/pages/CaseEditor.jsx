import React, { useState, useEffect } from "react";
import { postJSON, putJSON, deleteJSON, getJSON } from "../services/api";

const CASE_STATUSES = ["Open", "Closed", "Pending", "Under Review"];

export default function CaseEditor({ token, caseItem, onSaved, onDeleted, userRole }) {
  const [form, setForm] = useState({
    Description: caseItem?.Description || "",
    Status: caseItem?.Status || CASE_STATUSES[0],
    AssignedTo: caseItem?.Attendees?.[0]?.UserID || "",
  });
  const [attendees, setAttendees] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    async function loadAttendees() {
      try {
        const data = await getJSON("/users/attendees", token);
        if (!Array.isArray(data)) throw new Error("Invalid response");
        setAttendees(data);
      } catch (e) {
        console.error(e);
        setErr("Failed to load attendees.");
      }
    }
    loadAttendees();
  }, [token]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!form.Description || !form.Status || !form.AssignedTo) {
      setErr("All fields are required.");
      return;
    }

    try {
      const payload = {
        description: form.Description,      // lowercase key
        status: form.Status,                // lowercase key
        attendees: [parseInt(form.AssignedTo)], // array of user IDs
      };

      let savedCase;
      if (caseItem?.CaseID) {
        savedCase = await putJSON(`/cases/update/${caseItem.CaseID}`, payload, token);
      } else {
        savedCase = await postJSON("/cases/add", payload, token);
      }

      onSaved(savedCase);
    } catch (e) {
      console.error(e);
      setErr("Failed to save case.");
    }
  };

  const handleDelete = async () => {
    if (!caseItem?.CaseID) return;
    try {
      await deleteJSON(`/cases/delete/${caseItem.CaseID}`, token);
      onDeleted(caseItem.CaseID);
    } catch (e) {
      console.error(e);
      setErr("Failed to delete case.");
    }
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: 10, marginBottom: 10 }}>
      {err && <div style={{ color: "red" }}>{err}</div>}

      <input
        type="text"
        name="Description"
        placeholder="Description"
        value={form.Description}
        onChange={handleChange}
      />

      <select name="Status" value={form.Status} onChange={handleChange}>
        {CASE_STATUSES.map(status => (
          <option key={status} value={status}>{status}</option>
        ))}
      </select>

      <select name="AssignedTo" value={form.AssignedTo} onChange={handleChange}>
        <option value="">Select Attendee</option>
        {attendees.map(a => (
          <option key={a.UserID} value={a.UserID}>{a.Name}</option>
        ))}
      </select>

      <div style={{ marginTop: 5 }}>
        <button onClick={handleSave}>{caseItem?.CaseID ? "Update" : "Add"}</button>

        {/* Delete button only for Judges/Admin */}
        {caseItem?.CaseID && (userRole === "Judge" || userRole === "Admin") && (
          <button onClick={handleDelete} style={{ marginLeft: 5 }}>Delete</button>
        )}
      </div>
    </div>
  );
}
