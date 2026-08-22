import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Dashboard",
    path: "/"
  },
  {
    label: "Imports",
    path: "/imports"
  },
  {
    label: "Taxonomy",
    path: "/taxonomy"
  },
  {
    label: "Processing",
    path: "/processing"
  },
  {
    label: "Results",
    path: "/results"
  },
  {
    label: "Review Queue",
    path: "/review"
  },
];

export default function Sidebar({ mobileOpen, onClose }) {
  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/50 lg:hidden"
        />
      )}

      <aside
        className={[
          "fixed inset-y-0 left-0 z-50 w-72 border-r border-slate-200",
          "bg-white transition-transform duration-300 ease-in-out",
          "lg:w-64 lg:translate-x-0",
          mobileOpen
            ? "translate-x-0"
            : "-translate-x-full"
        ].join(" ")}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-5 sm:px-6">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Shopify
            </p>

            <h1 className="truncate text-base font-bold text-slate-900 sm:text-lg">
              Classification AI
            </h1>
          </div>

          {/* Mobile close button */}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close navigation"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900 lg:hidden"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="space-y-1 p-3 sm:p-4">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                [
                  "flex min-h-11 items-center rounded-lg px-3 py-3",
                  "text-sm font-medium transition-colors",
                  "sm:px-4",
                  isActive
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}