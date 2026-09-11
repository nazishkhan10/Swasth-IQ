# Database Schema & Data Models

The database is built on **SQLite** with **SQLAlchemy ORM**.

## Core Entities & Tables

### 1. `users`
- `id` (INTEGER, PK)
- `email` (VARCHAR, Unique, Indexed)
- `name` (VARCHAR)
- `password_hash` (VARCHAR)
- `created_at` (DATETIME)

### 2. `reports`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK -> users.id)
- `filename` (VARCHAR)
- `original_filename` (VARCHAR)
- `file_path` (VARCHAR)
- `file_type` (VARCHAR)
- `file_size` (INTEGER)
- `status` (VARCHAR: pending, ocr_completed, parsed, validated, analyzed)
- `created_at` (DATETIME)

### 3. `patient_metadata`
- `id` (INTEGER, PK)
- `report_id` (INTEGER, FK -> reports.id)
- `patient_name` (VARCHAR)
- `age` (VARCHAR)
- `gender` (VARCHAR)
- `accession_number` (VARCHAR)
- `referred_by` (VARCHAR)
- `sample_date` (VARCHAR)

### 4. `validated_medical_values`
- `id` (INTEGER, PK)
- `report_id` (INTEGER, FK -> reports.id)
- `parameter_name` (VARCHAR)
- `parameter_code` (VARCHAR)
- `validated_value` (FLOAT)
- `raw_value` (VARCHAR)
- `normalized_unit` (VARCHAR)
- `reference_low` (FLOAT)
- `reference_high` (FLOAT)
- `status` (VARCHAR: NORMAL, LOW, HIGH, CRITICAL_LOW, CRITICAL_HIGH)
- `is_converted` (BOOLEAN)
- `converted_value` (FLOAT)
- `canonical_unit` (VARCHAR)
- `conversion_factor` (FLOAT)
- `ocr_confidence` (FLOAT)
- `validation_trace` (TEXT)

### 5. `chat_messages` & `chat_executions`
- `id` (INTEGER, PK)
- `report_id` (INTEGER, FK -> reports.id)
- `role` (VARCHAR: user, assistant)
- `content` (TEXT)
- `prompt_version` (VARCHAR)
- `prompt_hash` (VARCHAR)
- `created_at` (DATETIME)
