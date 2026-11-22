
import { useEffect, useState } from "react";
import { getDisagreements } from "./services/api";
import "./App.css";

import {
  Database,
  AlertCircle,
  Copy,
  CircleHelp,
  FileWarning,
  Scale,
  Activity,
} from "lucide-react";

function App() {
  const [disagreements, setDisagreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reason, setReason] = useState("all");
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch disagreement data from Django API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getDisagreements();
        setDisagreements(data.results);
      } catch (err) {
        setError("Unable to load reconciliation data.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter and sort records
  const filteredData = disagreements
    .filter(
      (item) => reason === "all" || item.reason === reason
    )
    .sort((a, b) => {
      const first = Number(a.system_a_value ?? 0);
      const second = Number(b.system_a_value ?? 0);

      return sortOrder === "asc"
        ? first - second
        : second - first;
    });

  // Count disagreements by reason
  const reasonCounts = disagreements.reduce((counts, item) => {
    counts[item.reason] = (counts[item.reason] || 0) + 1;
    return counts;
  }, {});

  // Format disagreement reason
  const formatReason = (value) =>
    value.replaceAll("_", " ");

  // Format currency in Indian Rupees
  const formatValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "—";
    }

    return `₹${Number(value).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  // Loading and error messages
  if (loading) return <h2>Loading dashboard...</h2>;
  if (error) return <h2>{error}</h2>;

  return (
    <main className="dashboard">

      {/* Navbar */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon">
            <Scale size={48} />
          </div>

          <div className="brand-text">
            <h1>DealerOS Reconciliation</h1>
            <p>
              Compare records between System A and System B
            </p>
          </div>
        </div>

        <div className="sync-status">
          <Activity size={19} />
          <span>Data Sync Dashboard</span>
        </div>
      </header>

      {/* Summary Cards */}
      <section className="summary">

        <div className="summary-card total-card">
          <div className="card-icon blue-icon">
            <Database size={30} />
          </div>

          <div>
            <h3>Total Disagreements</h3>
            <strong>{disagreements.length}</strong>
          </div>
        </div>

        {Object.entries(reasonCounts).map(([key, count]) => {
          const icons = {
            value_mismatch: {
              icon: AlertCircle,
              className: "red-icon",
            },
            duplicate_in_b: {
              icon: Copy,
              className: "orange-icon",
            },
            missing_in_b: {
              icon: CircleHelp,
              className: "green-icon",
            },
            orphan_in_b: {
              icon: FileWarning,
              className: "purple-icon",
            },
          };

          const Icon = icons[key]?.icon;
          const iconClass = icons[key]?.className;

          return (
            <div className="summary-card" key={key}>
              {Icon && (
                <div className={`card-icon ${iconClass}`}>
                  <Icon size={30} />
                </div>
              )}

              <div>
                <h3>{formatReason(key)}</h3>
                <strong>{count}</strong>
              </div>
            </div>
          );
        })}

      </section>

      {/* Disagreement Table */}
      <section className="table-section">

        <div className="table-header">
          <h2>Disagreement Records</h2>

          {/* Filters and Sorting */}
          <div className="filters">
            <select
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            >
              <option value="all">All reasons</option>
              <option value="missing_in_b">Missing in B</option>
              <option value="orphan_in_b">Orphan in B</option>
              <option value="duplicate_in_b">Duplicate in B</option>
              <option value="value_mismatch">Value mismatch</option>
            </select>

            <select
              value={sortOrder}
              onChange={(event) => setSortOrder(event.target.value)}
            >
              <option value="asc">Value: Low to High</option>
              <option value="desc">Value: High to Low</option>
            </select>
          </div>
        </div>

        {/* Records */}
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Reason</th>
                <th>Organization</th>
                <th>System A Value</th>
                <th>System B Value</th>
                <th>Location</th>
                <th>Entry ID</th>
              </tr>
            </thead>

            <tbody>
              {filteredData.map((item, index) => (
                <tr
                  key={`${item.entry_id || item.record_id}-${item.reason}-${index}`}
                >
                  <td>{item.record_id}</td>

                  <td>
                    <span className={`reason reason-${item.reason}`}>
                      {formatReason(item.reason)}
                    </span>
                  </td>

                  <td>{item.organization}</td>

                  <td className="amount">
                    {formatValue(item.system_a_value)}
                  </td>

                  <td className="amount">
                    {formatValue(item.system_b_value)}
                  </td>

                  <td>{item.location}</td>

                  <td>{item.entry_id ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredData.length === 0 && (
            <p className="empty">
              No disagreements found.
            </p>
          )}
        </div>

        <div className="table-footer">
          Showing {filteredData.length} of {disagreements.length} records
        </div>

      </section>
    </main>
  );
}

export default App;
