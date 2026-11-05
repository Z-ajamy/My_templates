/*
 * ============================================================================
 * TARGET SCHEMA DEFINITION
 * ============================================================================
 * Table 1: customers
 * - customer_id (PK), status (VARCHAR), region (VARCHAR)
 * Table 2: orders
 * - order_id (PK), customer_id (FK), total_amount (DECIMAL), order_date (DATE)
 * * ============================================================================
 * LOGICAL EXECUTION ORDER (Crucial for query optimization):
 * ============================================================================
 * 1. FROM / JOIN     : Identify and merge base tables.
 * 2. WHERE           : Filter base rows (Index scans happen here).
 * 3. GROUP BY        : Aggregate rows into groups.
 * 4. HAVING          : Filter aggregated groups.
 * 5. WINDOW          : Calculate window functions over partitions.
 * 6. SELECT          : Project the final columns/expressions.
 * 7. DISTINCT        : Remove duplicates from the projection (Avoid if using GROUP BY).
 * 8. ORDER BY        : Sort the final result set.
 * 9. LIMIT / OFFSET  : Truncate the result set.
 * ============================================================================
 */

/* * COMMON TABLE EXPRESSION (CTE)
 * Used to modularize the query. Better than subqueries in SELECT/WHERE clauses.
 * Performance Note: PostgreSQL >= 12 and MySQL >= 8 materialize CTEs only if 
 * referenced multiple times, otherwise they inline them. SQLite inlines them.
 */
WITH high_value_customers AS (
    SELECT 
        customer_id,
        /*
         * AGGREGATE FUNCTIONS SIBLINGS & USAGE:
         * 1. SUM(): Calculates total. Ignores NULLs.
         * 2. COUNT(*): Counts all rows. COUNT(col) counts non-NULL rows.
         * 3. AVG(): Calculates mean. Beware of NULLs lowering the count denominator.
         * 4. MIN() / MAX(): Finds extremes. Fast if columns are indexed.
         */
        SUM(total_amount) AS total_spent,
        COUNT(order_id) AS order_count
    FROM orders
    WHERE order_date >= '2023-01-01'
    GROUP BY customer_id
    /* * HAVING is strictly for filtering based on aggregate results. 
     * Never use HAVING for base columns (use WHERE instead for performance).
     */
    HAVING SUM(total_amount) > 5000
)

/* MAIN QUERY PROJECTION */
SELECT 
    c.region,
    c.customer_id,
    c.status,
    hvc.total_spent,
    hvc.order_count,
    
    /*
     * WINDOW FUNCTIONS SIBLINGS & USAGE:
     * Window functions operate on a set of rows without collapsing them (unlike GROUP BY).
     * 1. ROW_NUMBER(): Unique sequential integer (1, 2, 3...). Used here.
     * 2. RANK(): Leaves gaps on ties (1, 2, 2, 4...). Use when exact ranking matters.
     * 3. DENSE_RANK(): No gaps on ties (1, 2, 2, 3...).
     * 4. NTILE(n): Divides partitions into 'n' buckets.
     * 5. LAG() / LEAD(): Accesses previous/next row data. Vital for time-series analysis.
     *
     * Performance: Sorting inside OVER() can be expensive. Needs memory (work_mem in Postgres).
     */
    ROW_NUMBER() OVER (
        PARTITION BY c.region 
        ORDER BY hvc.total_spent DESC
    ) AS regional_rank

FROM customers AS c

/*
 * JOIN SIBLINGS & ARCHITECTURAL IMPACT:
 * * 1. INNER JOIN (Used here): 
 * - Returns rows with a match in both tables.
 * - Optimizer can freely reorder INNER JOINs to find the best execution plan.
 * * 2. LEFT [OUTER] JOIN:
 * - Returns all rows from left table, NULLs for right if no match.
 * - Forces the optimizer to evaluate the left table first, limiting optimization flexibility.
 * * 3. RIGHT [OUTER] JOIN:
 * - Bad practice for readability. Rewrite as LEFT JOIN by swapping table order.
 * * 4. FULL [OUTER] JOIN:
 * - Returns all rows from both tables. 
 * - Very slow. NOT natively supported in SQLite (requires UNION of LEFT joins).
 * * 5. CROSS JOIN:
 * - Cartesian product (N rows * M rows). Extreme performance hazard.
 */
INNER JOIN high_value_customers AS hvc 
    ON c.customer_id = hvc.customer_id

WHERE c.status = 'ACTIVE'

ORDER BY 
    c.region ASC,
    regional_rank ASC

/* * PAGINATION (LIMIT / OFFSET)
 * Standard but fundamentally flawed for deep pagination (See explanation below).
 */
LIMIT 100 OFFSET 0;



--######################################################
WITH high_value_customers AS (
    SELECT 
        customer_id,
        SUM(total_amount) AS total_spent,
        COUNT(order_id) AS order_count
    FROM orders
    WHERE order_date >= '2023-01-01'
    GROUP BY customer_id
    HAVING SUM(total_amount) > 5000
)
SELECT 
    c.region,
    c.customer_id,
    c.status,
    hvc.total_spent,
    hvc.order_count,
    ROW_NUMBER() OVER (
        PARTITION BY c.region 
        ORDER BY hvc.total_spent DESC
    ) AS regional_rank

FROM customers AS c
INNER JOIN high_value_customers AS hvc 
    ON c.customer_id = hvc.customer_id
WHERE c.status = 'ACTIVE'

ORDER BY 
    c.region ASC,
    regional_rank ASC
LIMIT 100 OFFSET 0;
--######################################################

