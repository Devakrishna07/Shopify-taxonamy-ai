import React from "react";
import ResultStatusBadge from "./ResultStatusBadge";
import {
  formatConfidence,
  getDecisionLabel,
} from "../../utils/results.utils";

export default function ResultDetail({
  result,
  onClose,
}) {
  if (!result) {
    return null;
  }

  const product = result.product;
  const decision = result.decision;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Classification Result
            </h2>

            <p className="text-sm text-gray-500">
              Result #{result.id}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-2 text-gray-500 hover:bg-gray-100"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6 p-6">
          <section>
            <h3 className="mb-3 text-sm font-semibold uppercase text-gray-500">
              Product
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Info
                label="Title"
                value={product?.title}
              />

              <Info
                label="SKU"
                value={product?.sku}
              />

              <Info
                label="Brand"
                value={product?.brand}
              />

              <Info
                label="Product Type"
                value={product?.product_type}
              />

              <Info
                label="Existing Category"
                value={product?.existing_category}
              />

              <Info
                label="Existing Subcategory"
                value={product?.existing_subcategory}
              />
            </div>

            {product?.images && product.images.length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">Images</p>
                <div className="flex gap-4 overflow-x-auto py-2">
                  {product.images.map((img) => (
                    <img 
                      key={img.id} 
                      src={img.url} 
                      alt={product.title || "Product"} 
                      className="h-32 w-32 object-contain rounded-md border border-gray-200 bg-gray-50"
                      onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />
                  ))}
                </div>
              </div>
            )}
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold uppercase text-gray-500">
              Classification
            </h3>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <Info
                label="Confidence"
                value={formatConfidence(
                  result.confidence
                )}
              />

              <div>
                <p className="text-xs text-gray-500">
                  Status
                </p>

                <div className="mt-1">
                  <ResultStatusBadge
                    status={result.status}
                  />
                </div>
              </div>

              <Info
                label="Decision"
                value={getDecisionLabel(
                  decision?.decision_status
                )}
              />
            </div>
          </section>

          {decision && (
            <section>
              <h3 className="mb-3 text-sm font-semibold uppercase text-gray-500">
                Decision & Review
              </h3>

              <div className="space-y-4">
                <Info
                  label="Decision Reason"
                  value={
                    decision.decision_reason ||
                    "—"
                  }
                />

                <Info
                  label="Review Comment"
                  value={
                    decision.review_comment ||
                    "—"
                  }
                />

                <Info
                  label="Final Category ID"
                  value={
                    decision.final_category_id ??
                    "—"
                  }
                />

                <Info
                  label="Review Action"
                  value={
                    decision.review_action ||
                    "—"
                  }
                />

                <div>
                  <p className="text-xs text-gray-500">
                    AI Prediction
                  </p>

                  <pre className="mt-1 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs">
                    {JSON.stringify(
                      decision.ai_prediction,
                      null,
                      2
                    )}
                  </pre>
                </div>

                <div>
                  <p className="text-xs text-gray-500">
                    AI Alternatives
                  </p>

                  <pre className="mt-1 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs">
                    {JSON.stringify(
                      decision.ai_alternatives,
                      null,
                      2
                    )}
                  </pre>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div>
      <p className="text-xs text-gray-500">
        {label}
      </p>

      <p className="mt-1 break-words text-sm font-medium text-gray-900">
        {value ?? "—"}
      </p>
    </div>
  );
}