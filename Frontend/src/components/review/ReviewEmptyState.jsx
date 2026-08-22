import React from "react";

export default function ReviewEmptyState() {
  return (
    <div className="review-empty-state">
      <h3>No reviews available</h3>

      <p>
        Classification results requiring review
        will appear here.
      </p>
    </div>
  );
}