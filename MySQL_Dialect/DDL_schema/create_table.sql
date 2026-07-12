/*
 * ============================================================================
 * MYSQL CREATE TABLE - ARCHITECTURAL TEMPLATE
 * ============================================================================
 * Best Practice: Always use 'IF NOT EXISTS' in migration scripts to prevent 
 * deployment failures if the table is already present in the target environment.
 */
CREATE TABLE IF NOT EXISTS enterprise_employees (

    /* * ------------------------------------------------------------------------
     * 1. PRIMARY KEYS & NUMERIC TYPES
     * ------------------------------------------------------------------------
     */
    emp_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    /*
     * NUMERIC SIBLINGS & USAGE:
     * 1. TINYINT  (1 byte)  : -128 to 127. Use for booleans (TINYINT(1)) or status codes.
     * 2. SMALLINT (2 bytes) : -32,768 to 32,767. Use for lookup tables with few records.
     * 3. INT      (4 bytes) : ~ -2.1B to 2.1B. Standard ID for medium applications.
     * 4. BIGINT   (8 bytes) : Massive range. Standard for enterprise PKs/FKs to avoid integer overflow.
     * * Modifiers:
     * - UNSIGNED: Disallows negative numbers, doubling the positive range limit. 
     * Always use UNSIGNED for IDs and counts.
     * - AUTO_INCREMENT: MySQL-specific. Automatically generates sequential integers.
     */

    department_id BIGINT UNSIGNED NULL,

    /* * ------------------------------------------------------------------------
     * 2. STRING (CHARACTER) TYPES
     * ------------------------------------------------------------------------
     */
    national_id CHAR(14) NOT NULL,
    /*
     * STRING SIBLINGS & USAGE:
     * 1. CHAR(n)    : Fixed length (e.g., exactly 14 chars). 
     * Pros: Faster performance, no fragmentation. 
     * Cons: Wastes space if data is shorter (pads with spaces).
     * Use for: Hashes (SHA-256), Country Codes (ISO 3166), National IDs.
     * 2. VARCHAR(n) : Variable length up to 'n' chars. 
     * Pros: Saves space. 
     * Cons: Slight overhead for storing string length (1-2 bytes).
     * Use for: Names, Emails, Titles.
     */

    full_name VARCHAR(150) NOT NULL,
    
    biography TEXT NULL,
    /*
     * LARGE OBJECT (LOB) SIBLINGS:
     * 1. TEXT       : Up to 64KB. Stored off-page (outside the main row data).
     * 2. MEDIUMTEXT : Up to 16MB. 
     * 3. LONGTEXT   : Up to 4GB.
     * Warning: Heavily degrades performance if used in temporary tables or sorting (ORDER BY/GROUP BY).
     */

    /* * ------------------------------------------------------------------------
     * 3. ENUMERATIONS (ENUM)
     * ------------------------------------------------------------------------
     */
    contract_type ENUM('FULL_TIME', 'PART_TIME', 'CONTRACTOR') NOT NULL DEFAULT 'FULL_TIME',
    /*
     * ENUM SIBLINGS:
     * - SET: Similar to ENUM but allows multiple values (e.g., 'A,B'). 
     * Note: ENUM is highly memory efficient (stores internally as integers).
     * Anti-pattern: Do not use ENUM if the list of values changes frequently 
     * (requires ALTER TABLE). Use a separate lookup table with a Foreign Key instead.
     */

    /* * ------------------------------------------------------------------------
     * 4. EXACT MATH (FINANCIAL DATA)
     * ------------------------------------------------------------------------
     */
    base_salary DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    /*
     * DECIMAL(Precision, Scale):
     * - Precision: Total number of digits (10).
     * - Scale: Digits after the decimal point (2). Maximum value here is 99,999,999.99.
     * SIBLINGS:
     * 1. FLOAT / DOUBLE: Floating-point types. 
     * CRITICAL WARNING: Never use FLOAT/DOUBLE for money/financial data due to 
     * binary rounding errors (e.g., 0.1 + 0.2 = 0.30000000000000004). 
     * Always use DECIMAL for exact arithmetic.
     */

    /* * ------------------------------------------------------------------------
     * 5. DATE & TIME
     * ------------------------------------------------------------------------
     */
    birth_date DATE NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    /*
     * TEMPORAL SIBLINGS:
     * 1. DATE      : 'YYYY-MM-DD' (No time).
     * 2. DATETIME  : 'YYYY-MM-DD HH:MM:SS'. Range: 1000-01-01 to 9999-12-31. 
     * Does NOT convert time zones. Stored exactly as inserted.
     * 3. TIMESTAMP : Range: 1970-01-01 to 2038-01-19 (Year 2038 problem).
     * CONVERTS to UTC for storage, and back to current time zone on retrieval.
     * Use for metadata (created_at, updated_at). Use DATETIME for absolute events.
     */

    /* * ------------------------------------------------------------------------
     * 6. JSON & ADVANCED TYPES (MySQL 5.7.8+)
     * ------------------------------------------------------------------------
     */
    metadata JSON NULL,
    /*
     * JSON automatically validates formatting. Avoid replacing standard relational 
     * columns with JSON unless the schema is genuinely schemaless/dynamic.
     */

    /* * ============================================================================
     * TABLE CONSTRAINTS & INDEXES
     * ============================================================================
     */
    
    -- Primary Key Definition
    PRIMARY KEY (emp_id),
    
    -- Unique Constraint (Implicitly creates a UNIQUE INDEX)
    UNIQUE KEY uk_national_id (national_id),
    UNIQUE KEY uk_email (full_name), /* Named constraint for easier dropping later */

    -- Table-Level Check Constraint (MySQL 8.0.16+)
    CONSTRAINT chk_salary CHECK (base_salary >= 0),

    /*
     * INDEX SIBLINGS:
     * 1. B-TREE (Default): Excellent for range queries (>, <, BETWEEN) and sorting.
     * 2. HASH (Memory Engine only): Fast for exact matches (=), useless for ranges.
     * 3. FULLTEXT: For natural language search in TEXT/VARCHAR columns.
     */
    INDEX idx_department_salary (department_id, base_salary DESC),

    -- Foreign Key Constraint
    CONSTRAINT fk_employee_department 
        FOREIGN KEY (department_id) 
        REFERENCES departments(id)
        ON DELETE SET NULL 
        ON UPDATE CASCADE
    /*
     * FOREIGN KEY ACTIONS:
     * 1. RESTRICT (Default): Rejects deletion of parent if child exists.
     * 2. CASCADE: Automatically deletes child rows when parent is deleted. 
     * (Use with caution - can lock large parts of the database).
     * 3. SET NULL: Sets child column to NULL (Column must allow NULL).
     * 4. NO ACTION: Similar to RESTRICT in MySQL.
     */

) 
/* * ============================================================================
 * TABLE OPTIONS (STORAGE ENGINE & CHARSET)
 * ============================================================================
 */
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_0900_ai_ci 
COMMENT='Core table storing enterprise employee records';

/*
 * ENGINE SIBLINGS:
 * 1. InnoDB (Default): ACID compliant, supports Transactions, Row-level locking, and Foreign Keys. 
 * MUST be used for 99% of production tables.
 * 2. MyISAM: No transactions, Table-level locking (slow writes). Fast read/count. Deprecated in modern use.
 * 3. MEMORY: Stored entirely in RAM. Data lost on restart. Good for temporary caches.
 *
 * CHARSET SIBLINGS:
 * 1. utf8mb4: The TRUE UTF-8 implementation in MySQL. Supports 4-byte characters (Emojis, Complex Asian characters).
 * 2. utf8 (utf8mb3): A flawed, legacy 3-byte implementation. NEVER USE IT.
 *
 * COLLATE: Determines sorting/comparison rules (e.g., case sensitivity).
 * - ai = Accent Insensitive (e = é).
 * - ci = Case Insensitive (A = a).
 * - bin = Binary (Exact byte comparison, Case Sensitive, extremely fast).
 */
