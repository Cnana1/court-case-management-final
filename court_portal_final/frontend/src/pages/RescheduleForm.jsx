import React, { useState } from "react";
import { postFormData } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

export default function RescheduleForm() {
  const { token } = useAuth();
  const [caseId, setCaseId] = useState("");
  const [newDate, setNewDate] = useState("");
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  async function submit(e) {
    e.preventDefault();
    if (!caseId || !newDate) {
      setMsg("CaseID and NewDate are required");
      return;
    }

    const fd = new FormData();
    fd.append("CaseID", caseId);
    fd.append("NewDate", newDate);
    if (file) fd.append("file", file);

    try {
      const res = await postFormData("/reschedule/add", fd, token);
      setMsg(res.message || "Submitted successfully");
      setCaseId("");
      setNewDate("");
      setFile(null);
    } catch (err) {
      console.error(err);
      setMsg("Failed to submit request");
    }
  }

  return (
    <form onSubmit={submit}>
      <div>
        <input
          placeholder="CaseID"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
        />
      </div>
      <div>
        <input
          type="date"
          value={newDate}
          onChange={(e) => setNewDate(e.target.value)}
        />
      </div>
      <div>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      </div>
      <button type="submit">Submit Reschedule Request</button>
      {msg && <div>{msg}</div>}
    </form>
  );
}
