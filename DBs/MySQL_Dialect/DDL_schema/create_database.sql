/*
 * ============================================================================
 * MYSQL CREATE DATABASE - ARCHITECTURAL TEMPLATE
 * ============================================================================
 * Note: In MySQL, 'CREATE DATABASE' and 'CREATE SCHEMA' are strictly synonymous.
 * Using SCHEMA is preferred in standard ANSI SQL, but DATABASE is the MySQL norm.
 */
CREATE DATABASE IF NOT EXISTS enterprise_core_db

    /* * ------------------------------------------------------------------------
     * 1. CHARACTER SET (Data Encoding)
     * ------------------------------------------------------------------------
     * CHARACTER SET SIBLINGS & USAGE:
     * 1. utf8mb4 (Default in MySQL 8.0+): The standard 4-byte UTF-8 implementation. 
     * Supports emojis, complex Asian characters, and all languages safely. 
     * Architectural Standard: ALWAYS use this for global applications.
     * 2. utf8mb3 / utf8: Legacy 3-byte implementation. 
     * Warning: Deprecated and highly dangerous. Will cause silent data truncation 
     * if a user inputs a 4-byte character (like an emoji).
     * 3. latin1: 1-byte per character. 
     * Pros: Extremely fast and space-efficient. 
     * Cons: Strictly for Western European/English data. Fails with Arabic completely.
     * 4. binary: Stores strings as raw byte strings.
     */
    CHARACTER SET utf8mb4

    /* * ------------------------------------------------------------------------
     * 2. COLLATION (Sorting & Comparison Rules)
     * ------------------------------------------------------------------------
     * Collation dictates how strings are compared and sorted. It heavily impacts 
     * Index usage, WHERE clauses, and ORDER BY performance.
     * * COLLATION SIBLINGS:
     * 1. utf8mb4_0900_ai_ci (MySQL 8.0 Default):
     * - 0900: Based on Unicode 9.0 standard.
     * - ai (Accent Insensitive): 'e' equals 'é'.
     * - ci (Case Insensitive): 'A' equals 'a'.
     * Use case: Best for general text and human-readable search.
     * * 2. utf8mb4_bin:
     * - Compares raw numeric byte values directly.
     * - Strictly Case Sensitive ('A' != 'a').
     * Use case: Significantly faster. Use if the database primarily handles 
     * exact matches (e.g., UUIDs, Hashes, API Keys) rather than natural language.
     * * 3. utf8mb4_0900_as_cs:
     * - Accent Sensitive, Case Sensitive. 
     * Use case: Rare, but required for strict linguistic sorting systems.
     */
    COLLATE utf8mb4_0900_ai_ci

    /* * ------------------------------------------------------------------------
     * 3. ENCRYPTION (Data-at-Rest) - MySQL 8.0.16+
     * ------------------------------------------------------------------------
     * Defines default Data-at-Rest encryption for all tables within the database.
     * * ENCRYPTION SIBLINGS:
     * 1. ENCRYPTION = 'Y': 
     * Encrypts physical .ibd files on the disk using the MySQL keyring plugin. 
     * Architectural Impact: Crucial for compliance (PCI-DSS, HIPAA, GDPR). 
     * Adds slight CPU overhead during disk I/O operations.
     * 2. ENCRYPTION = 'N' (Default): 
     * No at-rest encryption. Yields maximum raw disk performance.
     */
    ENCRYPTION = 'Y';
