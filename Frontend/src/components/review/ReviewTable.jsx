import React from "react";
import {
  getAction,
  getActionClass,
  getActionLabel,
  getCreatedAt,
  getNewCategory,
  getOldCategory,
  getProductId,
} from "../../utils/review.utils";

export default function ReviewTable({
  reviews,
  loading,
  onSelect,
}) {
  if (loading) {
    return (
      <div className="review-table-state">
        Loading review records...
      </div>
    );
  }

  if (!reviews.length) {
    return (
      <div className="review-table-state">
        No review records found.
      </div>
    );
  }

  return (
    <div className="review-table-wrapper">
      <table className="review-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Product</th>
            <th>Old Category</th>
            <th>New Category</th>
            <th>Action</th>
            <th>Comment</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          {reviews.map((review) => {
            const action = getAction(review);

            return (
              <tr key={review.id}>
                <td>#{review.id}</td>

                <td>
                  {typeof getProductId(review) === "object"
                    ? getProductId(review)?.id
                    : getProductId(review)}
                </td>

                <td>{getOldCategory(review)}</td>

                <td>{getNewCategory(review)}</td>

                <td>
                  <span className={getActionClass(action)}>
                    {getActionLabel(action)}
                  </span>
                </td>

                <td className="review-comment-cell">
                  {review.comment || "—"}
                </td>

                <td>{getCreatedAt(review)}</td>

                <td>
                  <button
                    type="button"
                    className="review-view-button"
                    onClick={() => onSelect(review)}
                  >
                    Review
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}