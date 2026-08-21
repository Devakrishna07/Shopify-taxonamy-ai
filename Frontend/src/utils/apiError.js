export function getApiErrorMessage(error) {
  if (!error) {
    return "An unknown error occurred.";
  }

  if (error.response) {
    const data = error.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (data?.detail) {
      return data.detail;
    }

    if (data && typeof data === "object") {
      return Object.entries(data)
        .map(([field, message]) => {
          if (Array.isArray(message)) {
            return `${field}: ${message.join(", ")}`;
          }

          return `${field}: ${message}`;
        })
        .join(" | ");
    }

    return `Request failed with status ${error.response.status}.`;
  }

  if (error.request) {
    return "Unable to connect to the Django backend.";
  }

  return error.message || "An unexpected error occurred.";
}