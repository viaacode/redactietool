-- Table: public.jobs

CREATE TABLE IF NOT EXISTS public.jobs
(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department character varying(50) COLLATE pg_catalog."default" NOT NULL,
    pid character varying(10) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL,
    processed_at timestamp with time zone,
    speechmatic_job_id character varying(10) COLLATE pg_catalog."default" NOT NULL,
    transcription text COLLATE pg_catalog."default",
    summary text COLLATE pg_catalog."default",
    chapters text COLLATE pg_catalog."default",
    status character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'created',
    CONSTRAINT jobs_department_pid_unique UNIQUE (department, pid)
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.jobs
    OWNER TO appuser;