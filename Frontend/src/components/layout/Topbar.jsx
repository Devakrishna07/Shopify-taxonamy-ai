export default function Topbar({ onMenuClick }) {
  return (
    <header className="fixed left-0 right-0 top-0 z-30 h-16 border-b border-slate-200 bg-white lg:left-64">
      <div className="flex h-full items-center justify-between gap-3 px-3 sm:px-4 md:px-6">
        {/* Mobile menu */}
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onMenuClick}
            aria-label="Open navigation"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold text-slate-900 sm:text-base md:text-lg">
              Shopify Product Classification AI
            </h2>

            <p className="hidden text-xs text-slate-500 sm:block">
              Frontend operational console
            </p>
          </div>
        </div>

        {/* Backend status */}
        <div className="shrink-0">
          <div className="hidden rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 sm:block">
            Backend Connected
          </div>

          <div
            className="h-2.5 w-2.5 rounded-full bg-green-500 sm:hidden"
            title="Backend Connected"
          />
        </div>
      </div>
    </header>
  );
}