/*
 * ============================================================================
 * MYSQL DELETE - ARCHITECTURAL TEMPLATE & DATA PURGE CHEAT SHEET
 * ============================================================================
 * Target Tables: enterprise_employees (emp_id PK)
 *
 * * THE PHYSICAL REALITY OF DELETE IN INNODB:
 * When you execute DELETE, InnoDB does NOT physically free the disk space. 
 * The operating system will not see a reduction in the .ibd file size.
 * It merely marks the index pages as reusable, creating disk fragmentation.
 * To reclaim physical space after massive deletes, you must run:
 * OPTIMIZE TABLE table_name; (Which physically rebuilds the table).
 */

/* * ----------------------------------------------------------------------------
 * 1. STANDARD TARGETED DELETE
 * ----------------------------------------------------------------------------
 * Architectural Rule: The WHERE clause MUST hit an index (preferably a Unique/PK).
 * If you attempt to delete based on a non-indexed column, InnoDB will fall back 
 * to a full table scan and place Next-Key Locks on EVERY SINGLE ROW, 
 * completely paralyzing the database for writes.
 */
DELETE FROM enterprise_employees
WHERE emp_id = 10050;

/* * ----------------------------------------------------------------------------
 * 2. MULTI-TABLE DELETE (JOIN)
 * ----------------------------------------------------------------------------
 * SIBLING USAGE: 
 * Used to purge records from one table based on a relational state in another 
 * table without fetching data into the application layer.
 * Note: 'DELETE e' means only records from the 'e' (enterprise_employees) 
 * table will be deleted.
 */
DELETE e
FROM enterprise_employees AS e
INNER JOIN departments AS d 
    ON e.department_id = d.id
WHERE d.status = 'CLOSED_DOWN';

/* * ----------------------------------------------------------------------------
 * 3. CHUNKED DELETE (LIMIT & ORDER BY) - The Production Standard
 * ----------------------------------------------------------------------------
 * Anti-pattern: DELETE FROM logs WHERE created_at < '2022-01-01'; (On 10M rows).
 * This will blow up the Buffer Pool, max out the I/O, and cause replication lag.
 * * Solution: Delete in chunks. Run this in a loop via a backend cron job 
 * until rows_affected == 0.
 */
DELETE FROM enterprise_employees
WHERE status = 'TERMINATED'
ORDER BY updated_at ASC
LIMIT 1000;


/* * ============================================================================
 * THE SIBLINGS OF DELETE (ALTERNATIVES & STRICT RULES)
 * ============================================================================
 */

/* * ----------------------------------------------------------------------------
 * SIBLING 1: TRUNCATE TABLE (The Nuclear Option)
 * ----------------------------------------------------------------------------
 * Mechanism: TRUNCATE is a DDL (Data Definition Language) operation, not DML.
 * It physically drops the entire table structure and recreates a fresh, empty one.
 * * Pros: 
 * - O(1) time complexity. It takes milliseconds, regardless of table size.
 * - Bypasses the Undo Log entirely (no I/O overhead).
 * - Physically frees up disk space immediately to the OS.
 * * Cons/Dangers:
 * - CANNOT be rolled back. Once executed, data is gone.
 * - Resets the AUTO_INCREMENT counter back to 1.
 * - Fails if referenced by Foreign Keys.
 * - Does NOT trigger 'ON DELETE' triggers.
 */
-- TRUNCATE TABLE log_entries_temp;

/* * ----------------------------------------------------------------------------
 * SIBLING 2: SOFT DELETE (The Architectural Zero-Trust Standard)
 * ----------------------------------------------------------------------------
 * In core backend infrastructure (Financial, Healthcare, Enterprise), 
 * physical deletion is considered a severe architectural flaw.
 * Data must be preserved for structural audits and behavior tracking.
 * * Instead of DELETE, we use an UPDATE statement to flag the record.
 * This ensures behavioral confidentiality and full auditability.
 */
-- UPDATE enterprise_employees 
-- SET is_deleted = TRUE, deleted_at = CURRENT_TIMESTAMP 
-- WHERE emp_id = 10050;
