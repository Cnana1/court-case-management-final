import React, { useEffect, useState } from "react";
import { getJSON, deleteJSON } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import CaseEditor from "./CaseEditor";

export default function Cases({ showOnlyMine = false }) {
  const { token, user } = useAuth();
  const [cases, setCases] = useState([]);
  const [attendees, setAttendees] = useState([]);
  const [err, setErr] = useState("");
  const [showEditor, setShowEditor] = useState(false);
  const [editingCase, setEditingCase] = useState(null);

  const canEditCases = ["Judge", "Admin", "Clerk"].includes(user.role);
  const canDeleteCases = ["Judge", "Admin"].includes(user.role);
  const canAddCases = ["Judge", "Clerk", "Admin"].includes(user.role);

  const loadCases = async () => {
    try {
      const path = showOnlyMine ? "/cases/mine" : "/cases";
      const data = await getJSON(path, token);
      setCases(data);

      const att = await getJSON("/users/attendees", token);
      setAttendees(att);
    } catch (e) {
      console.error(e);
      setErr("Failed to load cases or attendees.");
    }
  };

  useEffect(() => {
    loadCases();
  }, [token, showOnlyMine]);

  const handleAdd = () => {
    setEditingCase(null);
    setShowEditor(true);
  };

  const handleEdit = (c) => {
    setEditingCase(c);
    setShowEditor(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this case?")) return;
    try {
      await deleteJSON(`/cases/delete/${id}`, token);
      setCases((prev) => prev.filter((c) => c.CaseID !== id));
      if (editingCase && editingCase.CaseID === id) setShowEditor(false);
    } catch (e) {
      alert("Failed to delete case.");
    }
  };

  // AUTO REFRESH AFTER EDIT/SAVE
  const handleSubmit = () => {
    setShowEditor(false);
    setEditingCase(null);
    loadCases();
  };

  if (err) return <div style={{ color: "red" }}>{err}</div>;

  return (
    <div>
      <h3>{showOnlyMine ? "My Cases" : "Cases"}</h3>

      {canAddCases && <button onClick={handleAdd}>Add Case</button>}

      {showEditor && (
        <CaseEditor
          token={token}
          caseItem={editingCase}
          onSaved={handleSubmit}
          onDeleted={(deletedCaseID) => {
            setCases((prev) =>
              prev.filter((c) => c.CaseID !== deletedCaseID)
            );
            setShowEditor(false);
            setEditingCase(null);
            loadCases();
          }}
          userRole={user.role}
        />
      )}

      {/* REMOVED COURT DATES HERE — fixes duplicate UI */}

      <table border="1" cellPadding="6" style={{ marginTop: "10px", width: "100%" }}>
        <thead>
          <tr>
            <th>CaseID</th>
            <th>Description</th>
            <th>Status</th>
            <th>Assigned To</th>
            <th>Court Dates</th>
            {canEditCases && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {cases.map((c) => (
            <tr key={c.CaseID}>
              <td>{c.CaseID}</td>
              <td>{c.Description}</td>
              <td>{c.Status}</td>
              <td>
                {c.Attendees?.length
                  ? c.Attendees.map((a) => a.Name).join(", ")
                  : "-"}
              </td>
              <td>
                {c.CourtDates?.length ? (
                  <ul style={{ margin: 0, paddingLeft: 16 }}>
                    {c.CourtDates.map((cd) => (
                      <li key={cd.CourtDateID || cd.id}>
                        {cd.Date} @ {cd.Time} ({cd.Location})
                      </li>
                    ))}
                  </ul>
                ) : "-"}
              </td>

              {canEditCases && (
                <td>
                  <button onClick={() => handleEdit(c)}>Update</button>
                  {canDeleteCases && (
                    <button
                      onClick={() => handleDelete(c.CaseID)}
                      style={{ marginLeft: 5 }}
                    >
                      Delete
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
