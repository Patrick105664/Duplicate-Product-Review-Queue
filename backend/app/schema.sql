CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    title      TEXT,
    brand      TEXT,
    model      TEXT,
    variant    TEXT,
    pack_quantity INTEGER,
    unit       TEXT,
    image_ref  TEXT,
    raw_json   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS labelled_pairs (
    pair_key     TEXT PRIMARY KEY,
    is_duplicate INTEGER NOT NULL CHECK (is_duplicate IN (0, 1))
);

CREATE TABLE IF NOT EXISTS suggestions (
    pair_key      TEXT PRIMARY KEY,
    id_a          TEXT NOT NULL REFERENCES products(product_id),
    id_b          TEXT NOT NULL REFERENCES products(product_id),
    confidence    REAL NOT NULL,
    reasons_json  TEXT NOT NULL,
    flags_json    TEXT NOT NULL DEFAULT '[]',
    created_at    TEXT NOT NULL,
    CHECK (id_a < id_b)
);

CREATE TABLE IF NOT EXISTS reviewers (
    reviewer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    display_name  TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'reviewer' CHECK (role IN ('reviewer', 'admin')),
    password_hash TEXT NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash  TEXT PRIMARY KEY,
    reviewer_id INTEGER NOT NULL REFERENCES reviewers(reviewer_id),
    created_at  TEXT NOT NULL,
    expires_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decisions (
    pair_key           TEXT PRIMARY KEY REFERENCES suggestions(pair_key),
    decision           TEXT NOT NULL CHECK (decision IN ('accept', 'reject')),
    reviewer           TEXT NOT NULL,
    note               TEXT,
    time_spent_seconds REAL,
    decided_at         TEXT NOT NULL,
    reviewer_id        INTEGER REFERENCES reviewers(reviewer_id)
);

CREATE TABLE IF NOT EXISTS decision_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_key    TEXT NOT NULL,
    decision    TEXT NOT NULL,
    reviewer    TEXT NOT NULL,
    decided_at  TEXT NOT NULL,
    reviewer_id INTEGER REFERENCES reviewers(reviewer_id)
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metric_snapshots (
    snapshot_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    label           TEXT,
    source          TEXT NOT NULL,
    threshold       REAL,
    true_positives  INTEGER NOT NULL CHECK (true_positives >= 0),
    false_positives INTEGER NOT NULL CHECK (false_positives >= 0),
    false_negatives INTEGER NOT NULL CHECK (false_negatives >= 0),
    true_negatives  INTEGER NOT NULL CHECK (true_negatives >= 0),
    precision       REAL,
    recall          REAL,
    accuracy        REAL,
    precision_num   INTEGER,
    precision_den   INTEGER,
    recall_num      INTEGER,
    recall_den      INTEGER,
    accuracy_num    INTEGER,
    accuracy_den    INTEGER,
    notes           TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_runs (
    scan_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at       TEXT NOT NULL,
    finished_at      TEXT,
    source           TEXT NOT NULL,
    products_count   INTEGER,
    pairs_found      INTEGER,
    new_pairs        INTEGER,
    status           TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    duration_seconds REAL,
    error            TEXT
);

CREATE TABLE IF NOT EXISTS pair_flags (
    flag_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_key   TEXT NOT NULL REFERENCES suggestions(pair_key),
    reviewer   TEXT NOT NULL,
    note       TEXT,
    flagged_at TEXT NOT NULL
);
