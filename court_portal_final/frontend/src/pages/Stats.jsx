import React, { useEffect, useState } from "react";
import { getJSON } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

export default function Stats() {
  const { token } = useAuth();
  const [stats, setStats] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getJSON("/admin/stats", token);
        if (!data || Object.keys(data).length === 0) {
          throw new Error("No stats returned");
        }
        setStats(data);
      } catch (e) {
        console.error(e);
        setErr("Failed to load statistics.");
      }
    }
    load();
  }, [token]);

  if (err) return <div style={{ color: "red" }}>{err}</div>;
  if (!stats) return <div>Loading stats...</div>;

  return (
    <div>
      <h3>Statistics</h3>

      {Object.entries(stats).map(([section, value]) => (
        <div key={section} style={{ marginBottom: 25 }}>
          <h4 style={{ textTransform: "capitalize" }}>{section.replace("_", " ")}</h4>

          {/* If the section is an object → render columns */}
          {typeof value === "object" ? (
            <table
              border="1"
              cellPadding="6"
              style={{ marginTop: 8, borderCollapse: "collapse", width: "100%" }}
            >
              <thead>
                <tr>
                  {Object.keys(value).map((col) => (
                    <th key={col} style={{ textTransform: "capitalize" }}>
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  {Object.values(value).map((v, i) => (
                    <td key={i}>{v}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          ) : (
            // For non-object values
            <div>{value}</div>
          )}
        </div>
      ))}
    </div>
  );
}
