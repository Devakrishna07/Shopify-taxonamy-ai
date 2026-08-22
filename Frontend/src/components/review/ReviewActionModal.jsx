import React, { useEffect, useState } from "react";

export default function ReviewActionModal({
  review,
  mode,
  categories,
  loading,
  onClose,
  onApprove,
  onEdit,
  onReject,
}) {
  const [categoryId, setCategoryId] = useState("");
  const [comment, setComment] = useState("");

  useEffect(() => {
    if (!review) {
      return;
    }

    setCategoryId(
      review.new_category_id ??
        review.approved_category_id ??
        review.old_category_id ??
        ""
    );

    setComment(review.comment || "");
  }, [review]);

  if (!review) {
    return null;
  }

  const submit = async (event) => {
    event.preventDefault();

    if (mode === "approve") {
      await onApprove({
        comment,
      });

      return;
    }

    if (mode === "edit") {
      await onEdit({
        new_category_id: categoryId,
        comment,
      });

      return;
    }

    if (mode === "reject") {
      await onReject({
        comment,
      });
    }
  };

  return (
    <div className="review-modal-overlay">
      <div className="review-modal">
        <div className="review-modal-header">
          <div>
            <h2>
              Review #{review.id}
            </h2>

            <p>
              Product:{" "}
              {review.product?.id ??
                review.product_id ??
                review.product ??
                "-"}
            </p>
          </div>

          <button
            type="button"
            className="review-modal-close"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <form onSubmit={submit}>
          <div className="review-detail-grid">
            <div>
              <span>Old Category</span>
              <strong>
                {review.old_category_id ?? "—"}
              </strong>
            </div>

            <div>
              <span>Current Category</span>
              <strong>
                {review.new_category_id ?? "—"}
              </strong>
            </div>

            <div>
              <span>Current Action</span>
              <strong>
                {review.action || "PENDING"}
              </strong>
            </div>

            <div>
              <span>Created</span>
              <strong>
                {review.created_at
                  ? new Date(
                      review.created_at
                    ).toLocaleString()
                  : "—"}
              </strong>
            </div>
          </div>

          {mode === "edit" && (
            <div className="review-form-group">
              <label htmlFor="review-category">
                New Taxonomy Category
              </label>

              <select
                id="review-category"
                value={categoryId}
                onChange={(event) =>
                  setCategoryId(event.target.value)
                }
                required
              >
                <option value="">
                  Select category
                </option>

                {categories.map((category) => (
                  <option
                    key={category.id}
                    value={category.id}
                  >
                    {category.name ||
                      category.title ||
                      category.path ||
                      `Category ${category.id}`}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="review-form-group">
            <label htmlFor="review-comment">
              Comment
            </label>

            <textarea
              id="review-comment"
              rows="4"
              placeholder="Add reviewer comment..."
              value={comment}
              onChange={(event) =>
                setComment(event.target.value)
              }
            />
          </div>

          <div className="review-modal-actions">
            <button
              type="button"
              className="review-secondary-button"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>

            {mode === "approve" && (
              <button
                type="submit"
                className="review-approve-button"
                disabled={loading}
              >
                {loading ? "Approving..." : "Approve"}
              </button>
            )}

            {mode === "edit" && (
              <button
                type="submit"
                className="review-edit-button"
                disabled={loading}
              >
                {loading ? "Saving..." : "Save Changes"}
              </button>
            )}

            {mode === "reject" && (
              <button
                type="submit"
                className="review-reject-button"
                disabled={loading}
              >
                {loading ? "Rejecting..." : "Reject"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}