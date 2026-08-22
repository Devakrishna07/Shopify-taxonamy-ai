import React from "react";

export default function ReviewFilters({
  search,
  action,
  onSearchChange,
  onActionChange,
  onRefresh,
}) {
  return (
    <div className="review-filters">
      <div className="review-search">
        <label htmlFor="review-search">Search</label>

        <input
          id="review-search"
          type="text"
          placeholder="Search reviews..."
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
        />
      </div>

      <div className="review-filter">
        <label htmlFor="review-action">Action</label>

        <select
          id="review-action"
          value={action}
          onChange={(event) => onActionChange(event.target.value)}
        >
          <option value="">All</option>
          <option value="APPROVE">Approved</option>
          <option value="EDIT">Edited</option>
          <option value="REJECT">Rejected</option>
        </select>
      </div>

      <button
        type="button"
        className="review-refresh-button"
        onClick={onRefresh}
      >
        Refresh
      </button>
    </div>
  );
}