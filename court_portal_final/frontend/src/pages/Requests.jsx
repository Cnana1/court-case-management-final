import React, { useEffect, useState } from "react";
import { getJSON, putJSON, deleteJSON } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

export default function Requests() {
  const { token } = useAuth();
  const [reqs, setReqs] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    load();
  }, [token]);

  async function load() {
    try {
      const data = await getJSON("/reschedule/all", token);
      if (!Array.isArray(data)) throw new Error("Invalid response");
      setReqs(data);
    } catch (e) {
      console.error(e);
      setErr("Failed to load requests. Make sure you're logged in.");
      setReqs([]);
    }
  }

  async function handleApprove(id) {
    try {
      await putJSON(`/reschedule/approve/${id}`, {}, token);
      load();
    } catch (e) {
      console.error(e);
      setErr("Failed to approve request.");
    }
  }

  async function handleDeny(id) {
    try {
      await putJSON(`/reschedule/deny/${id}`, {}, token);
      load();
    } catch (e) {
      console.error(e);
      setErr("Failed to deny request.");
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Are you sure you want to delete this request?")) return;
    try {
      await deleteJSON(`/reschedule/delete/${id}`, token);
      load(); // reload table after deletion
    } catch (e) {
      console.error(e);
      setErr("Failed to delete request.");
    }
  }

  if (err) return <div style={{ color: "red" }}>{err}</div>;

  return (
    <div>
      <h3>Reschedule Requests</h3>
      {reqs.length === 0 && <div>No requests found.</div>}
      {reqs.length > 0 && (
        <table border="1" cellPadding="6">
          <thead>
            <tr>
              <th>DateID</th>
              <th>CaseID</th>
              <th>New Date</th>
              <th>Attendee File</th> {/* <-- new column */}
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reqs.map(r => (
              <tr key={r.RequestID}>
                <td>{r.RequestID}</td>
                <td>{r.CaseID}</td>
                <td>{r.NewDate}</td>
                <td>
                  {r.FileAttachment ? (
                    <a
                      href={`http://127.0.0.1:5000/uploads/reschedule_files/${r.FileAttachment}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {r.FileAttachment}
                    </a>
                  ) : "-"}
                </td>
                <td>{r.Status}</td>
                <td>
                  <button onClick={() => handleApprove(r.RequestID)}>Approve</button>
                  <button onClick={() => handleDeny(r.RequestID)}>Deny</button>
                  <button onClick={() => handleDelete(r.RequestID)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
