export default function TaxonomyDetails({
  category,
  onClose,
}) {
  if (!category) {
    return null;
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Selected Category
          </p>

          <h2 className="mt-1 text-xl font-semibold text-gray-900">
            {category.name}
          </h2>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-3 py-1 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-900"
          >
            Close
          </button>
        )}
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs text-gray-500">
            Shopify ID
          </p>

          <p className="mt-1 font-medium text-gray-900">
            {category.shopify_id}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-500">
            Level
          </p>

          <p className="mt-1 font-medium text-gray-900">
            {category.level}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-500">
            Parent ID
          </p>

          <p className="mt-1 font-medium text-gray-900">
            {category.parent_id || "None"}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-500">
            Category Type
          </p>

          <p className="mt-1 font-medium text-gray-900">
            {category.is_root
              ? "Root"
              : category.is_leaf
              ? "Leaf"
              : "Branch"}
          </p>
        </div>
      </div>

      <div className="mt-6">
        <p className="text-xs text-gray-500">
          Full Taxonomy Path
        </p>

        <p className="mt-1 rounded-md bg-gray-50 p-3 text-sm text-gray-800">
          {category.full_name || category.name}
        </p>
      </div>
    </div>
  );
}