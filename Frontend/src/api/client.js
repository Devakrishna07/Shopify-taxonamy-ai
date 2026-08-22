const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api"
).replace(/\/+$/, "");


/**
 * Build the final API URL.
 */
function buildUrl(endpoint, params = {}) {
  const normalizedEndpoint = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;

  const url = new URL(
    `${API_BASE_URL}${normalizedEndpoint}`
  );

  Object.entries(params || {}).forEach(
    ([key, value]) => {
      // Do not send empty filter values.
      if (
        value !== undefined &&
        value !== null &&
        value !== ""
      ) {
        url.searchParams.set(
          key,
          String(value)
        );
      }
    }
  );

  return url.toString();
}


/**
 * Convert backend errors into a useful message.
 */
function getErrorMessage(data, statusCode) {
  if (
    typeof data === "object" &&
    data !== null
  ) {
    return (
      data.detail ||
      data.message ||
      data.error ||
      data.errors ||
      `Request failed with status ${statusCode}`
    );
  }

  if (data) {
    return data;
  }

  return `Request failed with status ${statusCode}`;
}


/**
 * Main HTTP request function.
 */
async function request(
  endpoint,
  options = {}
) {
  const {
    params = {},
    body,
    headers: customHeaders = {},
    ...fetchOptions
  } = options;

  const url = buildUrl(
    endpoint,
    params
  );

  const isFormData =
    body instanceof FormData;

  const headers = {
    ...(isFormData
      ? {}
      : {
          "Content-Type":
            "application/json",
        }),
    ...customHeaders,
  };

  console.log(
    "[API REQUEST]",
    fetchOptions.method || "GET",
    url
  );

  const response = await fetch(
    url,
    {
      ...fetchOptions,
      headers,
      body,
    }
  );

  let data = null;

  const contentType =
    response.headers.get(
      "content-type"
    );

  if (
    contentType?.includes(
      "application/json"
    )
  ) {
    data = await response.json();
  } else {
    const text =
      await response.text();

    data = text || null;
  }

  if (!response.ok) {
    const errorMessage =
      getErrorMessage(
        data,
        response.status
      );

    const error =
      new Error(errorMessage);

    error.status =
      response.status;

    error.data = data;

    error.url = url;

    console.error(
      "[API ERROR]",
      response.status,
      url,
      data
    );

    throw error;
  }

  console.log(
    "[API RESPONSE]",
    response.status,
    url
  );

  return data;
}


/**
 * API client.
 */
export const apiClient = {

  get(
    endpoint,
    options = {}
  ) {
    return request(
      endpoint,
      {
        ...options,
        method: "GET",
      }
    );
  },


  post(
    endpoint,
    body = undefined,
    options = {}
  ) {
    let requestBody = body;

    /*
     * FormData must be sent directly.
     *
     * JSON objects must be stringified.
     */
    if (
      body !== undefined &&
      body !== null &&
      !(body instanceof FormData) &&
      typeof body === "object"
    ) {
      requestBody =
        JSON.stringify(body);
    }

    return request(
      endpoint,
      {
        ...options,
        method: "POST",
        body: requestBody,
      }
    );
  },


  patch(
    endpoint,
    body = {},
    options = {}
  ) {
    return request(
      endpoint,
      {
        ...options,
        method: "PATCH",
        body:
          body instanceof FormData
            ? body
            : JSON.stringify(body),
      }
    );
  },


  put(
    endpoint,
    body = {},
    options = {}
  ) {
    return request(
      endpoint,
      {
        ...options,
        method: "PUT",
        body:
          body instanceof FormData
            ? body
            : JSON.stringify(body),
      }
    );
  },


  delete(
    endpoint,
    options = {}
  ) {
    return request(
      endpoint,
      {
        ...options,
        method: "DELETE",
      }
    );
  },
};


export default apiClient;