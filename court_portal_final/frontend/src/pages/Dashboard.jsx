import React, { useState, useCallback } from "react";
import Cases from "./Cases";
import CourtDates from "./CourtDates";
import Requests from "./Requests";
import RescheduleForm from "./RescheduleForm";
import Stats from "./Stats";
import RoleGate from "../components/RoleGate";
import { useAuth } from "../contexts/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();

  // KEY to force Cases to reload
  const [casesKey, setCasesKey] = useState(0);

  // Function passed down to CourtDates to trigger reload
  const refreshCases = useCallback(() => {
    setCasesKey((k) => k + 1);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      {/* HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h1>Court Portal Dashboard</h1>
        <div>
          <strong>{user?.name || "User"}</strong> ({user?.role})
          <button onClick={logout} style={{ marginLeft: 15, padding: "6px 12px" }}>Logout</button>
        </div>
      </div>

      {/* Attendee */}
      <RoleGate allowed={["Attendee"]}>
        <section>
          <h2>Submit a Reschedule Request</h2>
          <RescheduleForm />
        </section>
        <section>
          <h2>My Cases</h2>
          <Cases key={casesKey} showOnlyMine />
        </section>
      </RoleGate>

      {/* Clerk */}
      <RoleGate allowed={["Clerk"]}>
        <section>
          <h2>Assigned Cases</h2>
          <Cases key={casesKey} showOnlyMine={false} />
        </section>

        <section>
          <h2>Court Dates</h2>
          <CourtDates refreshCases={refreshCases} />
        </section>

        <section>
          <h2>All Reschedule Requests</h2>
          <Requests />
        </section>
      </RoleGate>

      {/* Judge */}
      <RoleGate allowed={["Judge"]}>
        <section>
          <h2>All Cases</h2>
          <Cases key={casesKey} showOnlyMine={false} />
        </section>

        <section>
          <h2>Court Dates</h2>
          <CourtDates refreshCases={refreshCases} />
        </section>

        <section>
          <h2>All Reschedule Requests</h2>
          <Requests />
        </section>

        <section>
          <Stats />
        </section>
      </RoleGate>

      {/* Admin */}
      <RoleGate allowed={["Admin"]}>
        <section>
          <h2>All Cases</h2>
          <Cases key={casesKey} showOnlyMine={false} />
        </section>

        <section>
          <h2>Court Dates</h2>
          <CourtDates refreshCases={refreshCases} />
        </section>

        <section>
          <h2>All Users</h2>
        </section>

        <section>
          <h2>Statistics</h2>
          <Stats />
        </section>
      </RoleGate>
    </div>
  );
}
