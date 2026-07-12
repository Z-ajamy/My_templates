/*
 * ============================================================================
 * MYSQL TRANSACTION CONTROL LANGUAGE (TCL) - ARCHITECTURAL TEMPLATE
 * ============================================================================
 * Target Engine: InnoDB (Strictly Required. MyISAM ignores TCL silently).
 *
 * UNDER THE HOOD MECHANICS:
 * 1. Undo Log: Stores the inverse of every DML operation (e.g., stores a DELETE 
 * if you do an INSERT) to allow physical ROLLBACK and support MVCC.
 * 2. Redo Log: Write-Ahead Log (WAL) that captures changes before they hit 
 * data pages on disk, ensuring Durability (Crash Recovery).
 * 3. Row Locking: InnoDB holds Exclusive Locks (X-Locks) on modified rows 
 * until the transaction completes (COMMIT/ROLLBACK).
 */

-- Crucial: Check engine capability. Transactions fail silently on non-transactional engines.
SET sql_mode = 'STRICT_TRANS_TABLES';

/* * ----------------------------------------------------------------------------
 * 1. TRANSACTION INITIALIZATION & ISOLATION LEVEL
 * ----------------------------------------------------------------------------
 * SIBLINGS (Isolation Levels - Set BEFORE starting the transaction):
 * 1. REPEATABLE READ (MySQL Default): Guarantees consistent reads within the same 
 * transaction. Uses Next-Key locks to prevent Phantom Reads.
 * 2. READ COMMITTED: Rows are unlocked as soon as they don't match the WHERE clause. 
 * Allows non-repeatable reads. Increases concurrency.
 * 3. READ UNCOMMITTED: Dirty reads allowed. Highest concurrency, zero consistency.
 * 4. SERIALIZABLE: Converts all plain SELECTs into SELECT ... FOR SHARE. Extremely slow.
 */
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Explicitly starts the transaction block. Disables autocommit for this session.
-- SIBLING: 'BEGIN;' or 'START TRANSACTION WITH CONSISTENT SNAPSHOT;' 
-- (The latter pre-allocates the MVCC read view immediately for maximum isolation).
START TRANSACTION;

/* * ----------------------------------------------------------------------------
 * 2. CORE DML OPERATIONS WITH ROW LOCKING
 * ----------------------------------------------------------------------------
 */
INSERT INTO enterprise_employees (national_id, full_name, base_salary, birth_date)
VALUES ('29906061122334', 'Systems Architect', 9500.00, '1999-06-06');

/* * ----------------------------------------------------------------------------
 * 3. SAVEPOINT MANAGEMENT (Partial Rollback Sub-systems)
 * ----------------------------------------------------------------------------
 * Architectural Purpose: Allows breaking down a massive monolithic transaction 
 * into smaller logical steps that can fail independently without aborting the entire block.
 */
SAVEPOINT point_alpha;

-- Perform a secondary operation that might fail or depend on business logic
UPDATE enterprise_employees 
SET base_salary = base_salary + 500.00 
WHERE national_id = '29906061122334';

/* * ----------------------------------------------------------------------------
 * 4. CONDITIONAL ROLLBACK & RESOLUTION
 * ----------------------------------------------------------------------------
 * SIBLINGS & COMMAND VARIATIONS:
 * 1. ROLLBACK TO SAVEPOINT name: Reverts data back to the savepoint state. 
 * Locks acquired AFTER the savepoint are released. The transaction remains ACTIVE.
 * 2. RELEASE SAVEPOINT name: Removes the savepoint from the session memory. 
 * Does NOT commit or rollback data. Frees internal dictionary resources.
 * 3. ROLLBACK (Global): Aborts the entire transaction, invalidates all savepoints, 
 * reads the Undo Log to reverse all mutations, and releases all row locks.
 */

-- Scenario A: Reverting only the secondary operation (Transaction stays alive)
ROLLBACK TO SAVEPOINT point_alpha;

-- Scenario B: Removing the savepoint metadata if the step succeeded
RELEASE SAVEPOINT point_alpha;

/* * ----------------------------------------------------------------------------
 * 5. FINAL COMMIT OR GLOBAL ROLLBACK
 * ----------------------------------------------------------------------------
 * COMMIT PHYSICAL MECHANISM:
 * 1. Flushes the transaction's changes from the InnoDB Log Buffer to the Redo Log.
 * 2. Initiates fsync() to write the Redo Log physically to disk (if innodb_flush_log_at_trx_commit = 1).
 * 3. Releases all Exclusive Row Locks.
 * 4. Marks the Undo Log pages as eligible for the Purge Thread.
 */
COMMIT; 

-- Alternative Global Abort (If an unrecoverable exception happens in application logic)
-- ROLLBACK;
