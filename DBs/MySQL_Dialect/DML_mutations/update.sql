/*
 * ============================================================================
 * MYSQL UPDATE - ARCHITECTURAL TEMPLATE & DATA MUTATION
 * ============================================================================
 * Target Tables: enterprise_employees (emp_id PK), departments (id PK)
 *
 * * THE EXECUTION PIPELINE OF AN UPDATE:
 * 1. Query Parser & Optimizer: Determines the best index to find the target rows.
 * 2. Storage Engine (InnoDB): Acquires Exclusive Locks (X-Locks) on the target rows.
 * 3. Buffer Pool: Modifies the data pages in RAM (making them "Dirty Pages").
 * 4. Undo Log: Writes the old values (to allow for ROLLBACK and MVCC).
 * 5. Redo Log: Writes the new values (to survive server crashes).
 * 6. Binlog: Records the transaction for replication to Slave servers.
 */

/* * ----------------------------------------------------------------------------
 * 1. STANDARD SINGLE-TABLE UPDATE
 * ----------------------------------------------------------------------------
 * Architectural Rule: The columns in the WHERE clause MUST be indexed. 
 * If no index is used, InnoDB falls back to a Full Table Scan and places 
 * Next-Key Locks on EVERY SINGLE ROW in the table, paralyzing production writes.
 */
UPDATE enterprise_employees
SET 
    base_salary = base_salary * 1.10,
    updated_at = CURRENT_TIMESTAMP
WHERE contract_type = 'FULL_TIME'
  AND emp_id = 10050; 

/* * ----------------------------------------------------------------------------
 * 2. MULTI-TABLE UPDATE (JOIN) - MySQL Specific Optimization
 * ----------------------------------------------------------------------------
 * SIBLING ARCHITECTURE (Cross-Engine Compatibility Limits):
 * - MySQL: Uses 'UPDATE t1 JOIN t2 ON ... SET ...'
 * - PostgreSQL/SQLite: Do NOT support JOIN directly in UPDATE. They use 
 * 'UPDATE t1 SET ... FROM t2 WHERE ...'
 *
 * Why use this? To update a table based on conditions evaluated in another 
 * table without pulling data into the application layer.
 */
UPDATE enterprise_employees AS e
INNER JOIN departments AS d 
    ON e.department_id = d.id
SET 
    e.base_salary = e.base_salary + 500.00
WHERE d.department_name = 'Engineering'
  AND e.contract_type = 'FULL_TIME';

/* * ----------------------------------------------------------------------------
 * 3. CONDITIONAL BULK UPDATE (CASE WHEN)
 * ----------------------------------------------------------------------------
 * SIBLING USAGE: 
 * Used to apply different logic to different rows in a SINGLE network round-trip 
 * and a SINGLE transaction. This is exponentially faster than looping over rows 
 * in backend code (e.g., Python/C++) and sending individual UPDATE statements.
 */
UPDATE enterprise_employees
SET base_salary = CASE
    WHEN contract_type = 'FULL_TIME' THEN base_salary * 1.10
    WHEN contract_type = 'PART_TIME' THEN base_salary * 1.05
    ELSE base_salary /* CRITICAL: If omitted, unmatched rows become NULL */
END
WHERE department_id = 5;

/* * ----------------------------------------------------------------------------
 * 4. CHUNKED UPDATE (LIMIT & ORDER BY)
 * ----------------------------------------------------------------------------
 * MySQL allows ORDER BY and LIMIT in single-table updates (unlike Postgres).
 * Use Case: Safely processing a queue or slowly migrating data without 
 * blowing up the Undo Log or causing massive Replication Lag.
 */
UPDATE enterprise_employees
SET status = 'PROCESSED'
WHERE status = 'PENDING'
ORDER BY created_at ASC
LIMIT 1000;
