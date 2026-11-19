# API Testing & Ingestion Documentation

This document maintains references to the test plan, Google Sheets test execution report, and Postman automated testing suite for the **Shopify Taxonomy AI** backend.

---

## 1. Google Sheets Test Plan & Live Execution Report

All test scenarios, acceptance criteria, and live execution results are stored and updated in the Google Sheet below:

🔗 **Google Sheet**: [Shopify Taxonomy AI - Backend API Test Plan & Report](https://docs.google.com/spreadsheets/d/1mIBvF2hn9e8DN89aOO79QSLCH-WtqjpFcqE3Jo-o1ig/edit)
* **Spreadsheet ID**: `1mIBvF2hn9e8DN89aOO79QSLCH-WtqjpFcqE3Jo-o1ig`

### Sheets Included:
1. **`Test_Summary`**: Live execution scorecard:
   - **Total Test Cases Executed**: `10`
   - **Passed**: `10 (100%)`
   - **Failed**: `0`
   - **Assertions Passed**: `19 / 19`
   - **Average Response Latency**: `28ms`
2. **`API_Test_Cases`**: Industrial standard test matrix populated with live run results (`Actual Status Code`, `Actual Response Body`, `Status: PASSED`, `Execution Time (ms)`, and assertion details).
3. **`Postman_Environment_Config`**: Reference matrix for Postman variables (`baseUrl`, `import_id`, `clientOrigin`).

---

## 2. Postman Collection & Test Artifacts

The Postman collections and sample test fixtures are preserved directly in the repository:

* 📁 **Collection**: [`postman/Shopify_Taxonomy_Imports.postman_collection.json`](file:///c:/Users/devap/Documents/my%20websites/Shopify-taxonamy-ai/postman/Shopify_Taxonomy_Imports.postman_collection.json)
* 📁 **Environment**: [`postman/Shopify_Taxonomy_Local.postman_environment.json`](file:///c:/Users/devap/Documents/my%20websites/Shopify-taxonamy-ai/postman/Shopify_Taxonomy_Local.postman_environment.json)
* 📁 **Test Fixtures**:
  - Valid XLSX: [`Backend/test_samples/products_valid.xlsx`](file:///c:/Users/devap/Documents/my%20websites/Shopify-taxonamy-ai/Backend/test_samples/products_valid.xlsx)
  - Valid CSV: [`Backend/test_samples/products_valid.csv`](file:///c:/Users/devap/Documents/my%20websites/Shopify-taxonamy-ai/Backend/test_samples/products_valid.csv)
  - Missing Title XLSX: [`Backend/test_samples/missing_title.xlsx`](file:///c:/Users/devap/Documents/my%20websites/Shopify-taxonamy-ai/Backend/test_samples/missing_title.xlsx)
  - Invalid File: [`Backend/test_samples/invalid_file.pdf`](file:///c:/Users/devap/Documents/my%20websites/Shopify-taxonamy-ai/Backend/test_samples/invalid_file.pdf)

---

## 3. How to Run the Tests

### Option A: Automated CLI Run via Newman
Run the automated test runner directly from your terminal:

```bash
newman run postman/Shopify_Taxonomy_Imports.postman_collection.json -e postman/Shopify_Taxonomy_Local.postman_environment.json -r cli
```

### Option B: Using Postman Desktop App
1. Open the Postman Desktop App.
2. Click **Import** in the upper-left corner.
3. Select `postman/Shopify_Taxonomy_Imports.postman_collection.json` and `postman/Shopify_Taxonomy_Local.postman_environment.json`.
4. Select the **Shopify Taxonomy AI - Local Environment**.
5. Click **Run Collection** to execute all tests with assertions.

---

## 4. API Response Envelope Specification

All endpoints follow the standardized response contract:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Operation successful.",
  "data": {},
  "meta": {
    "requestId": "req_01JXYZ9876543210",
    "timestamp": "2026-11-19T16:11:00.456Z",
    "pagination": {
      "page": 1,
      "perPage": 20,
      "totalItems": 142,
      "totalPages": 8,
      "hasNextPage": true,
      "hasPrevPage": false,
      "nextCursor": null
    }
  }
}
```
