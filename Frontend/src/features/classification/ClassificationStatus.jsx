const STATUS_CONFIG = {
  CLASSIFIED: {
    label: "Classified",
    className:
      "bg-blue-100 text-blue-700",
  },

  REVIEW: {
    label: "Needs Review",
    className:
      "bg-yellow-100 text-yellow-700",
  },

  APPROVED: {
    label: "Approved",
    className:
      "bg-green-100 text-green-700",
  },

  REJECTED: {
    label: "Rejected",
    className:
      "bg-red-100 text-red-700",
  },
};

export default function ClassificationStatus({ status }) {
  const config =
    STATUS_CONFIG[status] || {
      label: status || "Unknown",
      className: "bg-gray-100 text-gray-700",
    };

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${config.className}`}
    >
      {config.label}
    </span>
  );
}