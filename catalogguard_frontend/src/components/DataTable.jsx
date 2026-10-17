import React from "react";
import { ChevronRight } from "lucide-react";
import StatusBadge from "./StatusBadge";

export default function DataTable({ columns = [], rows = [], onRowClick, emptyMessage = "Nothing to show yet.", className = "" }) {
  return <div className={`table-wrap ${className}`}><table className="data-table"><thead><tr>{columns.map((col) => <th key={col.key}>{col.label}</th>)}{onRowClick && <th />}</tr></thead>
    <tbody>{rows.length ? rows.map((row, index) => <tr key={row.id || index} onClick={() => onRowClick?.(row)} className={onRowClick ? "clickable-row" : ""}>
      {columns.map((col) => <td key={col.key}>{col.render ? col.render(row[col.key], row) : col.key === "status" ? <StatusBadge status={row[col.key]} /> : row[col.key] ?? "—"}</td>)}
      {onRowClick && <td className="row-chevron"><ChevronRight size={16} /></td>}
    </tr>) : <tr><td colSpan={columns.length + (onRowClick ? 1 : 0)} className="empty-cell">{emptyMessage}</td></tr>}</tbody>
  </table></div>;
}
