import { useCallback, useEffect, useState } from "react";

import { useTaxonomy } from "../../hooks/useTaxonomy";

import TaxonomySearch from "../../components/taxonomy/TaxonomySearch";
import TaxonomyTable from "../../components/taxonomy/TaxonomyTable";
import TaxonomyDetails from "../../components/taxonomy/TaxonomyDetails";

import LoadingState from "../../components/common/LoadingState";
import ErrorState from "../../components/common/ErrorState";

export default function TaxonomyPage() {
  const {
    categories,
    searchResults,
    loading,
    searchLoading,
    error,
    loadCategories,
    search,
  } = useTaxonomy();

  const [selectedCategory, setSelectedCategory] =
    useState(null);

  const [level, setLevel] = useState("");
  const [rootOnly, setRootOnly] =
    useState(false);

  const [searchMode, setSearchMode] =
    useState(false);

  const loadInitialCategories = useCallback(() => {
    return loadCategories({
      level,
      root: rootOnly ? "true" : "",
    });
  }, [loadCategories, level, rootOnly]);

  useEffect(() => {
    loadInitialCategories();
  }, [loadInitialCategories]);

  const handleSearch = useCallback(
    async (query) => {
      if (!query.trim()) {
        setSearchMode(false);
        return;
      }

      setSearchMode(true);

      await search(query);
    },
    [search]
  );

  const displayedCategories = searchMode
    ? searchResults
    : categories;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Taxonomy Explorer
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Browse and search the Shopify product taxonomy.
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-5">
        <TaxonomySearch
          onSearch={handleSearch}
          loading={searchLoading}
        />

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <label className="text-sm font-medium text-gray-700">
            Level
          </label>

          <select
            value={level}
            onChange={(event) =>
              setLevel(event.target.value)
            }
            className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All levels</option>
            <option value="0">Level 0</option>
            <option value="1">Level 1</option>
            <option value="2">Level 2</option>
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5</option>
          </select>

          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={rootOnly}
              onChange={(event) =>
                setRootOnly(event.target.checked)
              }
              className="rounded border-gray-300"
            />

            Root categories only
          </label>

          <button
            type="button"
            onClick={() => {
              setSearchMode(false);
              loadInitialCategories();
            }}
            className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
          >
            Apply Filters
          </button>
        </div>
      </div>

      {error && (
        <ErrorState
          message={error.message}
          onRetry={loadInitialCategories}
        />
      )}

      {loading ? (
        <LoadingState message="Loading taxonomy..." />
      ) : (
        <TaxonomyTable
          categories={displayedCategories}
          onSelect={setSelectedCategory}
        />
      )}

      {selectedCategory && (
        <TaxonomyDetails
          category={selectedCategory}
          onClose={() =>
            setSelectedCategory(null)
          }
        />
      )}
    </div>
  );
}