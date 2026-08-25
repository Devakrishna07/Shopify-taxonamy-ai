import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  useTaxonomy,
} from "../../hooks/useTaxonomy";


function statusClasses(status) {
  switch (status) {
    case "classified":
      return "bg-green-100 text-green-700";

    case "approved":
      return "bg-blue-100 text-blue-700";

    case "needs_review":
      return "bg-yellow-100 text-yellow-700";

    case "manual_review":
      return "bg-orange-100 text-orange-700";

    case "failed":
      return "bg-red-100 text-red-700";

    case "rejected":
      return "bg-red-100 text-red-700";

    default:
      return "bg-gray-100 text-gray-700";
  }
}


function statusLabel(status) {
  switch (status) {
    case "needs_review":
      return "Needs Review";

    case "manual_review":
      return "Manual Review";

    case "classified":
      return "Classified";

    case "approved":
      return "Approved";

    case "rejected":
      return "Rejected";

    case "failed":
      return "Failed";

    default:
      return "Pending";
  }
}


function confidencePercent(value) {
  const number = Number(value || 0);

  if (number <= 1) {
    return Math.round(number * 100);
  }

  return Math.min(
    Math.round(number),
    100
  );
}


function StatCard({
  title,
  value,
  description,
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      <p className="mt-2 text-3xl font-bold text-gray-900">
        {value ?? 0}
      </p>

      {description && (
        <p className="mt-1 text-xs text-gray-500">
          {description}
        </p>
      )}
    </div>
  );
}


function ConfidenceBar({
  value,
}) {
  const percentage =
    confidencePercent(value);

  return (
    <div className="min-w-[140px]">
      <div className="mb-1 flex justify-between text-xs">
        <span className="font-medium text-gray-700">
          {percentage}%
        </span>

        <span className="text-gray-400">
          confidence
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-gray-900 transition-all"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}


export default function TaxonomyPage() {
  const {
    products,
    productsLoading,
    classificationLoading,
    error,

    stats,

    loadProductTaxonomyList,
    loadStats,

    runBulkClassification,

    approveTaxonomy,
    rejectTaxonomy,
  } = useTaxonomy();


  const [search, setSearch] =
    useState("");

  const [status, setStatus] =
    useState("");

  const [classification, setClassification] =
    useState("");

  const [level, setLevel] =
    useState("");

  const [page, setPage] =
    useState(1);

  const [total, setTotal] =
    useState(0);

  const [message, setMessage] =
    useState("");

  const [actionLoading, setActionLoading] =
    useState(null);

  const [expandedProduct, setExpandedProduct] =
    useState(null);

  const [processingAll, setProcessingAll] =
    useState(false);


  const pageSize = 25;


  const loadProducts =
    useCallback(
      async () => {
        try {
          const response =
            await loadProductTaxonomyList({
              search,
              status,
              classification,
              level,
              page,
              pageSize,
            });

          setTotal(
            Number(
              response?.count || 0
            )
          );

        } catch (err) {
          console.error(
            "Failed to load taxonomy products:",
            err
          );
        }
      },
      [
        loadProductTaxonomyList,
        search,
        status,
        classification,
        level,
        page,
      ]
    );


  useEffect(() => {
    loadProducts();
  }, [
    loadProducts,
  ]);


  useEffect(() => {
    loadStats();
  }, [
    loadStats,
  ]);


  const refresh =
    async () => {
      await Promise.all([
        loadProducts(),
        loadStats(),
      ]);
    };


  const handleClassifyBatch =
    async () => {
      setMessage("");

      try {
        const result =
          await runBulkClassification(
            10
          );

        setMessage(
          `Processed ${result?.processed || 0}. ` +
          `Classified ${result?.classified || 0}. ` +
          `Needs review ${result?.needs_review || 0}. ` +
          `Manual review ${result?.manual_review || 0}. ` +
          `Failed ${result?.failed || 0}. ` +
          `Remaining ${result?.remaining || 0}.`
        );

        await refresh();

      } catch (err) {
        setMessage(
          err?.response?.data?.message ||
          err?.message ||
          "Classification failed."
        );
      }
    };


  const handleClassifyAll =
    async () => {
      if (processingAll) {
        return;
      }

      setProcessingAll(true);
      setMessage(
        "Starting batch classification..."
      );

      let totalProcessed = 0;
      let totalClassified = 0;
      let totalReview = 0;
      let totalManual = 0;
      let totalFailed = 0;

      try {
        while (true) {
          const result =
            await runBulkClassification(
              10
            );

          const processed =
            Number(
              result?.processed || 0
            );

          const remaining =
            Number(
              result?.remaining || 0
            );

          totalProcessed +=
            processed;

          totalClassified +=
            Number(
              result?.classified || 0
            );

          totalReview +=
            Number(
              result?.needs_review || 0
            );

          totalManual +=
            Number(
              result?.manual_review || 0
            );

          totalFailed +=
            Number(
              result?.failed || 0
            );

          setMessage(
            `Processing... ${totalProcessed} processed, ` +
            `${remaining} remaining.`
          );

          if (
            processed === 0 ||
            remaining === 0
          ) {
            break;
          }
        }

        setMessage(
          `Classification complete. ` +
          `Processed ${totalProcessed}, ` +
          `classified ${totalClassified}, ` +
          `needs review ${totalReview}, ` +
          `manual review ${totalManual}, ` +
          `failed ${totalFailed}.`
        );

        await refresh();

      } catch (err) {
        setMessage(
          err?.response?.data?.message ||
          err?.message ||
          "Batch classification failed."
        );

      } finally {
        setProcessingAll(false);
      }
    };


  const handleApprove =
    async (item) => {
      const productId =
        item.product;

      const categoryId =
        item.category_id ||
        item.category?.id;

      if (
        !productId ||
        !categoryId
      ) {
        return;
      }

      setActionLoading(
        `approve-${productId}`
      );

      try {
        await approveTaxonomy(
          productId,
          categoryId
        );

        setMessage(
          "Classification approved."
        );

        await refresh();

      } catch (err) {
        setMessage(
          err?.response?.data?.message ||
          err?.message ||
          "Approval failed."
        );

      } finally {
        setActionLoading(null);
      }
    };


  const handleReject =
    async (item) => {
      const productId =
        item.product;

      if (!productId) {
        return;
      }

      const reason =
        window.prompt(
          "Reason for rejecting this classification:",
          "Classification requires manual correction."
        );

      if (
        reason === null
      ) {
        return;
      }

      setActionLoading(
        `reject-${productId}`
      );

      try {
        await rejectTaxonomy(
          productId,
          reason
        );

        setMessage(
          "Classification rejected."
        );

        await refresh();

      } catch (err) {
        setMessage(
          err?.response?.data?.message ||
          err?.message ||
          "Rejection failed."
        );

      } finally {
        setActionLoading(null);
      }
    };


  const handleSearch =
    (event) => {
      setSearch(
        event.target.value
      );

      setPage(1);
    };


  const totalPages =
    Math.max(
      1,
      Math.ceil(
        total / pageSize
      )
    );


  return (
    <div className="space-y-6">

      {/* HEADER */}

      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Product Taxonomy
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            AI classification of imported products against Shopify taxonomy.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handleClassifyBatch}
            disabled={
              classificationLoading ||
              processingAll
            }
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {classificationLoading
              ? "Processing..."
              : "Classify Next 10"}
          </button>

          <button
            type="button"
            onClick={handleClassifyAll}
            disabled={
              classificationLoading ||
              processingAll
            }
            className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {processingAll
              ? "Classifying..."
              : "Classify All Pending"}
          </button>
        </div>
      </div>


      {/* MESSAGE */}

      {message && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          {message}
        </div>
      )}


      {/* ERROR */}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error?.message ||
            error?.detail ||
            "Failed to load taxonomy."}
        </div>
      )}


      {/* STATS */}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <StatCard
          title="Products"
          value={
            stats?.total_products ??
            total
          }
          description="Products imported into the database"
        />

        <StatCard
          title="Classified"
          value={
            stats?.classified ??
            0
          }
          description="High-confidence classifications"
        />

        <StatCard
          title="Needs Review"
          value={
            stats?.needs_review ??
            0
          }
          description="AI result needs approval"
        />

        <StatCard
          title="Manual Review"
          value={
            stats?.manual_review ??
            0
          }
          description="Insufficient confidence/data"
        />

        <StatCard
          title="Approved"
          value={
            stats?.approved ??
            0
          }
          description="Human-approved classifications"
        />

        <StatCard
          title="Failed"
          value={
            stats?.failed ??
            0
          }
          description="Products that encountered errors"
        />

        <StatCard
          title="Rejected"
          value={
            stats?.rejected ??
            0
          }
          description="Rejected classifications"
        />

        <StatCard
          title="Unclassified"
          value={
            stats?.unclassified ??
            0
          }
          description="Products waiting for classification"
        />

      </div>


      {/* PROGRESS */}

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-900">
              Classification Progress
            </p>

            <p className="mt-1 text-xs text-gray-500">
              {stats?.classification_progress ??
                0}
              % of products have a classification result.
            </p>
          </div>

          <span className="text-sm font-semibold text-gray-900">
            {stats?.classification_progress ??
              0}
            %
          </span>
        </div>

        <div className="mt-3 h-3 overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-gray-900 transition-all"
            style={{
              width: `${Math.min(
                Number(
                  stats?.classification_progress ||
                    0
                ),
                100
              )}%`,
            }}
          />
        </div>
      </div>


      {/* FILTERS */}

      <div className="rounded-xl border border-gray-200 bg-white p-5">

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">

          <div className="lg:col-span-2">
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Search
            </label>

            <input
              type="text"
              value={search}
              onChange={handleSearch}
              placeholder="Product title, SKU, category..."
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500"
            />
          </div>


          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Status
            </label>

            <select
              value={status}
              onChange={(event) => {
                setStatus(
                  event.target.value
                );

                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">
                All
              </option>

              <option value="classified">
                Classified
              </option>

              <option value="approved">
                Approved
              </option>

              <option value="needs_review">
                Needs Review
              </option>

              <option value="manual_review">
                Manual Review
              </option>

              <option value="rejected">
                Rejected
              </option>

              <option value="failed">
                Failed
              </option>
            </select>
          </div>


          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Classification
            </label>

            <select
              value={classification}
              onChange={(event) => {
                setClassification(
                  event.target.value
                );

                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">
                All
              </option>

              <option value="classified">
                Classified
              </option>

              <option value="unclassified">
                Unclassified
              </option>
            </select>
          </div>


          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Taxonomy Level
            </label>

            <select
              value={level}
              onChange={(event) => {
                setLevel(
                  event.target.value
                );

                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">
                All Levels
              </option>

              {[0, 1, 2, 3, 4, 5].map(
                (value) => (
                  <option
                    key={value}
                    value={value}
                  >
                    Level {value}
                  </option>
                )
              )}
            </select>
          </div>

        </div>
      </div>


      {/* TABLE */}

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">

        {productsLoading ? (
          <div className="p-12 text-center text-sm text-gray-500">
            Loading classification results...
          </div>
        ) : products.length === 0 ? (
          <div className="p-12 text-center">
            <p className="font-semibold text-gray-900">
              No classification results found
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Import products and run AI classification.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">

            <table className="min-w-full divide-y divide-gray-200">

              <thead className="bg-gray-50">
                <tr>

                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Product
                  </th>

                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Shopify Taxonomy
                  </th>

                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Attributes
                  </th>

                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Confidence
                  </th>

                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Status
                  </th>

                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Actions
                  </th>

                </tr>
              </thead>


              <tbody className="divide-y divide-gray-200">

                {products.map(
                  (item) => {
                    const productId =
                      item.product;

                    const category =
                      item.category ||
                      null;

                    const percentage =
                      confidencePercent(
                        item.confidence
                      );

                    const attributes =
                      Array.isArray(
                        item.attributes
                      )
                        ? item.attributes
                        : [];

                    const alternatives =
                      Array.isArray(
                        item.alternatives
                      )
                        ? item.alternatives
                        : [];

                    const isExpanded =
                      expandedProduct ===
                      productId;

                    return (
                      <tr
                        key={
                          item.id ||
                          productId
                        }
                        className="align-top hover:bg-gray-50"
                      >

                        {/* PRODUCT */}

                        <td className="px-5 py-4">

                          <div className="font-semibold text-gray-900">
                            {item.product_title ||
                              `Product #${productId}`}
                          </div>

                          {item.product_sku && (
                            <div className="mt-1 text-xs text-gray-500">
                              SKU: {item.product_sku}
                            </div>
                          )}

                          {item.product_external_id && (
                            <div className="mt-1 text-xs text-gray-400">
                              External ID:{" "}
                              {item.product_external_id}
                            </div>
                          )}

                          <div className="mt-2 flex flex-wrap gap-2">

                            {item.image_status && (
                              <span className="rounded-full bg-gray-100 px-2 py-1 text-[11px] text-gray-600">
                                Image:{" "}
                                {item.image_status}
                              </span>
                            )}

                          </div>

                        </td>


                        {/* CATEGORY */}

                        <td className="px-5 py-4">

                          {category ? (
                            <div>

                              <div className="font-semibold text-gray-900">
                                {item.category_name ||
                                  category.name}
                              </div>

                              <div className="mt-1 max-w-lg text-xs leading-5 text-gray-500">
                                {item.category_full_name ||
                                  category.full_name}
                              </div>

                              <div className="mt-2 flex flex-wrap gap-2">

                                {item.category_level !==
                                  null &&
                                  item.category_level !==
                                    undefined && (
                                    <span className="rounded-full bg-gray-100 px-2 py-1 text-[11px] text-gray-600">
                                      Level{" "}
                                      {item.category_level}
                                    </span>
                                  )}

                                {category.shopify_id && (
                                  <span className="rounded-full bg-gray-100 px-2 py-1 font-mono text-[11px] text-gray-600">
                                    {category.shopify_id}
                                  </span>
                                )}

                              </div>

                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">
                              No category assigned
                            </span>
                          )}

                        </td>


                        {/* ATTRIBUTES */}

                        <td className="px-5 py-4">

                          {attributes.length ===
                          0 ? (
                            <span className="text-xs text-gray-400">
                              No detected attributes
                            </span>
                          ) : (
                            <div className="space-y-2">

                              {attributes
                                .slice(0, 4)
                                .map(
                                  (
                                    attribute
                                  ) => (
                                    <div
                                      key={
                                        attribute.attribute_id
                                      }
                                    >
                                      <p className="text-xs font-semibold text-gray-700">
                                        {
                                          attribute.name
                                        }
                                      </p>

                                      {attribute.values
                                        ?.slice(
                                          0,
                                          3
                                        )
                                        .map(
                                          (
                                            value
                                          ) => (
                                            <span
                                              key={
                                                value.id
                                              }
                                              className="mr-1 mt-1 inline-block rounded-full bg-blue-50 px-2 py-1 text-[11px] text-blue-700"
                                            >
                                              {
                                                value.name
                                              }
                                            </span>
                                          )
                                        )}
                                    </div>
                                  )
                                )}

                            </div>
                          )}

                        </td>


                        {/* CONFIDENCE */}

                        <td className="px-5 py-4">
                          <ConfidenceBar
                            value={
                              item.confidence
                            }
                          />
                        </td>


                        {/* STATUS */}

                        <td className="px-5 py-4">

                          <span
                            className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(
                              item.status
                            )}`}
                          >
                            {statusLabel(
                              item.status
                            )}
                          </span>

                          {item.review_reason && (
                            <p className="mt-2 max-w-xs text-xs leading-5 text-gray-500">
                              {
                                item.review_reason
                              }
                            </p>
                          )}

                        </td>


                        {/* ACTIONS */}

                        <td className="px-5 py-4">

                          <div className="flex flex-col items-end gap-2">

                            <button
                              type="button"
                              onClick={() =>
                                setExpandedProduct(
                                  isExpanded
                                    ? null
                                    : productId
                                )
                              }
                              className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
                            >
                              {isExpanded
                                ? "Hide Details"
                                : "Details"}
                            </button>


                            {category &&
                              [
                                "classified",
                                "needs_review",
                                "manual_review",
                              ].includes(
                                item.status
                              ) && (
                                <div className="flex gap-2">

                                  <button
                                    type="button"
                                    disabled={
                                      actionLoading ===
                                      `approve-${productId}`
                                    }
                                    onClick={() =>
                                      handleApprove(
                                        item
                                      )
                                    }
                                    className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
                                  >
                                    {actionLoading ===
                                    `approve-${productId}`
                                      ? "..."
                                      : "Approve"}
                                  </button>

                                  <button
                                    type="button"
                                    disabled={
                                      actionLoading ===
                                      `reject-${productId}`
                                    }
                                    onClick={() =>
                                      handleReject(
                                        item
                                      )
                                    }
                                    className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50"
                                  >
                                    {actionLoading ===
                                    `reject-${productId}`
                                      ? "..."
                                      : "Reject"}
                                  </button>

                                </div>
                              )}

                          </div>

                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>


            {/* EXPANDED DETAILS */}

            {expandedProduct && (
              <div className="border-t border-gray-200 bg-gray-50 p-6">

                {products
                  .filter(
                    (item) =>
                      item.product ===
                      expandedProduct
                  )
                  .map(
                    (item) => (
                      <div
                        key={
                          item.product
                        }
                        className="grid gap-6 lg:grid-cols-3"
                      >

                        <div>
                          <h3 className="font-semibold text-gray-900">
                            AI Reason
                          </h3>

                          <p className="mt-2 rounded-lg bg-white p-4 text-sm leading-6 text-gray-600">
                            {item.ai_reason ||
                              "No AI explanation available."}
                          </p>
                        </div>


                        <div>
                          <h3 className="font-semibold text-gray-900">
                            Matched Product Terms
                          </h3>

                          <p className="mt-2 rounded-lg bg-white p-4 text-sm leading-6 text-gray-600">
                            {item.matched_text ||
                              "No matched terms recorded."}
                          </p>
                        </div>


                        <div>
                          <h3 className="font-semibold text-gray-900">
                            Alternative Categories
                          </h3>

                          {item.alternatives?.length ? (
                            <div className="mt-2 space-y-2">
                              {item.alternatives.map(
                                (
                                  alternative
                                ) => (
                                  <div
                                    key={
                                      alternative.category_id
                                    }
                                    className="rounded-lg border border-gray-200 bg-white p-3"
                                  >
                                    <p className="text-sm font-medium text-gray-900">
                                      {
                                        alternative.name
                                      }
                                    </p>

                                    <p className="mt-1 text-xs text-gray-500">
                                      {
                                        alternative.full_name
                                      }
                                    </p>

                                    <p className="mt-1 text-xs font-semibold text-gray-700">
                                      {confidencePercent(
                                        alternative.confidence
                                      )}
                                      % match
                                    </p>
                                  </div>
                                )
                              )}
                            </div>
                          ) : (
                            <p className="mt-2 text-sm text-gray-400">
                              No alternatives available.
                            </p>
                          )}

                        </div>

                      </div>
                    )
                  )}

              </div>
            )}

          </div>
        )}

        {/* PAGINATION */}

        {total > 0 && (
          <div className="flex items-center justify-between border-t border-gray-200 px-5 py-4">

            <p className="text-sm text-gray-500">
              Page {page} of{" "}
              {totalPages}
            </p>

            <div className="flex gap-2">

              <button
                type="button"
                disabled={page <= 1}
                onClick={() =>
                  setPage(
                    (value) =>
                      value - 1
                  )
                }
                className="rounded-md border border-gray-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>

              <button
                type="button"
                disabled={
                  page >= totalPages
                }
                onClick={() =>
                  setPage(
                    (value) =>
                      value + 1
                  )
                }
                className="rounded-md border border-gray-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}
