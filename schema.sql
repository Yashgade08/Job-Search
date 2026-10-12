-- ==============================================================================
-- PostgreSQL DDL Schema for Job Market Skill Demand Analyzer & Crawler
-- ==============================================================================

-- 1. Crawl Runs Table
CREATE TABLE IF NOT EXISTS crawl_runs (
    id SERIAL PRIMARY KEY,
    run_uuid VARCHAR(64) UNIQUE NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds FLOAT DEFAULT 0.0,
    urls_discovered INTEGER DEFAULT 0,
    pages_crawled INTEGER DEFAULT 0,
    jobs_extracted INTEGER DEFAULT 0,
    duplicates_skipped INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    average_page_time_ms FLOAT DEFAULT 0.0,
    http_200_count INTEGER DEFAULT 0,
    http_429_count INTEGER DEFAULT 0,
    http_other_count INTEGER DEFAULT 0,
    error_summary TEXT
);

CREATE INDEX IF NOT EXISTS idx_crawl_runs_source ON crawl_runs(source_name);
CREATE INDEX IF NOT EXISTS idx_crawl_runs_status ON crawl_runs(status);

-- 2. Crawl Audit Logs Table
CREATE TABLE IF NOT EXISTS crawl_logs (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES crawl_runs(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10) DEFAULT 'INFO',
    url TEXT,
    status_code INTEGER,
    message TEXT NOT NULL,
    error_type VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_crawl_logs_run_id ON crawl_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_level ON crawl_logs(level);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_time ON crawl_logs(timestamp);

-- 3. Crawl Frontier Table
CREATE TABLE IF NOT EXISTS crawl_frontier (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    canonical_url VARCHAR(1000) UNIQUE NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    priority INTEGER DEFAULT 10,
    depth INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'queued',
    retry_count INTEGER DEFAULT 0,
    http_status INTEGER,
    error_message TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    crawled_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_frontier_status ON crawl_frontier(status);
CREATE INDEX IF NOT EXISTS idx_frontier_priority ON crawl_frontier(priority);
CREATE INDEX IF NOT EXISTS idx_frontier_source ON crawl_frontier(source_name);

-- 4. Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    fingerprint VARCHAR(64) UNIQUE NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location_raw VARCHAR(255),
    normalized_title VARCHAR(255) NOT NULL,
    role_category VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    is_remote BOOLEAN DEFAULT FALSE,
    salary_min FLOAT,
    salary_max FLOAT,
    salary_currency VARCHAR(10),
    salary_period VARCHAR(20),
    experience_min_years FLOAT,
    experience_max_years FLOAT,
    experience_level VARCHAR(50),
    description_raw TEXT,
    description_cleaned TEXT NOT NULL,
    raw_html TEXT,
    posting_date TIMESTAMP,
    job_url TEXT NOT NULL,
    canonical_url VARCHAR(1000) NOT NULL,
    source_portal VARCHAR(100) NOT NULL,
    crawl_run_id INTEGER REFERENCES crawl_runs(id) ON DELETE SET NULL,
    extracted_skills_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_fingerprint ON jobs(fingerprint);
CREATE INDEX IF NOT EXISTS idx_jobs_role_cat ON jobs(role_category);
CREATE INDEX IF NOT EXISTS idx_jobs_norm_title ON jobs(normalized_title);
CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city);
CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);
CREATE INDEX IF NOT EXISTS idx_jobs_remote ON jobs(is_remote);
CREATE INDEX IF NOT EXISTS idx_jobs_exp_level ON jobs(experience_level);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source_portal);
CREATE INDEX IF NOT EXISTS idx_jobs_posting_date ON jobs(posting_date);

-- 5. Standardized Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    normalized_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    is_tech_skill BOOLEAN DEFAULT TRUE,
    aliases TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);

-- 6. Job-Skill Association Junction Table
CREATE TABLE IF NOT EXISTS job_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    is_required BOOLEAN DEFAULT TRUE,
    confidence FLOAT DEFAULT 1.0,
    occurrence_count INTEGER DEFAULT 1,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_job_skill UNIQUE (job_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_job_skills_job ON job_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_req ON job_skills(is_required);

-- 7. Analytics Views for Fast Aggregations
CREATE OR REPLACE VIEW view_top_skills AS
SELECT 
    s.id AS skill_id,
    s.name AS skill_name,
    s.category AS skill_category,
    s.is_tech_skill,
    COUNT(js.job_id) AS demand_count,
    ROUND(COUNT(CASE WHEN js.is_required = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(js.job_id), 0), 2) AS required_percentage,
    AVG(CASE WHEN j.salary_max IS NOT NULL THEN (j.salary_min + j.salary_max)/2.0 ELSE NULL END) AS avg_salary
FROM skills s
JOIN job_skills js ON s.id = js.skill_id
JOIN jobs j ON js.job_id = j.id
GROUP BY s.id, s.name, s.category, s.is_tech_skill
ORDER BY demand_count DESC;

CREATE OR REPLACE VIEW view_role_skill_demand AS
SELECT 
    j.role_category,
    s.name AS skill_name,
    s.category AS skill_category,
    COUNT(js.job_id) AS demand_count
FROM jobs j
JOIN job_skills js ON j.id = js.job_id
JOIN skills s ON js.skill_id = s.id
GROUP BY j.role_category, s.name, s.category
ORDER BY j.role_category, demand_count DESC;
