import React, { useCallback, useEffect, useMemo, useState } from "react";

import {
  approveReview,
  editReview,
  getReview,
  getReviews,
  getTaxonomyCategories,
  rejectReview,
} from "../api/review.api";

import ReviewTable from "../components/review/ReviewTable";
import ReviewDetail from "../components/review/ReviewDetail";

import {
  normalizeListResponse,
} from "../utils/review.utils";

export default function ReviewPage() {
  const [reviews, setReviews] = useState([]);
  const [categories, setCategories] = useState([]);

  const [selectedReview, setSelectedReview] = useState(null);

  const [search, setSearch] = useState("");
  const [action, setAction] = useState("");

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const [error, setError] = useState("");

  // =========================================================
  // LOAD REVIEWS
  // =========================================================

  const loadReviews = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const params = {};

      if (action) {
        params.action = action;
      }

      if (search.trim()) {
        params.search = search.trim();
      }

      const data = await getReviews(params);

      setReviews(normalizeListResponse(data));
    } catch (err) {
      console.error("Review loading error:", err);

      setError(
        err.message || "Unable to load review records."
      );
    } finally {
      setLoading(false);
    }
  }, [action, search]);

  // =========================================================
  // LOAD TAXONOMY CATEGORIES
  // =========================================================

  const loadCategories = useCallback(async () => {
    try {
      const data = await getTaxonomyCategories({
        leaf: true,
      });

      setCategories(normalizeListResponse(data));
    } catch (err) {
      console.error(
        "Taxonomy category loading error:",
        err
      );
    }
  }, []);

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  // =========================================================
  // OPEN REVIEW
  // =========================================================

  const openReview = async (review) => {
    try {
      setError("");

      const data = await getReview(review.id);

      setSelectedReview(data);
    } catch (err) {
      console.error("Review detail error:", err);

      setError(
        err.message ||
          "Unable to load review details."
      );
    }
  };

  // =========================================================
  // APPROVE
  // =========================================================

  const handleApprove = async (id, payload = {}) => {
    try {
      setActionLoading(true);
      setError("");

      await approveReview(id, payload);

      await loadReviews();

      setSelectedReview(null);
    } catch (err) {
      console.error("Approve review error:", err);

      setError(
        err.message ||
          "Unable to approve the review."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // =========================================================
  // EDIT
  // =========================================================

  const handleEdit = async (id, payload) => {
    try {
      setActionLoading(true);
      setError("");

      await editReview(id, payload);

      await loadReviews();

      setSelectedReview(null);
    } catch (err) {
      console.error("Edit review error:", err);

      setError(
        err.message ||
          "Unable to edit the review."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // =========================================================
  // REJECT
  // =========================================================

  const handleReject = async (id, payload = {}) => {
    try {
      setActionLoading(true);
      setError("");

      await rejectReview(id, payload);

      await loadReviews();

      setSelectedReview(null);
    } catch (err) {
      console.error("Reject review error:", err);

      setError(
        err.message ||
          "Unable to reject the review."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // =========================================================
  // STATISTICS
  // =========================================================

  const statistics = useMemo(() => {
    return {
      total: reviews.length,

      approved: reviews.filter(
        (item) =>
          String(item.action).toUpperCase() ===
          "APPROVE"
      ).length,

      edited: reviews.filter(
        (item) =>
          String(item.action).toUpperCase() ===
          "EDIT"
      ).length,

      rejected: reviews.filter(
        (item) =>
          String(item.action).toUpperCase() ===
          "REJECT"
      ).length,
    };
  }, [reviews]);

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="min-h-screen bg-gray-50 p-6">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">
            Review Queue
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Review and approve product taxonomy
            classifications.
          </p>
        </div>

        <button
          type="button"
          onClick={loadReviews}
          disabled={loading}
          className="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <div className="flex items-start justify-between gap-4">
            <span>{error}</span>

            <button
              type="button"
              onClick={() => setError("")}
              className="font-semibold text-red-600 hover:text-red-800"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* =====================================================
          STATISTICS
      ===================================================== */}

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

        {/* Total */}

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Total
          </p>

          <p className="mt-2 text-3xl font-bold text-gray-900">
            {statistics.total}
          </p>
        </div>

        {/* Approved */}

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Approved
          </p>

          <p className="mt-2 text-3xl font-bold text-green-600">
            {statistics.approved}
          </p>
        </div>

        {/* Edited */}

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Edited
          </p>

          <p className="mt-2 text-3xl font-bold text-blue-600">
            {statistics.edited}
          </p>
        </div>

        {/* Rejected */}

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Rejected
          </p>

          <p className="mt-2 text-3xl font-bold text-red-600">
            {statistics.rejected}
          </p>
        </div>
      </div>

      {/* =====================================================
          FILTERS
      ===================================================== */}

      <div className="mb-5 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

          {/* Search */}

          <div className="md:col-span-2">
            <label
              htmlFor="review-search"
              className="mb-1.5 block text-sm font-medium text-gray-700"
            >
              Search
            </label>

            <input
              id="review-search"
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search reviews..."
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          {/* Action */}

          <div>
            <label
              htmlFor="review-action"
              className="mb-1.5 block text-sm font-medium text-gray-700"
            >
              Action
            </label>

            <select
              id="review-action"
              value={action}
              onChange={(event) =>
                setAction(event.target.value)
              }
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">
                All actions
              </option>

              <option value="APPROVE">
                Approved
              </option>

              <option value="EDIT">
                Edited
              </option>

              <option value="REJECT">
                Rejected
              </option>
            </select>
          </div>
        </div>

        {/* Filter actions */}

        <div className="mt-4 flex justify-end">
          <button
            type="button"
            onClick={() => {
              setSearch("");
              setAction("");
            }}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* =====================================================
          TABLE
      ===================================================== */}

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        {loading ? (
          <div className="flex min-h-[300px] items-center justify-center">
            <div className="text-sm text-gray-500">
              Loading review records...
            </div>
          </div>
        ) : reviews.length === 0 ? (
          <div className="flex min-h-[300px] flex-col items-center justify-center px-6 text-center">
            <div className="mb-3 rounded-full bg-gray-100 p-4">
              <svg
                className="h-6 w-6 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a2 2 0 01.414.586L19 7.414V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>

            <h3 className="text-base font-semibold text-gray-900">
              No reviews available
            </h3>

            <p className="mt-1 max-w-md text-sm text-gray-500">
              Classification results requiring
              review will appear here.
            </p>
          </div>
        ) : (
          <ReviewTable
            reviews={reviews}
            loading={loading}
            onSelect={openReview}
          />
        )}
      </div>

      {/* =====================================================
          SELECTED REVIEW
      ===================================================== */}

      {selectedReview && (
        <ReviewDetail
          review={selectedReview}
          categories={categories}
          loading={actionLoading}
          onApprove={handleApprove}
          onEdit={handleEdit}
          onReject={handleReject}
          onClose={() =>
            setSelectedReview(null)
          }
        />
      )}
    </div>
  );
}