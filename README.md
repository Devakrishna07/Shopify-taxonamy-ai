# Shopify Product Classification AI

An AI-powered product classification and taxonomy management platform designed to automatically process Shopify product data, classify products against the Shopify taxonomy, extract category-specific attributes, calculate confidence, and route uncertain results for human review.

The system consists of a **React + Vite + Tailwind CSS frontend** and a **Django REST Framework backend**, with AI inference, processing orchestration, decision management, and batch reliability built around the existing Django business modules.

---

## 🚀 Project Overview

The Shopify Product Classification AI system automates the classification of large product catalogs.

A typical workflow is:

```text
Product Source
     │
     ▼
   Imports
     │
     ▼
 Processing
     │
     ├──────────────► Shopify Taxonomy
     │
     ▼
 AI Inference
     │
     ├── Classification
     ├── Attributes
     └── Supporting Signals
     │
     ▼
 Decision & Review
     │
     ▼
   Results
     │
     ├── Auto Approved
     ├── Needs Review
     └── Manual Review
     │
     ▼
 Human Decision
```

The backend is designed to process products individually so that a failure affecting one product does not terminate the entire batch. Batch processing also supports progress tracking, retries, failure isolation, and resume-oriented execution.

---

## ✨ Key Features

### Product Import

* Import product catalogs
* Support CSV/Excel and other configured product sources
* Product-level validation
* Import-level validation
* Optional product image support
* Handling of incomplete product information

### Shopify Taxonomy

* Browse the Shopify taxonomy hierarchy
* Search taxonomy categories
* Inspect category paths
* Use the authoritative taxonomy source for classification
* Support manual category selection/reclassification

### AI Classification

* AI-powered product classification
* Primary category prediction
* Confidence score
* Alternative category predictions
* Text-only inference
* Image + text inference when an image is available

### Attribute Extraction

* Extract category-relevant product attributes
* Store attribute values
* Associate confidence scores with extracted attributes
* Display category-aware attributes in the frontend

### Review & Decision Management

Classification results are automatically routed according to confidence:

| Confidence        | Decision        |
| ----------------- | --------------- |
| `>= 0.85`         | `AUTO_APPROVED` |
| `0.60 – < 0.85`   | `NEEDS_REVIEW`  |
| `< 0.60`          | `MANUAL_REVIEW` |
| Inference failure | `FAILED`        |

These thresholds are defined by the backend decision policy.

Human reviewers can:

* Approve results
* Edit results
* Reject results
* Reclassify products
* Review alternative categories
* Compare AI predictions with human-approved outcomes

The original AI prediction is preserved when human decisions modify the final result, where supported.

### Batch Processing

Designed for large product catalogs, including representative **10,000+ product datasets**.

Features include:

* Chunked processing
* Progress tracking
* Retry handling
* Product-level failure isolation
* Permanent failure recording
* Last processed product tracking
* Resume-oriented state
* Batch summary
* Processing job status

---

# 🏗️ Architecture

## Backend

The completed backend contains ten logical capability areas:

1. **Imports**
2. **Taxonomy**
3. **Classification**
4. **Attributes**
5. **Reviews**
6. **Processing**
7. **Results**
8. **AI Inference & Multimodal Services**
9. **Decision & Review Services**
10. **Batch & Reliability Services**

Batch and reliability functionality is implemented inside the Processing capability rather than as an additional Django business application.

---

## Frontend

The frontend is built around:

* Vite
* React
* Tailwind CSS v3
* PostCSS
* Autoprefixer
* React Router
* Centralized API client
* Optional TanStack Query for caching and processing-job polling
* Vitest
* React Testing Library
* Playwright

The frontend architecture explicitly keeps backend intelligence and AI inference out of React.

---

# 📁 Project Structure

```text
Shopify Product Classification AI/
│
├── Backend/
│   ├── manage.py
│   │
│   ├── <project_config>/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── imports/
│   ├── taxonamy/
│   ├── classification/
│   ├── attributes/
│   ├── reviews/
│   ├── processing/
│   ├── results/
│   │
│   └── services/
│       ├── ai/
│       │   ├── classifier.py
│       │   ├── attribute_extractor.py
│       │   ├── image_processor.py
│       │   ├── taxonomy_matcher.py
│       │   └── schemas.py
│       │
│       └── decision/
│           ├── confidence.py
│           ├── alternatives.py
│           ├── review.py
│           └── approval.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── index.html
    ├── .env.example
    │
    └── src/
        ├── main.jsx
        ├── App.jsx
        │
        ├── routes/
        │
        ├── api/
        │   ├── client.js
        │   ├── endpoints.js
        │   ├── imports.api.js
        │   ├── processing.api.js
        │   ├── results.api.js
        │   ├── taxonomy.api.js
        │   ├── classification.api.js
        │   ├── attributes.api.js
        │   └── reviews.api.js
        │
        ├── components/
        │   ├── layout/
        │   ├── common/
        │   ├── tables/
        │   ├── status/
        │   ├── progress/
        │   └── forms/
        │
        ├── features/
        │   ├── dashboard/
        │   ├── imports/
        │   ├── taxonomy/
        │   ├── classification/
        │   ├── attributes/
        │   ├── reviews/
        │   ├── processing/
        │   ├── ai-inference/
        │   ├── decision-review/
        │   ├── batch-reliability/
        │   └── results/
        │
        ├── hooks/
        ├── context/
        ├── utils/
        ├── types/
        └── styles/
            └── index.css
```

This structure follows the supplied frontend architecture.

---

# 🔄 Processing Pipeline

Each product follows the following processing sequence:

```text
1. Import Product
        │
2. Normalize & Validate
        │
3. Build AI Product Input
        │
4. Detect Available Modalities
        │
5. Load/Search Shopify Taxonomy
        │
6. Run AI Inference
        │
7. Generate Category + Confidence + Alternatives
        │
8. Extract Attributes
        │
9. Apply Classification & Attribute Logic
        │
10. Apply Decision & Review Policy
        │
11. Persist Result
        │
12. Continue to Next Product
```

The pipeline uses available fields such as:

* Product title
* Description
* Product type
* Brand
* Image

The backend determines whether the product can use **text-only** or **image + text** inference.

---

# 🔌 API Integration

The frontend communicates with Django through REST APIs.

The API base URL is centrally configured using:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The deployment-specific API prefix should not be hardcoded inside individual feature components.

## Processing APIs

```http
GET    /processing/
POST   /processing/
GET    /processing/{id}/
POST   /processing/{id}/start/
```

Used for:

* Creating processing jobs
* Starting batches
* Monitoring processing state
* Polling progress

## Results APIs

```http
GET    /results/
GET    /results/{id}/
PATCH  /results/{id}/
PUT    /results/{id}/
POST   /results/{id}/approve/
POST   /results/{id}/reject/
POST   /results/{id}/reclassify/
```

These endpoints support result inspection and human decision workflows.

---

# 🖥️ Frontend Routes

| Route                          | Purpose             |
| ------------------------------ | ------------------- |
| `/`                            | Dashboard           |
| `/imports`                     | Import Workspace    |
| `/taxonomy`                    | Taxonomy Explorer   |
| `/processing`                  | Processing Jobs     |
| `/processing/:id`              | Batch/Job Monitor   |
| `/results`                     | Results Workspace   |
| `/results/:id`                 | Result Detail       |
| `/review`                      | Review Queue        |
| `/products/:id/classification` | Classification View |
| `/products/:id/attributes`     | Attributes View     |
| `/products/:id/signals`        | AI/Review Signals   |

These routes correspond to the planned operational frontend surfaces.

---

# 📊 Dashboard

The dashboard provides operational visibility into:

* Total imported products
* Active processing jobs
* Completed products
* Failed products
* Retry count
* Processing progress
* Auto-approved products
* Products requiring review
* Manual-review products
* Pending review queue
* Recently completed results

---

# 📝 Result Object

A typical result exposed to the frontend contains:

```json
{
  "product_id": 123,
  "category": {
    "id": 456,
    "name": "Example Category",
    "path": "Parent > Example Category"
  },
  "confidence": 0.91,
  "alternatives": [],
  "attributes": [
    {
      "name": "Material",
      "value": "Cotton",
      "confidence": 0.88
    }
  ],
  "decision": {
    "status": "AUTO_APPROVED",
    "requires_review": false,
    "reason": "Confidence above approval threshold"
  },
  "processing_status": "COMPLETED"
}
```

This reflects the suggested frontend result contract in the backend architecture.

---

# 🛡️ Error Handling & Fallbacks

The system is designed to continue processing wherever possible.

### Missing Image

Uses the text-only inference path.

### Invalid Image

Image processing failure should not terminate product processing. Text fallback is used where available.

### Missing Description

Available product signals such as title, product type and brand can still be processed.

### Missing Optional Signals

Unavailable optional fields are omitted instead of causing a fatal batch failure.

### AI Failure

The failure is recorded at product level and retry behavior is applied according to batch policy.

### Permanent Product Failure

The product is marked as failed and processing continues with subsequent products.

### Low Confidence

Alternative predictions are preserved and the result is routed to review.

---

# ⚙️ Installation

## Prerequisites

Install the following:

* Python
* Node.js
* npm
* MariaDB/MySQL or the configured Django database
* Git

---

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>

cd <PROJECT_DIRECTORY>
```

---

# 🐍 Backend Setup

Navigate to the backend:

```bash
cd Backend
```

Create a virtual environment:

### Windows

```bash
python -m venv env
```

Activate it:

```bash
env\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv env
source env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Django checks:

```bash
python manage.py check
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The backend will normally be available at:

```text
http://127.0.0.1:8000/
```

---

# ⚛️ Frontend Setup

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
.env
```

Add:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The Vite frontend will display the URL provided in the terminal.

---

# 🔗 Frontend ↔ Backend

The frontend should communicate with Django through the centralized API client.

Example:

```javascript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
```

Feature-specific API services should call the centralized client rather than making raw requests throughout React components.

Recommended API structure:

```text
src/
└── api/
    ├── client.js
    ├── endpoints.js
    ├── imports.api.js
    ├── processing.api.js
    ├── results.api.js
    ├── taxonomy.api.js
    ├── classification.api.js
    ├── attributes.api.js
    └── reviews.api.js
```

---

# 🧪 Testing

## Backend

Run Django checks:

```bash
python manage.py check
```

Run Processing tests:

```bash
python manage.py test processing
```

Run the complete backend test suite:

```bash
python manage.py test
```

The architecture recommends verifying migrations, batch APIs, retry behavior, failure isolation, review routing, and Results APIs.

## Frontend

Recommended testing stack:

```text
Vitest
React Testing Library
Playwright
```

Tests should cover:

* API transformations
* Confidence threshold mapping
* Loading states
* Empty states
* Error states
* Shared components
* Module integration
* Processing-job polling
* Results workflow
* Review workflow

---

# 🔬 End-to-End Workflow

The primary E2E workflow is:

```text
Import
  ↓
Create Processing Job
  ↓
Start Job
  ↓
Poll Job Status
  ↓
Process Products
  ↓
View Results
  ↓
Open Review Queue
  ↓
Approve / Edit / Reject / Reclassify
  ↓
Refresh Results & Batch Summary
```

The frontend architecture defines this as the principal integration path.

---

# 📈 Large-Batch Processing

The architecture is designed around large product catalogs.

For a representative 10,000-product execution, the ProcessingJob tracks fields such as:

```text
id
job_type
status
import_id
total_items
completed_items
failed_items
max_retries
retry_count
last_processed_id
error_message
progress
started_at
completed_at
```

The backend explicitly supports chunking, progress tracking, retries, failure isolation and resume-oriented state.

---

# 🧠 Architecture Principles

The project follows these core principles:

* Preserve existing Django business modules.
* Keep AI inference behind a replaceable service interface.
* Do not duplicate AI inference logic in the frontend.
* Keep normalization and validation inside Processing.
* Keep batch reliability functionality inside Processing.
* Preserve original AI predictions after human corrections.
* Isolate individual product failures.
* Use Django REST APIs as the frontend/backend boundary.

These principles are explicitly defined in the completed backend architecture.

---

# 🗺️ Development Roadmap

The frontend implementation follows an agile module-based progression:

```text
Sprint 0  → Foundation & API
Sprint 1  → Imports
Sprint 2  → Taxonomy + Classification
Sprint 3  → Attributes + Reviews
Sprint 4  → Processing
Sprint 5  → Batch & Reliability
Sprint 6  → Results
Sprint 7  → Decision & Review
Sprint 8  → AI / Multimodal
Sprint 9  → E2E QA & Acceptance
```

The frontend architecture defines these sprints and their respective backend integration requirements.

---

# ✅ Definition of Done

A module is considered complete when:

* The real backend endpoint is exercised.
* Loading, empty, success and error states are implemented.
* API calls use the centralized API client.
* Backend responses are converted into stable frontend view models.
* Backend fallback behavior is represented in the UI.
* Module integration tests cover the main success path.
* Backend business logic is not duplicated in React.
* AI inference is not duplicated in the frontend.

---

# 📌 Current Completion Criteria

The completed system should provide:

* Product import
* Shopify taxonomy browsing/search
* AI classification
* Confidence scoring
* Alternative categories
* Category-aware attributes
* Image and text processing
* Missing-data fallbacks
* Manual review
* Result approval/edit/rejection/reclassification
* Batch processing
* Retry handling
* Failure isolation
* Processing progress
* Human-vs-AI decision state
* Frontend/backend API integration

The backend architecture marks these core requirements as satisfied or designed/supported, with final acceptance activity focused on end-to-end validation, especially representative 10,000+ product execution and failure/retry/API review flows.

---

# 🚧 Production Validation

Before production deployment, validate:

```text
[ ] Django system checks pass
[ ] All migrations are applied
[ ] Import workflow works
[ ] Taxonomy APIs work
[ ] Classification workflow works
[ ] Attribute extraction works
[ ] ProcessingJob creation works
[ ] ProcessingJob start works
[ ] Processing status polling works
[ ] Batch progress is accurate
[ ] Retry behavior works
[ ] Product failures are isolated
[ ] Results APIs work
[ ] Review actions work
[ ] Approval/reclassification works
[ ] Original AI prediction is preserved
[ ] Text-only inference works
[ ] Image + text inference works
[ ] 10,000+ product validation is completed
[ ] Frontend E2E tests pass
```

---

# 🔐 Configuration

Do not commit sensitive configuration to GitHub.

Use environment variables for:

* Database credentials
* Django secret key
* AI service credentials
* External API credentials
* Storage credentials
* Frontend API base URL
* Production configuration

Example:

```env
# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

For production:

```env
VITE_API_BASE_URL=https://your-api-domain.example
```

---

# 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Implement the feature.
4. Run backend and frontend tests.
5. Verify API integration.
6. Commit your changes.

```bash
git add .
git commit -m "Add your feature"
```

7. Push the branch.

```bash
git push origin feature/your-feature
```

8. Open a Pull Request.

---

# 📄 License

Add the project's applicable license here.

Example:

```text
MIT License
```

---

# 👨‍💻 Project

**Shopify Product Classification AI**

AI-assisted product classification and taxonomy management platform using:

```text
React
Vite
Tailwind CSS
Django
Django REST Framework
MariaDB / MySQL
AI Inference
Shopify Taxonomy
Batch Processing
Human Review
```

The architecture is based on the completed backend design and the corresponding frontend architecture and sprint plan dated **21 August 2026**.
