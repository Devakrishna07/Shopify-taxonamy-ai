import { useEffect, useState } from "react";

export default function TaxonomySearch({
  onSearch,
  loading = false,
}) {
  const [query, setQuery] = useState("");

  useEffect(() => {
    const timeout = setTimeout(() => {
      onSearch(query);
    }, 400);

    return () => clearTimeout(timeout);
  }, [query, onSearch]);

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(event) =>
          setQuery(event.target.value)
        }
        placeholder="Search Shopify taxonomy..."
        className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 pr-24 text-sm outline-none transition focus:border-gray-900 focus:ring-1 focus:ring-gray-900"
      />

      {loading && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
        </div>
      )}
    </div>
  );
}