create table my_table_name (
  id bigserial primary key,
  content text,
  metadata jsonb,
  chunk_hash text unique,
  embedding double precision[]
);
