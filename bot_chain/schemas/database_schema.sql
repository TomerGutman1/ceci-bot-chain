-- CECI-AI Government Decisions Database Schema
-- Based on israeli_government_decisions_DB_SCHEME.md

-- Main decisions table
CREATE TABLE IF NOT EXISTS government_decisions (
    id SERIAL PRIMARY KEY,
    government_number INTEGER NOT NULL,
    decision_number INTEGER NOT NULL,
    decision_date DATE,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    topics TEXT[], -- Array of topic keywords
    ministries TEXT[], -- Array of ministry names
    decision_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_gov_decision UNIQUE (government_number, decision_number),
    CONSTRAINT valid_government_number CHECK (government_number > 0 AND government_number <= 50),
    CONSTRAINT valid_decision_number CHECK (decision_number > 0)
);

-- Governments metadata table
CREATE TABLE IF NOT EXISTS governments (
    id SERIAL PRIMARY KEY,
    government_number INTEGER UNIQUE NOT NULL,
    start_date DATE,
    end_date DATE,
    prime_minister VARCHAR(100),
    coalition_parties TEXT[],
    total_decisions INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    
    CONSTRAINT valid_government_number CHECK (government_number > 0 AND government_number <= 50)
);

-- Topics taxonomy table
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    parent_topic_id INTEGER REFERENCES topics(id),
    description TEXT,
    keywords TEXT[],
    
    -- Hebrew topic normalization
    hebrew_variants TEXT[] -- Different Hebrew spellings/forms
);

-- Ministries reference table
CREATE TABLE IF NOT EXISTS ministries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    short_name VARCHAR(50),
    english_name VARCHAR(200),
    category VARCHAR(50),
    active BOOLEAN DEFAULT true,
    
    -- Hebrew ministry normalization
    hebrew_variants TEXT[] -- Different Hebrew forms
);

-- Decision-topic many-to-many relationship
CREATE TABLE IF NOT EXISTS decision_topics (
    decision_id INTEGER REFERENCES government_decisions(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0,
    
    PRIMARY KEY (decision_id, topic_id)
);

-- Decision-ministry many-to-many relationship
CREATE TABLE IF NOT EXISTS decision_ministries (
    decision_id INTEGER REFERENCES government_decisions(id) ON DELETE CASCADE,
    ministry_id INTEGER REFERENCES ministries(id) ON DELETE CASCADE,
    role VARCHAR(50), -- 'primary', 'secondary', 'mentioned'
    
    PRIMARY KEY (decision_id, ministry_id)
);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_decisions_content_fts 
ON government_decisions USING gin(to_tsvector('hebrew', content));

CREATE INDEX IF NOT EXISTS idx_decisions_title_fts 
ON government_decisions USING gin(to_tsvector('hebrew', title));

CREATE INDEX IF NOT EXISTS idx_decisions_summary_fts 
ON government_decisions USING gin(to_tsvector('hebrew', summary));

-- Regular indexes for common queries
CREATE INDEX IF NOT EXISTS idx_decisions_government_number 
ON government_decisions(government_number);

CREATE INDEX IF NOT EXISTS idx_decisions_decision_number 
ON government_decisions(decision_number);

CREATE INDEX IF NOT EXISTS idx_decisions_date 
ON government_decisions(decision_date);

CREATE INDEX IF NOT EXISTS idx_decisions_topics 
ON government_decisions USING gin(topics);

CREATE INDEX IF NOT EXISTS idx_decisions_ministries 
ON government_decisions USING gin(ministries);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_decisions_gov_date 
ON government_decisions(government_number, decision_date);

CREATE INDEX IF NOT EXISTS idx_decisions_gov_number 
ON government_decisions(government_number, decision_number);

-- Views for common queries

-- View: Recent decisions by government
CREATE OR REPLACE VIEW recent_decisions_by_government AS
SELECT 
    government_number,
    COUNT(*) as total_decisions,
    MAX(decision_date) as latest_decision,
    MIN(decision_date) as first_decision
FROM government_decisions 
WHERE status = 'active'
GROUP BY government_number
ORDER BY government_number DESC;

-- View: Decisions by topic with counts
CREATE OR REPLACE VIEW decisions_by_topic AS
SELECT 
    unnest(topics) as topic,
    COUNT(*) as decision_count,
    COUNT(DISTINCT government_number) as government_count,
    MAX(decision_date) as latest_decision
FROM government_decisions 
WHERE status = 'active'
GROUP BY unnest(topics)
ORDER BY decision_count DESC;

-- View: Ministry activity summary
CREATE OR REPLACE VIEW ministry_activity AS
SELECT 
    unnest(ministries) as ministry,
    COUNT(*) as decision_count,
    COUNT(DISTINCT government_number) as government_count,
    MAX(decision_date) as latest_activity
FROM government_decisions 
WHERE status = 'active'
GROUP BY unnest(ministries)
ORDER BY decision_count DESC;

-- Sample data insert (for testing)
INSERT INTO governments (government_number, start_date, prime_minister, coalition_parties) VALUES
(35, '2021-06-13', 'נפתלי בנט', ARRAY['ימינה', 'יש עתיד', 'כחול לבן', 'עבודה', 'מרץ']),
(36, '2022-06-30', 'יאיר לפיד', ARRAY['יש עתיד', 'כחול לבן', 'עבודה', 'מרץ']),
(37, '2022-12-29', 'בנימין נתניהו', ARRAY['ליכוד', 'שס', 'יהדות התורה', 'ציונות דתית', 'עוצמה יהודית'])
ON CONFLICT (government_number) DO NOTHING;

-- Insert sample topics
INSERT INTO topics (name, category, keywords, hebrew_variants) VALUES
('חינוך', 'חברה', ARRAY['בתי ספר', 'מורים', 'תלמידים', 'אוניברסיטאות'], ARRAY['חינוך', 'השכלה', 'לימודים']),
('ביטחון', 'ביטחון', ARRAY['צבא', 'משטרה', 'טרור', 'איומים'], ARRAY['ביטחון', 'בטחון', 'ביטחון לאומי']),
('כלכלה', 'כלכלה', ARRAY['תקציב', 'מסים', 'השקעות', 'יצוא'], ARRAY['כלכלה', 'כלכלי', 'משק']),
('בריאות', 'חברה', ARRAY['בתי חולים', 'רופאים', 'תרופות', 'ביטוח'], ARRAY['בריאות', 'רפואה', 'בריאותי']),
('תחבורה', 'תשתית', ARRAY['כבישים', 'רכבות', 'תחבורה ציבורית'], ARRAY['תחבורה', 'תחבורתי', 'הובלה'])
ON CONFLICT (name) DO NOTHING;

-- Insert sample ministries
INSERT INTO ministries (name, short_name, english_name, category, hebrew_variants) VALUES
('משרד החינוך', 'מח״י', 'Ministry of Education', 'חברה', ARRAY['משרד החינוך', 'החינוך', 'מח״י']),
('משרד הביטחון', 'משה״ב', 'Ministry of Defense', 'ביטחון', ARRAY['משרד הביטחון', 'הביטחון', 'משה״ב']),
('משרד האוצר', 'האוצר', 'Ministry of Finance', 'כלכלה', ARRAY['משרד האוצר', 'האוצר', 'אוצר']),
('משרד הבריאות', 'משה״ב', 'Ministry of Health', 'חברה', ARRAY['משרד הבריאות', 'הבריאות', 'בריאות']),
('משרד התחבורה', 'התחבורה', 'Ministry of Transport', 'תשתית', ARRAY['משרד התחבורה', 'התחבורה', 'תחבורה'])
ON CONFLICT (name) DO NOTHING;

-- Functions for Hebrew text processing

-- Function to normalize Hebrew text for search
CREATE OR REPLACE FUNCTION normalize_hebrew_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Remove nikud (Hebrew diacritics)
    input_text := regexp_replace(input_text, '[\u0591-\u05C7]', '', 'g');
    
    -- Normalize whitespace
    input_text := regexp_replace(input_text, '\s+', ' ', 'g');
    
    -- Trim
    input_text := trim(input_text);
    
    RETURN input_text;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to extract government number from text
CREATE OR REPLACE FUNCTION extract_government_number(input_text TEXT)
RETURNS INTEGER AS $$
DECLARE
    gov_num INTEGER;
BEGIN
    -- Try direct number pattern: "ממשלה 37"
    SELECT (regexp_match(input_text, 'ממשלה\s+(\d+)'))[1]::INTEGER INTO gov_num;
    
    IF gov_num IS NOT NULL THEN
        RETURN gov_num;
    END IF;
    
    -- Try Hebrew number patterns
    CASE 
        WHEN input_text ~ 'שלושים ושבע|37' THEN RETURN 37;
        WHEN input_text ~ 'שלושים ושש|36' THEN RETURN 36;
        WHEN input_text ~ 'שלושים וחמש|35' THEN RETURN 35;
        WHEN input_text ~ 'שלושים ושמונה|38' THEN RETURN 38;
        ELSE RETURN NULL;
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to extract decision number from text
CREATE OR REPLACE FUNCTION extract_decision_number(input_text TEXT)
RETURNS INTEGER AS $$
DECLARE
    decision_num INTEGER;
BEGIN
    -- Try pattern: "החלטה 660" or "החלטה מספר 660"
    SELECT (regexp_match(input_text, 'החלטה\s+(?:מספר\s+)?(\d+)'))[1]::INTEGER INTO decision_num;
    
    IF decision_num IS NOT NULL THEN
        RETURN decision_num;
    END IF;
    
    -- Try standalone numbers that might be decision numbers
    SELECT (regexp_match(input_text, '\b(\d{3,4})\b'))[1]::INTEGER INTO decision_num;
    
    RETURN decision_num;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Row Level Security (RLS) - commented out for development
-- ALTER TABLE government_decisions ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY decisions_public_read ON government_decisions FOR SELECT USING (status = 'active');

COMMENT ON TABLE government_decisions IS 'Main table storing Israeli government decisions with full-text search capabilities';
COMMENT ON TABLE governments IS 'Metadata about Israeli governments including terms and leadership';
COMMENT ON TABLE topics IS 'Taxonomy of decision topics with Hebrew normalization';
COMMENT ON TABLE ministries IS 'Reference table for Israeli government ministries';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;