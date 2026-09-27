# Architecture: InspectionPro

## 1. Purpose

InspectionPro is designed as a modular web application for building and structure inspections under the workflow described in GOST 31937-2024.

The architecture goal for MVP is:

1. Keep inspection data structurally consistent from object card to final report.
2. Separate field data capture, expert review, and approved client-facing output.
3. Make future additions possible without rewriting the core:
   offline mode, monitoring, analytics, BIM/IFC, AI assistant, multi-tenant support.

## 2. Architecture style

For MVP we use a modular monolith with clear domain boundaries:

- `frontend`: React SPA
- `backend`: Django + Django REST Framework API
- `postgres`: primary relational database
- `redis`: background queue / cache
- `celery`: async jobs for reports, notifications, future heavy processing
- `nginx`: reverse proxy and static/media gateway

This is intentionally not microservices yet. The domain is broad, but the operational complexity of microservices would slow MVP delivery. We keep domains isolated at code level so they can be extracted later if needed.

## 3. High-level system context

```text
[Engineer / Expert / Manager / Client]
                 |
                 v
          [React Frontend SPA]
                 |
                 v
           [Nginx Reverse Proxy]
                 |
                 v
      [Django REST API - Modular Monolith]
        |         |          |         |
        v         v          v         v
   [PostgreSQL] [Redis] [Celery] [Media Storage]
```

## 4. Core architectural principles

### 4.1 Single source of truth

All key entities are linked around:

- `BuildingObject`
- `InspectionProject`
- `StructuralElement`
- `Defect`
- `Measurement`
- `Report`

Reports are generated from structured data, not maintained as independent free-form documents.

### 4.2 Domain separation

Each business area lives in its own backend app and frontend feature module.

### 4.3 Workflow-driven model

The system must reflect the real inspection lifecycle:

1. Object
2. Inspection project
3. Technical task
4. Work program
5. Elements registry
6. Field inspection data
7. Expert review
8. Approved report
9. Historical archive / future monitoring

### 4.4 Auditability

Changes to categories, approvals, report states, and critical records are logged.

### 4.5 Role-based visibility

Client users never access draft or internal engineering data unless explicitly allowed by business rules.

## 5. Domain module map

## 5.1 Backend bounded modules

### `users`

Responsibilities:

- authentication
- JWT tokens
- user management
- roles and permissions
- user profile state

### `objects`

Responsibilities:

- building/structure card
- object metadata
- object attachments
- object history entry points

### `inspections`

Responsibilities:

- inspection project
- project status workflow
- technical task
- work program
- team assignment

### `elements`

Responsibilities:

- full registry of structural elements
- mandatory evaluation of each core element
- per-element condition summary
- linkage to defects, photos, measurements

### `defects`

Responsibilities:

- defect records
- damage classification
- preliminary/final category linkage
- engineering recommendations

### `measurements`

Responsibilities:

- instrument measurements
- measurement methods and devices
- value history inside project context

### `reports`

Responsibilities:

- report section assembly
- DOCX/PDF generation
- report versions
- review/approval workflow

### `dictionaries`

Responsibilities:

- system dictionaries
- predefined values for forms and reports
- admin-managed reference data

### `files`

Responsibilities:

- file metadata
- upload linkage
- media ownership
- future versioning rules

### `audit`

Responsibilities:

- audit log
- critical state transitions
- actor tracking

### `notifications`

Responsibilities:

- in-app notifications
- event-driven user alerts
- future email delivery

## 5.2 Frontend feature map

### `app`

- app bootstrap
- router
- auth provider
- global API client setup

### `pages`

- route-level pages

### `features`

- auth
- objects
- inspections
- elements
- defects
- measurements
- reports
- dashboard

### `widgets`

- reusable composed UI blocks:
  stats, filters, tables, activity cards, upload panels

### `shared`

- UI kit adapters
- types
- API helpers
- validation schemas
- formatters

## 6. Repository structure

```text
InspectionPro/
  docs/
    architecture.md
  backend/
    config/
    apps/
      users/
      objects/
      inspections/
      elements/
      defects/
      measurements/
      reports/
      dictionaries/
      audit/
      files/
      notifications/
  frontend/
    src/
      app/
      pages/
      features/
      widgets/
      shared/
  nginx/
```

## 7. Domain model relationships

```text
BuildingObject
  └── InspectionProject
        ├── TechnicalTask
        ├── WorkProgram
        ├── StructuralElement
        │     ├── Defect
        │     ├── Measurement
        │     └── InspectionPhoto
        ├── ProjectFile
        ├── Report
        ├── AuditLog
        └── Notification events
```

### Key relationship rules

1. One object has many inspection projects.
2. One project has many structural elements.
3. One structural element may have zero or many defects.
4. One structural element must still have an inspection evaluation record even if no defects are found.
5. Photos can belong to object, project, element, defect, or measurement context.
6. Final report references only approved or included records.

## 8. Mandatory inspection coverage model

This PRD has an important architectural requirement: not only defects but all key elements must be evaluated.

For that reason the element subsystem should not be modeled as optional metadata. It must be a first-class workflow entity.

Recommended design:

- `StructuralElement`: the inspected unit
- `ElementInspection`: evaluation record for that unit in a project
- `Defect`: optional child records linked to the element

For MVP, this can still be implemented inside a single `elements` domain if we want to keep schema simpler, but logically we must preserve two ideas:

1. the element exists in the inspection registry
2. the element inspection result exists even when no defect exists

Minimal rule:

- every required element group in a project must have at least one evaluation record before project submission to review

## 9. Status workflows

## 9.1 Project status

```text
Draft -> Planned -> In Progress -> Review -> Approved -> Archived
```

Rules:

- only Manager/Admin can move into `Planned`
- Engineers work mainly in `In Progress`
- Expert/Admin can move `Review -> Approved`
- Approved projects become read-only for most business fields

## 9.2 Report status

```text
Draft -> Generated -> On Review -> Approved -> Archived
```

## 9.3 Defect lifecycle

```text
Draft -> Confirmed -> Included in Report -> Archived
```

Future monitoring can extend this with:

- new
- unchanged
- progressing
- resolved

## 10. Permission model

| Role | Main responsibility | Access profile |
| ---- | ------------------- | -------------- |
| Admin | platform control | full access |
| Manager | project coordination | objects, projects, assignments, reporting visibility |
| Engineer | field data entry | elements, defects, measurements, photos, draft reports |
| Expert | validation and approval | review, categories, conclusions, approvals |
| Client | approved output only | own approved reports and limited statuses |

Permission strategy:

- coarse-grained by role
- refined by object/project ownership or assignment
- refined by record state, especially approved vs draft

## 11. API architecture

API style:

- REST for CRUD and workflow endpoints
- OpenAPI-first documentation via `drf-spectacular`
- consistent pagination, filtering, and validation errors

Recommended API grouping:

```text
/api/auth/
/api/users/
/api/objects/
/api/projects/
/api/projects/{id}/technical-task/
/api/projects/{id}/work-program/
/api/projects/{id}/elements/
/api/projects/{id}/defects/
/api/projects/{id}/measurements/
/api/projects/{id}/photos/
/api/projects/{id}/reports/
/api/dictionaries/
/api/audit/
/api/notifications/
```

Design notes:

1. Prefer nested endpoints for project-scoped resources in list/create actions.
2. Keep detail endpoints flat for direct access:
   `/api/elements/{id}/`, `/api/defects/{id}/`.
3. Use explicit workflow actions for state transitions:
   `submit-review`, `approve`, `archive`.

## 12. Data architecture

PostgreSQL is the main operational store.

### Data categories

1. Master data:
   users, dictionaries, object cards
2. Transactional inspection data:
   projects, elements, defects, measurements, files
3. Document outputs:
   reports, report versions
4. Audit data:
   logs, approval trail

### Storage notes

- files should be stored outside the database
- database stores metadata and relations
- use UUIDs for external-facing identifiers if public API exposure is expected
- soft delete is preferable for business-critical entities like reports and logs

## 13. File and media architecture

MVP approach:

- uploaded binary files stored on local volume in Docker environment
- metadata stored in DB

File attachment model should support:

- owner type
- owner id
- category
- original filename
- content type
- size
- uploaded_by
- created_at

Planned evolution:

- move media to S3/MinIO-compatible storage
- image compression pipeline
- EXIF extraction
- markup overlays

## 14. Report generation architecture

Report generation should be asynchronous.

Flow:

1. User edits report inputs
2. API validates project completeness
3. Celery task assembles structured context
4. Report generator builds DOCX
5. PDF is generated from DOCX or HTML pipeline
6. Files are attached to `Report`
7. User is notified when generation finishes

Reason:

- report generation can be heavy
- 100-page report target must not block API request threads

## 15. Frontend architecture

Recommended frontend pattern:

- React SPA
- route-based pages
- domain-driven feature folders
- TanStack Query for server state
- React Hook Form + Zod for forms
- Zustand only for lightweight client UI state if needed

### State split

1. Server state:
   objects, projects, defects, reports, dictionaries
2. Form state:
   object forms, inspection forms, defect forms
3. UI state:
   dialogs, filters, local table preferences
4. Auth state:
   current user, tokens, role-aware navigation

### Frontend priorities for MVP

- fast navigation between object and project context
- dense data-entry forms
- attachment-friendly UX
- clear workflow/status visibility
- printable report preview

## 16. Validation and business rules

Key rules to encode early:

1. A project cannot go to review if mandatory inspection sections are incomplete.
2. Required element groups must be evaluated even if no defects exist.
3. Final condition category must be expert-confirmed before approval.
4. Client access is limited to approved materials only.
5. Report generation should validate inclusion consistency:
   object data, project data, elements, defects, photos, measurements.

## 17. Observability and audit

For MVP:

- structured backend logging
- request ID support
- audit log for business actions
- error tracking hooks prepared for future Sentry integration

Audit-critical actions:

- login/logout
- create/update/delete of core records
- category changes
- project state transitions
- report generation and approval
- file uploads and removals

## 18. Security architecture

Minimum security baseline:

- JWT access + refresh tokens
- password hashing via Django standards
- role-based permissions in DRF
- HTTPS in production
- file upload validation
- object-level access checks
- approval-state-based data visibility

## 19. MVP implementation order

### Phase 1: platform foundation

- backend project setup
- frontend project setup
- Docker Compose
- PostgreSQL / Redis wiring
- authentication / roles
- OpenAPI

### Phase 2: core object and project flow

- objects
- projects
- technical task
- work program

### Phase 3: inspection data capture

- structural elements
- full element evaluation
- defects
- measurements
- photos/files

### Phase 4: review and reports

- category approval
- workflow transitions
- report builder
- DOCX/PDF generation

### Phase 5: management and polish

- dashboard
- notifications
- audit UI
- filtering/search optimization

## 20. Architecture decisions for next build step

When we start implementation, these decisions should remain fixed unless business needs change:

1. Use modular monolith, not microservices.
2. Keep project as the central aggregate for inspection workflow.
3. Treat element evaluation as mandatory first-class data, not only defects.
4. Generate reports asynchronously.
5. Keep client access separated from internal engineering workspace.
6. Build repository structure for future scale, but optimize current delivery for MVP speed.
