import React, { useState } from "react";
import ReviewActionModal from "./ReviewActionModal";

export default function ReviewDetail({
  review,
  categories,
  loading,
  onApprove,
  onEdit,
  onReject,
  onClose,
}) {
  const [mode, setMode] = useState(null);

  if (!review) {
    return null;
  }

  const closeModal = () => {
    if (!loading) {
      setMode(null);
    }
  };

  const handleApprove = async (payload) => {
    await onApprove(review.id, payload);
    setMode(null);
  };

  const handleEdit = async (payload) => {
    await onEdit(review.id, payload);
    setMode(null);
  };

  const handleReject = async (payload) => {
    await onReject(review.id, payload);
    setMode(null);
  };

  return (
    <>
      <div className="review-detail-panel">
        <div className="review-detail-header">
          <div>
            <h2>Review #{review.id}</h2>

            <p>
              Product ID:{" "}
              {review.product?.id ??
                review.product_id ??
                review.product ??
                "-"}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="review-close-button"
          >
            Close
          </button>
        </div>

        <div className="review-info-grid">
          <div className="review-info-card">
            <span>Old Category</span>
            <strong>
              {review.old_category_id ?? "—"}
            </strong>
          </div>

          <div className="review-info-card">
            <span>New Category</span>
            <strong>
              {review.new_category_id ?? "—"}
            </strong>
          </div>

          <div className="review-info-card">
            <span>Action</span>
            <strong>
              {review.action || "PENDING"}
            </strong>
          </div>

          <div className="review-info-card">
            <span>Created At</span>
            <strong>
              {review.created_at
                ? new Date(
                  review.created_at
                ).toLocaleString()
                : "—"}
            </strong>
          </div>
        </div>

        <div className="review-comment">
          <h3>Reviewer Comment</h3>

          <p>
            {review.comment || "No comment added."}
          </p>
        </div>

        {review.product_info?.images?.length > 0 && (
          <div className="review-comment" style={{ marginTop: "1rem" }}>
            <h3>Product Images</h3>
            <div style={{ display: "flex", gap: "1rem", overflowX: "auto", marginTop: "0.5rem" }}>
              {review.product_info.images.map((img, i) => (
                <img
                  key={i}
                  src={img.url}
                  alt={review.product_info.title || "Product"}
                  style={{ height: "120px", width: "120px", objectFit: "contain", borderRadius: "8px", border: "1px solid #ccc", backgroundColor: "#f9fafb" }}
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              ))}
            </div>
          </div>
        )}

        <div className="review-action-buttons">
          <button
            type="button"
            className="review-approve-button"
            onClick={() => setMode("approve")}
          >
            Approve
          </button>

          <button
            type="button"
            className="review-edit-button"
            onClick={() => setMode("edit")}
          >
            Edit Category
          </button>

          <button
            type="button"
            className="review-reject-button"
            onClick={() => setMode("reject")}
          >
            Reject
          </button>
        </div>
      </div>

      <ReviewActionModal
        review={review}
        mode={mode}
        categories={categories}
        loading={loading}
        onClose={closeModal}
        onApprove={handleApprove}
        onEdit={handleEdit}
        onReject={handleReject}
      />
    </>
  );
}