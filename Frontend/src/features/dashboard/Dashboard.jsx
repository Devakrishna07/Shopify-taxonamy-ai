// const cards = [
//   {
//     title: "Imported Products",
//     value: "—"
//   },
//   {
//     title: "Active Jobs",
//     value: "—"
//   },
//   {
//     title: "Completed",
//     value: "—"
//   },
//   {
//     title: "Needs Review",
//     value: "—"
//   }
// ];

// export default function Dashboard() {
//   return (
//     <div>
//       <div className="mb-8">
//         <h1 className="text-3xl font-bold text-slate-900">
//           Dashboard
//         </h1>

//         <p className="mt-2 text-slate-500">
//           Operational overview of the Shopify product
//           classification pipeline.
//         </p>
//       </div>

//       <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
//         {cards.map((card) => (
//           <div
//             key={card.title}
//             className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
//           >
//             <p className="text-sm font-medium text-slate-500">
//               {card.title}
//             </p>

//             <p className="mt-3 text-3xl font-bold text-slate-900">
//               {card.value}
//             </p>
//           </div>
//         ))}
//       </div>

//       <div className="mt-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
//         <h2 className="text-lg font-semibold text-slate-900">
//           System Foundation
//         </h2>

//         <p className="mt-2 text-sm leading-6 text-slate-600">
//           The frontend foundation is ready. Subsequent modules
//           will replace these placeholders with live data from
//           the Django REST backend.
//         </p>
//       </div>
//     </div>
//   );
// }

import { useEffect, useState } from "react";

import { getProcessingJobs } from "../../api/processing.api";
import { getApiErrorMessage } from "../../utils/apiError";

export default function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [jobCount, setJobCount] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function checkBackend() {
      try {
        const data = await getProcessingJobs();

        setBackendStatus("connected");

        if (Array.isArray(data)) {
          setJobCount(data.length);
        } else if (Array.isArray(data?.results)) {
          setJobCount(data.results.length);
        } else {
          setJobCount(null);
        }
      } catch (err) {
        setBackendStatus("disconnected");
        setError(getApiErrorMessage(err));
      }
    }

    checkBackend();
  }, []);

  const statusText = {
    checking: "Checking...",
    connected: "Connected",
    disconnected: "Disconnected"
  };

  return (
    <div className="mx-auto w-full max-w-[1600px]">
      {/* Page heading */}
      <section className="mb-6 sm:mb-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="min-w-0">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl lg:text-4xl">
              Dashboard
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
              Operational overview of the Shopify product
              classification pipeline.
            </p>
          </div>

          <div className="shrink-0">
            <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600">
              Foundation Module
            </span>
          </div>
        </div>
      </section>

      {/* KPI cards */}
      <section
        aria-label="Dashboard statistics"
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <StatCard
          title="Backend"
          value={statusText[backendStatus]}
          status={backendStatus}
        />

        <StatCard
          title="Processing Jobs"
          value={jobCount ?? "—"}
        />

        <StatCard
          title="Imported Products"
          value="—"
        />

        <StatCard
          title="Needs Review"
          value="—"
        />
      </section>

      {/* Backend error */}
      {backendStatus === "disconnected" && (
        <section className="mt-6">
          <div
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 p-4 sm:p-5"
          >
            <h2 className="text-sm font-semibold text-red-800 sm:text-base">
              Backend connection failed
            </h2>

            <p className="mt-1 break-words text-sm leading-6 text-red-700">
              {error}
            </p>

            <p className="mt-2 text-xs leading-5 text-red-600">
              Check VITE_API_BASE_URL and confirm Django is
              running.
            </p>
          </div>
        </section>
      )}

      {/* Backend success */}
      {backendStatus === "connected" && (
        <section className="mt-6">
          <div className="flex flex-col gap-3 rounded-xl border border-green-200 bg-green-50 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-green-800 sm:text-base">
                Django REST API connected
              </h2>

              <p className="mt-1 text-sm leading-6 text-green-700">
                The frontend successfully reached the processing
                endpoint.
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2 text-xs font-medium text-green-700">
              <span className="h-2.5 w-2.5 rounded-full bg-green-500" />
              Online
            </div>
          </div>
        </section>
      )}

      {/* System information */}
      <section className="mt-6">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <div className="flex flex-col gap-2">
            <h2 className="text-base font-semibold text-slate-900 sm:text-lg">
              System Foundation
            </h2>

            <p className="text-sm leading-6 text-slate-600">
              The frontend foundation is ready. Subsequent
              modules will replace these placeholders with live
              data from the Django REST backend.
            </p>
          </div>

          {/* Responsive architecture indicator */}
          <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <ArchitectureItem
              title="React"
              description="UI layer"
            />

            <ArchitectureItem
              title="Vite"
              description="Build system"
            />

            <ArchitectureItem
              title="Tailwind CSS"
              description="Responsive styling"
            />

            <ArchitectureItem
              title="Django API"
              description="Backend integration"
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function StatCard({ title, value, status }) {
  const isConnected = status === "connected";
  const isDisconnected = status === "disconnected";

  return (
    <article className="min-w-0 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md sm:p-5 lg:p-6">
      <div className="flex items-start justify-between gap-3">
        <p className="min-w-0 text-sm font-medium text-slate-500">
          {title}
        </p>

        {status && (
          <span
            className={[
              "mt-1 h-2.5 w-2.5 shrink-0 rounded-full",
              isConnected && "bg-green-500",
              isDisconnected && "bg-red-500",
              !isConnected &&
                !isDisconnected &&
                "animate-pulse bg-amber-400"
            ]
              .filter(Boolean)
              .join(" ")}
          />
        )}
      </div>

      <p
        className={[
          "mt-3 truncate text-2xl font-bold sm:text-3xl",
          isConnected && "text-green-600",
          isDisconnected && "text-red-600",
          !status && "text-slate-900"
        ]
          .filter(Boolean)
          .join(" ")}
      >
        {value}
      </p>
    </article>
  );
}

function ArchitectureItem({ title, description }) {
  return (
    <div className="min-w-0 rounded-lg bg-slate-50 p-4">
      <p className="truncate text-sm font-semibold text-slate-900">
        {title}
      </p>

      <p className="mt-1 truncate text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}