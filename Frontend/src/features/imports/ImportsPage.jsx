import { useState, useEffect } from "react";

import ImportDropzone from "./ImportDropzone";
import ImportResult from "./ImportResult";
import ValidationSummary from "./ValidationSummary";

import {
  uploadProducts,
  getImport,
  getImports,
} from "../../api/imports.api";

import {
  normalizeImportResponse,
} from "./imports.utils";

export default function ImportsPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [importResult, setImportResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const [error, setError] = useState("");

  // --------------------------------------------------
  // FILE SELECTED
  // --------------------------------------------------

  function handleFileSelected(file) {
    console.log("[ImportsPage] File selected:", file);

    setSelectedFile(file);
    setImportResult(null);
    setError("");
  }

  // --------------------------------------------------
  // IMPORT PRODUCTS
  // --------------------------------------------------

  async function handleImport() {
    console.log("[ImportsPage] handleImport() called");
    console.log("[ImportsPage] selectedFile:", selectedFile);

    if (!selectedFile) {
      setError("Please select a CSV or XLSX file first.");
      return;
    }

    setError("");
    setImportResult(null);
    setLoading(true);

    try {
      console.log(
        "[ImportsPage] Sending file to backend:",
        selectedFile.name
      );

      const response = await uploadProducts(selectedFile);

      console.log(
        "[ImportsPage] Backend response:",
        response
      );

      const normalized = normalizeImportResponse(
        response?.data ?? response
      );

      console.log(
        "[ImportsPage] Normalized response:",
        normalized
      );

      setImportResult(normalized);
    } catch (err) {
      console.error(
        "[ImportsPage] Import failed:",
        err
      );

      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  // --------------------------------------------------
  // REFRESH IMPORT STATUS
  // --------------------------------------------------

  async function handleRefresh() {
    if (!importResult?.id) {
      return;
    }

    console.log(
      "[ImportsPage] Refreshing import:",
      importResult.id
    );

    setRefreshing(true);
    setError("");

    try {
      const response = await getImport(
        importResult.id
      );

      console.log(
        "[ImportsPage] Refresh response:",
        response
      );

      const normalized = normalizeImportResponse(
        response?.data ?? response
      );

      setImportResult(normalized);
    } catch (err) {
      console.error(
        "[ImportsPage] Refresh failed:",
        err
      );

      setError(getErrorMessage(err));
    } finally {
      setRefreshing(false);
    }
  }

  // --------------------------------------------------
  // ERROR HANDLING
  // --------------------------------------------------

  function getErrorMessage(error) {
    if (error?.response?.data) {
      const data = error.response.data;

      if (typeof data === "string") {
        return data;
      }

      if (data.error) {
        return data.error;
      }

      if (data.detail) {
        return data.detail;
      }

      if (data.message) {
        return data.message;
      }

      if (
        Array.isArray(data.non_field_errors)
      ) {
        return data.non_field_errors.join(", ");
      }

      if (
        typeof data === "object"
      ) {
        return Object.entries(data)
          .map(([field, messages]) => {
            if (Array.isArray(messages)) {
              return `${field}: ${messages.join(", ")}`;
            }

            return `${field}: ${messages}`;
          })
          .join(" | ");
      }
    }

    if (error?.data) {
      if (typeof error.data === "string") {
        return error.data;
      }

      if (error.data.error) {
        return error.data.error;
      }

      if (error.data.detail) {
        return error.data.detail;
      }

      if (error.data.message) {
        return error.data.message;
      }
    }

    if (error?.request) {
      return (
        "Unable to connect to the Django backend. " +
        "Make sure the backend is running on " +
        "http://localhost:8000."
      );
    }

    return (
      error?.message ||
      "Unable to import the products."
    );
  }

  // --------------------------------------------------
  // LOAD RECENT IMPORT ON MOUNT
  // --------------------------------------------------

  useEffect(() => {
    async function loadRecentImport() {
      try {
        const response = await getImports();
        const data = response?.data ?? response;
        if (data && data.length > 0) {
          setImportResult(normalizeImportResponse(data[0]));
        }
      } catch (err) {
        console.error("[ImportsPage] Failed to load recent import:", err);
      }
    }
    loadRecentImport();
  }, []);

  // --------------------------------------------------
  // PAGE
  // --------------------------------------------------

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto w-full max-w-6xl px-6 py-10">

        {/* PAGE HEADER */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Import Products
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            Upload your Shopify product dataset
            using a CSV or XLSX file. The file will
            be sent to the Django backend for import
            processing.
          </p>
        </header>

        {/* ERROR */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-5">
            <div className="flex items-start gap-3">
              <div className="text-xl">
                ⚠
              </div>

              <div>
                <h2 className="font-semibold text-red-800">
                  Import Error
                </h2>

                <p className="mt-1 text-sm text-red-700">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* UPLOAD SECTION */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="mb-6">
            <h2 className="text-xl font-semibold text-slate-900">
              Upload Product Data
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Select a CSV or XLSX file containing
              your Shopify product data.
            </p>
          </div>

          {/* DROPZONE */}
          <ImportDropzone
            selectedFile={selectedFile}
            onFileSelected={handleFileSelected}
            disabled={loading}
          />

          {/* ACTION BUTTONS */}
          <div className="mt-6 flex flex-wrap items-center gap-3">

            <button
              type="button"
              onClick={handleImport}
              disabled={
                !selectedFile || loading
              }
              className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Uploading..."
                : "Upload & Import"}
            </button>

            {selectedFile && !loading && (
              <button
                type="button"
                onClick={() =>
                  handleFileSelected(null)
                }
                className="rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                Clear File
              </button>
            )}

          </div>

          {/* UPLOAD STATUS */}
          {loading && (
            <div className="mt-6 rounded-lg border border-blue-200 bg-blue-50 p-4">
              <div className="flex items-center gap-3">

                <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" />

                <div>
                  <p className="text-sm font-semibold text-blue-800">
                    Uploading product file...
                  </p>

                  <p className="mt-1 text-xs text-blue-600">
                    Sending the file to the Django
                    backend. Please wait.
                  </p>
                </div>

              </div>
            </div>
          )}

        </section>

        {/* IMPORT RESULT */}
        {importResult && (
          <ImportResult
            result={importResult}
            onRefresh={handleRefresh}
            refreshing={refreshing}
          />
        )}

        {/* VALIDATION SUMMARY */}
        {importResult && (
          <ValidationSummary
            result={importResult}
          />
        )}

      </div>
    </main>
  );
}