# RAG GitHub Actions

[![Tests: Ingestion](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-ingest.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-ingest.yml) [![Tests: Query](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-query.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-query.yml) [![Black](https://github.com/jinglemansweep/rag-actions/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/black.yml) [![Flake8](https://github.com/jinglemansweep/rag-actions/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/flake8.yml) [![MyPy](https://github.com/jinglemansweep/rag-actions/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/mypy.yml)

![Logo](./docs/images/logo.png)

A collection of GitHub Actions that provide typical [Langchain](https://www.langchain.com/) RAG workflows such as content indexing, chunking and embedding. The resulting embeddings are then stored in [Supabase](https://supabase.com/) tables for retrieval and querying.

## Setup

Create a Supabase account and database and create required vector tables and functions using the provided [example SQL file](./supabase/setup.sql).

All workflows require the same base configuration, consisting of an OpenAI API Key, Supabase URL and API Key which should be created as GitHub secrets so they can be reused across multiple workflows.

## Ingest: Directory

This action can currently index text files and other unstructured documents, usually located in a directory within a Git repository.

Example Usage:

    - name: Ingest Directory
      uses: jinglemansweep/rag-actions/.github/actions/ingest-directory@main
      with:
        openai_api_key: ${{ secrets.OPENAI_API_KEY }}
        supabase_url: ${{ secrets.SUPABASE_URL }}
        supabase_key: ${{ secrets.SUPABASE_KEY }}
        supabase_table: "documents"
        ingest_dir: "./test/content"
        ingest_metadata: '{"github": {"run": "${{ github.run_id }}"}}'

## Ingest: Text

This action can currently index simple text fragments.

Example Usage:

    - name: Ingest Text
      uses: jinglemansweep/rag-actions/.github/actions/ingest-text@main
      with:
        openai_api_key: ${{ secrets.OPENAI_API_KEY }}
        supabase_url: ${{ secrets.SUPABASE_URL }}
        supabase_key: ${{ secrets.SUPABASE_KEY }}
        supabase_table: "documents"
        ingest_text: |
          Hello, this is some example text, generated dynamically
          by a GitHub Action Run ${{ github.run_id }}
        ingest_metadata: '{"github": {"run": "${{ github.run_id }}"}}'
