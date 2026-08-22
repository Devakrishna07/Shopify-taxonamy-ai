export const ACCEPTED_FILE_TYPES = [
  ".csv",
  ".xlsx",
];

export const MAX_FILE_SIZE = 20 * 1024 * 1024;

export function validateSelectedFile(file) {
  const errors = [];

  if (!file) {
    errors.push("Please select a file.");
    return errors;
  }

  const fileName = file.name.toLowerCase();

  const validExtension = ACCEPTED_FILE_TYPES.some(
    (extension) => fileName.endsWith(extension)
  );

  if (!validExtension) {
    errors.push(
      "Only CSV and XLSX files are supported."
    );
  }

  if (file.size === 0) {
    errors.push("The selected file is empty.");
  }

  if (file.size > MAX_FILE_SIZE) {
    errors.push(
      "The selected file exceeds the 20 MB limit."
    );
  }

  return errors;
}

export function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) {
    return "0 Bytes";
  }

  const units = [
    "Bytes",
    "KB",
    "MB",
    "GB",
  ];

  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );

  const value =
    bytes / Math.pow(1024, index);

  return `${value.toFixed(
    index === 0 ? 0 : 2
  )} ${units[index]}`;
}

export function normalizeImportResponse(response) {
  return {
    id: response?.id ?? null,

    fileName:
      response?.file_name ?? "",

    status:
      response?.status ?? "UNKNOWN",

    totalRows:
      response?.total_rows ?? 0,

    processedRows:
      response?.processed_rows ?? 0,

    failedRows:
      response?.failed_rows ?? 0,

    createdAt:
      response?.created_at ?? null,

    completedAt:
      response?.completed_at ?? null,

    error:
      response?.error ?? null,
  };
}