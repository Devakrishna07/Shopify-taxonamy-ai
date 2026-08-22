export default function TaxonomyTable({
  categories = [],
  onSelect,
}) {
  if (!categories.length) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
        No taxonomy categories found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                Category
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                Shopify ID
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                Level
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                Type
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {categories.map((category) => (
              <tr
                key={category.id}
                onClick={() => onSelect?.(category)}
                className="cursor-pointer hover:bg-gray-50"
              >
                <td className="px-4 py-4">
                  <div className="font-medium text-gray-900">
                    {category.name}
                  </div>

                  {category.full_name && (
                    <div className="mt-1 text-xs text-gray-500">
                      {category.full_name}
                    </div>
                  )}
                </td>

                <td className="px-4 py-4 text-sm text-gray-600">
                  {category.shopify_id}
                </td>

                <td className="px-4 py-4 text-sm text-gray-600">
                  {category.level}
                </td>

                <td className="px-4 py-4">
                  {category.is_root ? (
                    <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
                      Root
                    </span>
                  ) : category.is_leaf ? (
                    <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                      Leaf
                    </span>
                  ) : (
                    <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700">
                      Branch
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}