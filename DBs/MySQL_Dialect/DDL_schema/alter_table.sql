/*
 * ============================================================================
 * MYSQL ALTER TABLE - ARCHITECTURAL TEMPLATE & CHEAT SHEET
 * ============================================================================
 * WARNING: Executing ALTER TABLE on multi-gigabyte tables can block production.
 * Always define ALGORITHM and LOCK explicitly to prevent accidental table locks.
 */

/* * ----------------------------------------------------------------------------
 * 1. ONLINE DDL CONTROL (The most critical aspect for a Systems Engineer)
 * ----------------------------------------------------------------------------
 * SIBLINGS (ALGORITHM):
 * 1. INSTANT (MySQL 8.0.12+): Modifies metadata only in the data dictionary. 
 * Time complexity is O(1). Does not touch the physical rows. Always prefer this.
 * 2. INPLACE: Modifies the table without creating a temporary table, but may 
 * rebuild the B-Tree. Allows concurrent DML (Inserts/Updates).
 * 3. COPY: The legacy method. Creates a new table, copies all rows, drops the 
 * old table. Time complexity is O(N). Blocks all writes. NEVER use in production.
 *
 * SIBLINGS (LOCK):
 * 1. NONE: Allows concurrent reads and writes.
 * 2. SHARED: Allows concurrent reads, but blocks writes.
 * 3. EXCLUSIVE: Blocks both reads and writes.
 */

-- Example of a safe, non-blocking metadata alteration
ALTER TABLE enterprise_employees
    ALTER COLUMN base_salary SET DEFAULT 1000.00,
    ALGORITHM = INSTANT,
    LOCK = NONE;

/* * ----------------------------------------------------------------------------
 * 2. MODIFYING COLUMNS (ADD, DROP, CHANGE, MODIFY)
 * ----------------------------------------------------------------------------
 */

-- ADD SIBLINGS:
-- By default, ADD appends the column to the physical end of the row.
-- You can use 'FIRST' or 'AFTER column_name' to dictate logical position,
-- but doing so might force ALGORITHM=INPLACE instead of INSTANT.
ALTER TABLE enterprise_employees
    ADD COLUMN phone_number VARCHAR(15) NULL AFTER full_name;

-- MODIFY vs CHANGE:
-- 1. MODIFY: Changes the data type or constraints of an existing column.
-- 2. CHANGE: Can rename the column AND change its data type simultaneously.

-- Using MODIFY (Keeping the same name)
ALTER TABLE enterprise_employees
    MODIFY COLUMN full_name VARCHAR(255) NOT NULL;

-- Using CHANGE (Renaming 'biography' to 'resume_text')
ALTER TABLE enterprise_employees
    CHANGE COLUMN biography resume_text LONGTEXT NULL;

-- DROP COLUMN:
-- Warning: Dropping a column physically rebuilds the table (prior to MySQL 8.0.29).
ALTER TABLE enterprise_employees
    DROP COLUMN contract_type;

/* * ----------------------------------------------------------------------------
 * 3. MANAGING INDEXES & KEYS (Performance Tuning)
 * ----------------------------------------------------------------------------
 */

-- ADDING INDEXES:
-- Building an index uses ALGORITHM=INPLACE but requires CPU and Disk I/O.
ALTER TABLE enterprise_employees
    ADD UNIQUE INDEX uidx_phone (phone_number),
    ADD INDEX idx_name_salary (full_name, base_salary),
    -- FULLTEXT is specifically for natural language search strings.
    ADD FULLTEXT INDEX fidx_resume (resume_text);

-- DROPPING INDEXES:
-- Fast metadata operation (ALGORITHM=INSTANT in modern MySQL).
ALTER TABLE enterprise_employees
    DROP INDEX idx_department_salary;

/* * ----------------------------------------------------------------------------
 * 4. MANAGING FOREIGN KEYS
 * ----------------------------------------------------------------------------
 * Dropping or adding foreign keys requires ALGORITHM=INPLACE.
 * The constraint name MUST be known (which is why we explicitly named it 
 * in the CREATE TABLE template).
 */

ALTER TABLE enterprise_employees
    DROP FOREIGN KEY fk_employee_department;

ALTER TABLE enterprise_employees
    ADD CONSTRAINT fk_employee_dept_new 
    FOREIGN KEY (department_id) REFERENCES new_departments(id) 
    ON DELETE RESTRICT 
    ON UPDATE CASCADE;

/* * ----------------------------------------------------------------------------
 * 5. TABLE ENGINE & CHARACTER SET UPGRADES
 * ----------------------------------------------------------------------------
 */

-- Changing the engine rebuilds the entire table physically (ALGORITHM=COPY).
-- Do this during maintenance windows only.
ALTER TABLE enterprise_employees
    ENGINE = InnoDB;

-- CONVERT TO CHARACTER SET vs DEFAULT CHARACTER SET:
-- 1. CONVERT TO: Physically rebuilds the table and converts all existing 
--    string columns to the new charset. Very slow.
-- 2. DEFAULT: Only changes the default for future added columns. Very fast.
ALTER TABLE enterprise_employees
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

/* * ----------------------------------------------------------------------------
 * 6. RENAMING THE TABLE
 * ----------------------------------------------------------------------------
 */
ALTER TABLE enterprise_employees
    RENAME TO core_employees;
