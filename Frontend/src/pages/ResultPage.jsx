import React, {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getResults,
  getResultsSummary,
  getResultById,
} from "../api/results.api";

import ResultsSummary from "../components/results/ResultsSummary";
import ResultsFilters from "../components/results/ResultsFilters";
import ResultsTable from "../components/results/ResultsTable";
import ResultDetail from "../components/results/ResultDetail";

const INITIAL_FILTERS = {
  search: "",
  status: "",
  min_confidence: "",
  ordering: "-id",
};

export default function ResultsPage() {
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(null);

  const [filters, setFilters] =
    useState(INITIAL_FILTERS);

  const [loading, setLoading] =
    useState(true);

  const [summaryLoading, setSummaryLoading] =
    useState(true);

  const [error, setError] = useState("");

  const [selectedResult, setSelectedResult] =
    useState(null);

  const [detailLoading, setDetailLoading] =
    useState(false);

  const loadResults = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const params = {};

      if (filters.search.trim()) {
        params.search = filters.search.trim();
      }

      if (filters.status) {
        params.status = filters.status;
      }

      if (filters.min_confidence) {
        params.min_confidence =
          filters.min_confidence;
      }

      if (filters.ordering) {
        params.ordering = filters.ordering;
      }

      const data = await getResults(params);

      setResults(
        Array.isArray(data)
          ? data
          : data?.results || []
      );
    } catch (err) {
      console.error(
        "Failed to load results:",
        err
      );

      setError(
        err?.response?.data?.detail ||
          "Failed to load classification results."
      );
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const loadSummary = useCallback(async () => {
    try {
      setSummaryLoading(true);

      const data =
        await getResultsSummary();

      setSummary(data);
    } catch (err) {
      console.error(
        "Failed to load summary:",
        err
      );
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadResults();
  }, [loadResults]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  function handleFilterChange(
    key,
    value
  ) {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function handleResetFilters() {
    setFilters(INITIAL_FILTERS);
  }

  async function handleSelectResult(result) {
    try {
      setDetailLoading(true);

      const fullResult =
        await getResultById(result.id);

      setSelectedResult(fullResult);
    } catch (err) {
      console.error(
        "Failed to load result:",
        err
      );

      setSelectedResult(result);
    } finally {
      setDetailLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Classification Results
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Review AI classification results and
            decision status.
          </p>
        </div>

        <ResultsSummary
          summary={summary}
          loading={summaryLoading}
        />

        <ResultsFilters
          filters={filters}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
        />

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <ResultsTable
          results={results}
          loading={loading}
          onSelect={handleSelectResult}
        />

        {detailLoading && (
          <div className="text-center text-sm text-gray-500">
            Loading result details...
          </div>
        )}

        {selectedResult && (
          <ResultDetail
            result={selectedResult}
            onClose={() =>
              setSelectedResult(null)
            }
          />
        )}
      </div>
    </div>
  );
}