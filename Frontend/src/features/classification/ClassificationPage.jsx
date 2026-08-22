import { useState } from "react";
import classificationApi from "../../api/classification.api";
import ClassificationResult from "./ClassificationResult";

export default function ClassificationPage() {
  const [productId, setProductId] = useState("");
  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [loadingResult, setLoadingResult] = useState(false);
  const [error, setError] = useState("");

  const handleClassify = async (event) => {
    event.preventDefault();

    const id = Number(productId);

    if (!id || id <= 0) {
      setError("Enter a valid product ID.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response =
        await classificationApi.classifyProduct(id);

      setResult(response.data ?? response);
    } catch (err) {
      const message =
        err?.response?.data?.error ||
        err?.response?.data?.detail ||
        err?.message ||
        "Classification failed.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadResult = async () => {
    const id = Number(productId);

    if (!id || id <= 0) {
      setError("Enter a valid product ID.");
      return;
    }

    setLoadingResult(true);
    setError("");

    try {
      const response =
        await classificationApi.getClassification(id);

      setResult(response.data ?? response);
    } catch (err) {
      const message =
        err?.response?.data?.error ||
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to load classification result.";

      setError(message);
    } finally {
      setLoadingResult(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Product Classification
          </h1>

          <p className="mt-2 text-sm text-gray-600">
            Classify a product and inspect its predicted
            Shopify category, confidence and alternatives.
          </p>
        </div>

        {/* Controls */}
        <section className="mb-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <form
            onSubmit={handleClassify}
            className="flex flex-col gap-4 md:flex-row md:items-end"
          >
            <div className="flex-1">
              <label
                htmlFor="productId"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Product ID
              </label>

              <input
                id="productId"
                type="number"
                min="1"
                value={productId}
                onChange={(event) =>
                  setProductId(event.target.value)
                }
                placeholder="Enter product ID"
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-indigo-600 px-5 py-2.5 font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Classifying..."
                : "Classify Product"}
            </button>

            <button
              type="button"
              onClick={handleLoadResult}
              disabled={loadingResult}
              className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loadingResult
                ? "Loading..."
                : "Load Existing Result"}
            </button>
          </form>

          {error && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}
        </section>

        {/* Result */}
        {result ? (
          <ClassificationResult result={result} />
        ) : (
          <div className="rounded-xl border border-dashed border-gray-300 bg-white p-12 text-center">
            <h2 className="text-lg font-semibold text-gray-900">
              No classification selected
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              Enter a product ID and classify it to view
              the result.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}