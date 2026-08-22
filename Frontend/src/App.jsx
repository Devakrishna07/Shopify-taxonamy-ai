import { BrowserRouter } from "react-router-dom";
import { Routes, Route } from "react-router-dom";

import AppShell from "./components/layout/AppShell";
import Dashboard from "./features/dashboard/Dashboard";
import ImportsPage from "./features/imports/ImportsPage";
import TaxonomyPage from "./features/taxonomy/TaxonomyPage";
import ClassificationPage from "./features/classification/ClassificationPage";

function PlaceholderPage({ title }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold text-slate-900">
        {title}
      </h1>

      <p className="mt-2 text-sm text-slate-500">
        This module will be implemented in its assigned sprint.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Dashboard />} />

          <Route
            path="/imports"
            element={<ImportsPage />}
          />

          <Route
            path="/taxonomy"
            element={<TaxonomyPage/>}
          />

          <Route
            path="/processing"
            element={<PlaceholderPage title="Processing Jobs" />}
          />

          <Route
            path="/processing/:id"
            element={<PlaceholderPage title="Batch / Job Monitor" />}
          />

          <Route
            path="/results"
            element={<PlaceholderPage title="Results Workspace" />}
          />

          <Route
            path="/results/:id"
            element={<PlaceholderPage title="Result Detail" />}
          />

          <Route
            path="/review"
            element={<PlaceholderPage title="Review Queue" />}
          />

          <Route
            path="/products/:id/classification"
            element={<ClassificationPage/>}
          />

          <Route
            path="/products/:id/attributes"
            element={<PlaceholderPage title="Attributes View" />}
          />

          <Route
            path="/products/:id/signals"
            element={<PlaceholderPage title="AI / Review Signals" />}
          />

          <Route
            path="*"
            element={<PlaceholderPage title="Page Not Found" />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}