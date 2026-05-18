# API Documentation

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs`

---

## Endpoints

### POST `/procurement/request`
Create a new procurement request (multipart/form-data).

**Fields:**
- `input_text` (string) — natural language description
- `file` (file, optional) — `.xlsx` or `.csv`
- `user_id` (string, default `demo_user`)

**Response 201:**
```json
{
  "request_id": "uuid",
  "parsed_items": [...],
  "status": "pending",
  "created_at": "ISO datetime"
}
```

---

### POST `/procurement/{request_id}/confirm`
Confirm (and optionally edit) extracted parameters. Starts the crawl pipeline in the background.

**Body:**
```json
{ "items": [{ "product_name": "...", "quantity": 500, ... }] }
```

---

### GET `/procurement/{request_id}/status`
Poll for pipeline progress.

**Response:**
```json
{
  "status": "crawling|matching|scoring|completed|failed",
  "progress": {
    "platforms_crawled": 3,
    "total_platforms": 4,
    "listings_found": 18,
    "clusters_created": 2
  }
}
```

---

### GET `/procurement/{request_id}/results`
Get ranked comparison results. Returns 202 if still processing.

---

### POST `/procurement/{request_id}/decision`
Record the buyer's decision to the audit log.

**Body:**
```json
{
  "action": "accept|override|re_search|reject",
  "chosen_listing_id": "uuid",
  "override_reason": "optional string"
}
```

---

### GET `/procurement/{request_id}/export?format=pdf|excel`
Download results as PDF or Excel file.
