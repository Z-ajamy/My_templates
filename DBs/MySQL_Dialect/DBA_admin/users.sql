/*
 * ============================================================================
 * MYSQL 8.0+ USER MANAGEMENT & ROLE-BASED ACCESS CONTROL (RBAC) MASTER SCRIPT
 * ============================================================================
 * This script is an enterprise-grade architectural blueprint for managing 
 * identities, authentication plugins, hierarchical privileges, and resource limits.
 */

/* ============================================================================
 * SECTION 1: USER CREATION & AUTHENTICATION ARCHITECTURE (CREATE USER)
 * ============================================================================
 * Syntactic Structure: CREATE USER 'username'@'host' IDENTIFIED WITH ...
 *
 * HOST SIBLINGS & NETWORKING BOUNDARIES:
 * 1. 'developer'@'localhost'  : Strictly allows Unix socket or loopback connections.
 * 2. 'app_node'@'%'           : Wildcard host. Allows connection from ANY IP. Massive security hazard.
 * 3. 'api_gateway'@'10.0.5.%' : Subnet isolation. Restricted to the internal private network.
 */

-- Scenario A: Modern Secure User with Resource Governance and Password Policies
CREATE USER IF NOT EXISTS 'db_architect'@'10.0.5.%'
    /*
     * AUTHENTICATION PLUGIN SIBLINGS:
     * 1. caching_sha2_password (Default in 8.0): Uses SHA-256 with caching for high performance. Secure.
     * 2. mysql_native_password (Legacy): Uses older SHA-1 hashing. Vulnerable to brute-force. 
     * Only use for legacy client compatibility (e.g., old PHP/Java drivers).
     */
    IDENTIFIED WITH caching_sha2_password BY 'Complex_Crypto_Entropy_String_99!'
    
    /*
     * PASSWORD MANAGEMENT & ROTATION POLICIES:
     * Enforces continuous compliance at the engine level without application logic.
     */
    REQUIRE SSL                       -- Forces transport layer encryption (TLS)
    PASSWORD EXPIRE INTERVAL 90 DAY   -- Enforces regular credential rotation
    PASSWORD HISTORY 5                -- Prevents reuse of the last 5 passwords
    PASSWORD REUSE INTERVAL 365 DAY   -- Restricts reusing old passwords within a year
    FAILED_LOGIN_ATTEMPTS 3           -- Account locking mechanism threshold
    PASSWORD_LOCK_TIME 1              -- Automatically locks account for 1 day on brute-force detection
    
    /*
     * RESOURCE GOVERNANCE (Denial of Service Prevention):
     * Limits system resource consumption per connection block.
     */
    WITH MAX_QUERIES_PER_HOUR 50000
         MAX_UPDATES_PER_HOUR 10000
         MAX_CONNECTIONS_PER_HOUR 100
         MAX_USER_CONNECTIONS 10;     -- Maximum concurrent sessions for this individual user

-- SIBLING OPERATION: Account Modification and Temporary Locking
ALTER USER 'db_architect'@'10.0.5.%' ACCOUNT LOCK;   -- Soft suspension
ALTER USER 'db_architect'@'10.0.5.%' ACCOUNT UNLOCK; -- Reactivation

/* ============================================================================
 * SECTION 2: PRIVILEGE HIERARCHY & THE LOGICAL BOUNDARIES OF *.*
 * ============================================================================
 * PRIVILEGE SCOPE LEVELS:
 * * Level 1: Global Level (*.*)
 * - Syntax: GRANT PRIVILEGES ON *.*
 * - Scope: Applies to all databases, tables, functions, and procedures on the instance.
 * - Architectural Impact: Modifies the `mysql.user` system table directly. 
 * Reserved strictly for DBAs. Granting administrative tokens here (like SUPER, SHUTDOWN, 
 * RELOAD, PROCESS) allows full server control.
 *
 * Level 2: Database Level (db_name.*)
 * - Syntax: GRANT PRIVILEGES ON enterprise_db.*
 * - Scope: Applies to all objects within a specific namespace.
 * - Architectural Impact: Modifies `mysql.db`. Standard level for application connections.
 *
 * Level 3: Table Level (db_name.table_name)
 * - Syntax: GRANT PRIVILEGES ON enterprise_db.financial_ledger
 * - Scope: Restricted to a single physical or virtual entity.
 * - Architectural Impact: Modifies `mysql.tables_priv`. Reduces blast radius.
 *
 * Level 4: Column Level (Privilege(col) ON db_name.table_name)
 * - Syntax: GRANT SELECT(emp_id, full_name), UPDATE(base_salary) ON enterprise_db.employees
 * - Scope: Surgical restriction of data access. Maximum zero-trust isolation.
 * - Architectural Impact: Modifies `mysql.columns_priv`. Highest CPU parsing overhead.
 */

/* ============================================================================
 * SECTION 3: ROLE-BASED ACCESS CONTROL (RBAC) ARCHITECTURE
 * ============================================================================
 * Roles are conceptual collections of privileges that act as security templates.
 * They drastically simplify identity and access management (IAM) lifecycle.
 */

-- 1. Create specialized roles (stored internally as users with no password/host set to '%')
CREATE ROLE IF NOT EXISTS 'analytics_read_only', 'data_engineer_role';

-- 2. Populate Roles with Precise Privileges across the hierarchy
-- Granting Database Level privileges to the read-only role
GRANT SELECT, SHOW VIEW 
ON analytics_db.* TO 'analytics_read_only';

-- Granting Table and Column Level privileges to the engineering role
GRANT SELECT, INSERT, UPDATE 
ON production_db.inventory 
TO 'data_engineer_role';

GRANT UPDATE(base_salary) 
ON production_db.employees 
TO 'data_engineer_role';

-- 3. Assigning the Role to a Human Kian (User)
GRANT 'data_engineer_role' TO 'db_architect'@'10.0.5.%';

/*
 * CRITICAL ARCHITECTURAL WARNING: THE DEFAULT ROLE PITFALL
 * When a role is granted to a user, it is NOT automatically active when the user logs in. 
 * The user session starts with zero role privileges unless explicitly activated.
 * SIBLING COMMANDS FOR ACTIVATION:
 * - Session Level: SET ROLE 'data_engineer_role'; (Must be executed by the application post-login)
 * - Persistent Level: SET DEFAULT ROLE ... (Configures engine-level auto-activation)
 */
SET DEFAULT ROLE 'data_engineer_role' TO 'db_architect'@'10.0.5.%';


/* ============================================================================
 * SECTION 4: THE HAZARDS OF 'WITH GRANT OPTION' & DELEGATION BOUNDARIES
 * ============================================================================
 * The 'WITH GRANT OPTION' clause allows the recipient user or role to grant their 
 * owned privileges to other users without requiring admin/root access.
 *
 * SECURITY ATTACK VECTOR:
 * If a user with 'GRANT OPTION' on '*.*' is compromised, the attacker can spawn 
 * new administrative accounts, bypass existing access controls, and establish persistence.
 */
GRANT SELECT, INSERT 
ON production_db.customer_records 
TO 'data_engineer_role' 
WITH GRANT OPTION; -- Allows role members to extend these exact tokens to others


/* ============================================================================
 * SECTION 5: PRIVILEGE AUDITING, REVOCATION, AND DECONSTRUCTION (SIBLINGS)
 * ============================================================================
 */

-- Inspection / Audit Trail: View active tokens for a specific identity
SHOW GRANTS FOR 'db_architect'@'10.0.5.%';
SHOW GRANTS FOR 'db_architect'@'10.0.5.%' USING 'data_engineer_role';

-- REVOKE SIBLING: Removing a specific privilege without dropping the user
REVOKE UPDATE(base_salary) 
ON production_db.employees 
FROM 'data_engineer_role';

-- REVOKE ALL: Strips all structural privileges and roles, leaves identity intact
REVOKE ALL PRIVILEGES, GRANT OPTION 
FROM 'db_architect'@'10.0.5.%';

-- Deconstruction Layer: Completely dropping identities and roles from the system dictionary
DROP USER 'db_architect'@'10.0.5.%';
DROP ROLE 'analytics_read_only', 'data_engineer_role';

-- Commit privilege alterations to the in-memory ACL cache immediately
FLUSH PRIVILEGES;
