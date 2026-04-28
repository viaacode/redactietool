-- Table: public.pending_subtitles

CREATE TABLE IF NOT EXISTS public.pending_subtitles
(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department VARCHAR(120) NOT NULL,
    pid VARCHAR(120) NOT NULL,
    subtitle_type VARCHAR(20) NOT NULL DEFAULT 'closed',
    srt_filename VARCHAR(255) NOT NULL,
    srt_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT pending_subtitles_department_pid_unique UNIQUE (department, pid)
);

ALTER TABLE IF EXISTS public.pending_subtitles OWNER TO appuser;
