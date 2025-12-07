import React, { useState } from "react";
import { postJSON, putJSON, deleteJSON } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

const LOCATIONS = ["Courtroom A", "Courtroom B", "Courtroom C"];

export default function CourtDateEditor({ courtDate, onSaved, onDeleted }) {
  const { token, user } = useAuth(); // <--- added `user`
  const [form, setForm] = useState({
    Date: courtDate?.Date || "",
    Time: courtDate?.Time || "",
    Location: courtDate?.Location || LOCATIONS[0],
    CaseID: courtDate?.CaseID || "",
  });
  const [err, setErr] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!form.Date || !form.Time || !form.Location || !form.CaseID) {
      setErr("All fields are required.");
      return;
    }

    try {
      if (courtDate?.CourtDateID) {
        await putJSON(
          `/courtdate/update/${courtDate.CourtDateID}`,
          {
            date: form.Date,
            time: form.Time,
            location: form.Location,
            case_id: form.CaseID,
          },
          token
        );
      } else {
        await postJSON(
          "/courtdate/add",
          {
            date: form.Date,
            time: form.Time,
            location: form.Location,
            case_id: form.CaseID,
          },
          token
        );
      }

      onSaved();
    } catch (e) {
      console.error(e);
      setErr("Failed to save court date.");
    }
  };

  const handleDelete = async () => {
    if (!courtDate?.CourtDateID) return;

    try {
      await deleteJSON(`/courtdate/delete/${courtDate.CourtDateID}`, token);
      onDeleted();
    } catch (e) {
      console.error(e);
      setErr("Failed to delete court date.");
    }
  };

  // Only Judge/Admin can see Delete button
  const canDelete = user?.role === "Judge" || user?.role === "Admin";

  return (
    <div style={{ marginBottom: 20, borderBottom: "1px solid #ccc", paddingBottom: 10 }}>
      {err && <div style={{ color: "red" }}>{err}</div>}

      <input type="date" name="Date" value={form.Date} onChange={handleChange} />
      <input type="time" name="Time" value={form.Time} onChange={handleChange} />
      
      <select name="Location" value={form.Location} onChange={handleChange}>
        {LOCATIONS.map((loc) => (
          <option key={loc} value={loc}>{loc}</option>
        ))}
      </select>

      <input
        type="number"
        name="CaseID"
        placeholder="Case ID"
        value={form.CaseID}
        onChange={handleChange}
      />

      <button onClick={handleSave}>
        {courtDate ? "Update" : "Add"}
      </button>

      {courtDate && canDelete && (
        <button onClick={handleDelete} style={{ marginLeft: 10 }}>
          Delete
        </button>
      )}
    </div>
  );
}
