/*
 * ============================================================================
 * MYSQL INSERT - ARCHITECTURAL TEMPLATE & DATA MUTATION CHEAT SHEET
 * ============================================================================
 * Target Table: enterprise_employees (emp_id PK, national_id UNIQUE)
 */

/* * ----------------------------------------------------------------------------
 * 1. STANDARD SINGLE-ROW INSERT
 * ----------------------------------------------------------------------------
 * Best Practice: ALWAYS specify the target columns. Relying on positional 
 * insertion (omitting column names) will break your application instantly 
 * if a new column is added to the table via ALTER TABLE.
 */
INSERT INTO enterprise_employees 
    (national_id, full_name, contract_type, base_salary, birth_date)
VALUES 
    ('29905051234567', 'System Admin', 'FULL_TIME', 8500.00, '1999-05-05');

/* * ----------------------------------------------------------------------------
 * 2. BULK (MULTI-ROW) INSERT
 * ----------------------------------------------------------------------------
 * SIBLING PERFORMANCE:
 * Executing 1,000 single INSERT statements requires 1,000 network round-trips 
 * and 1,000 transaction commits.
 * Executing ONE bulk INSERT with 1,000 rows reduces network overhead drastically 
 * and commits everything in a single transaction. Time complexity drops significantly.
 * * Engine Limit: Bounded by the 'max_allowed_packet' configuration in MySQL 
 * (Default is usually 64MB). Do not exceed this per single query.
 */
INSERT INTO enterprise_employees 
    (national_id, full_name, contract_type, base_salary, birth_date)
VALUES 
    ('29901010000001', 'Engineer A', 'FULL_TIME', 9000.00, '1999-01-01'),
    ('29901010000002', 'Engineer B', 'CONTRACTOR', 7500.00, '1999-01-02'),
    ('29901010000003', 'Engineer C', 'PART_TIME', 4000.00, '1999-01-03');

/* * ----------------------------------------------------------------------------
 * 3. UPSERT (INSERT ... ON DUPLICATE KEY UPDATE)
 * ----------------------------------------------------------------------------
 * Architectural Purpose: Resolves 'Race Conditions' and 'Check-then-Act' flaws.
 * Instead of querying "Does this ID exist?" -> (If yes: UPDATE, If no: INSERT)
 * within the application (which requires two round-trips and fails under concurrency), 
 * let the database engine handle the conflict atomically.
 *
 * Trigger: Fires when an inserted row causes a duplicate value in a PRIMARY KEY 
 * or a UNIQUE INDEX.
 */
INSERT INTO enterprise_employees 
    (national_id, full_name, contract_type, base_salary, birth_date)
VALUES 
    ('29905051234567', 'System Admin', 'FULL_TIME', 8500.00, '1999-05-05')
ON DUPLICATE KEY UPDATE
    /* VALUES() function retrieves the value you *attempted* to insert */
    full_name = VALUES(full_name),
    base_salary = VALUES(base_salary),
    updated_at = CURRENT_TIMESTAMP;

/* * ----------------------------------------------------------------------------
 * 4. INSERT IGNORE
 * ----------------------------------------------------------------------------
 * SIBLING USAGE:
 * Attempts to insert. If a duplicate key violation or data conversion error 
 * occurs, it silently IGNORES the row and downgrades the error to a warning.
 * * Danger: It ignores ALL errors, including data truncation (e.g., trying to 
 * insert a 200-char string into a 150-char column). Use strictly for deduplication 
 * during large data imports, never for standard business logic.
 */
INSERT IGNORE INTO enterprise_employees 
    (national_id, full_name, contract_type, base_salary, birth_date)
VALUES 
    ('29905051234567', 'System Admin', 'FULL_TIME', 8500.00, '1999-05-05');

/* * ----------------------------------------------------------------------------
 * 5. REPLACE INTO (The Dangerous Sibling)
 * ----------------------------------------------------------------------------
 * Mechanism: If a conflict occurs, it DELETES the existing row entirely, 
 * then INSERTS the new row.
 * * Severe Architectural Flaws:
 * 1. It physically destroys and recreates the row, causing new auto-increment IDs.
 * 2. It triggers ON DELETE CASCADE foreign keys, potentially wiping out child rows 
 * in other tables silently.
 * 3. Rebuilds all indexes for that row twice (Delete + Insert).
 * * Verdict: NEVER use REPLACE INTO. ALWAYS use ON DUPLICATE KEY UPDATE.
 */
REPLACE INTO enterprise_employees 
    (national_id, full_name, contract_type, base_salary, birth_date)
VALUES 
    ('29905051234567', 'System Admin', 'FULL_TIME', 8500.00, '1999-05-05');

/* * ----------------------------------------------------------------------------
 * 6. INSERT ... SELECT (Data Migration)
 * ----------------------------------------------------------------------------
 * Usage: Moving large chunks of data from one table to another entirely inside 
 * the database engine without moving data to the application layer (Backend).
 * Extremely fast.
 */
INSERT INTO enterprise_employees 
    (national_id, full_name, contract_type, base_salary, birth_date)
SELECT 
    temp.nat_id, 
    temp.name, 
    'CONTRACTOR', 
    temp.salary, 
    temp.dob
FROM legacy_hr_import_table AS temp
WHERE temp.is_processed = FALSE;
