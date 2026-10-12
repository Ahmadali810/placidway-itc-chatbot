-- Run this once in the Supabase SQL editor (free project is fine).
-- Enables vector search + tables used by the Placidway chatbot n8n workflows.

create extension if not exists vector;

create table if not exists placidway_docs (
  id bigserial primary key,
  content text not null,
  embedding vector(768),
  source_url text,
  source_name text,
  created_at timestamptz default now()
);

create table if not exists chat_history (
  id bigserial primary key,
  session_id text not null,
  role text not null,
  content text not null,
  created_at timestamptz default now()
);

create table if not exists chat_events (
  id bigserial primary key,
  session_id text not null,
  event_type text not null,   -- 'answered' | 'unanswered'
  question text not null,
  lead_email text,             -- set when the visitor shares an email
  created_at timestamptz default now()
);

-- Cosine-similarity search used by the "Retrieve chunks" node.
create or replace function match_documents(query_embedding vector(768), match_count int)
returns table (id bigint, content text, source_url text, source_name text, similarity float)
language sql stable as $$
  select id, content, source_url, source_name,
         1 - (embedding <=> query_embedding) as similarity
  from placidway_docs
  order by embedding <=> query_embedding
  limit match_count;
$$;
