# RAG GitHub Actions

[![.github/workflows/test.yml](https://github.com/jinglemansweep/rag-actions/actions/workflows/test.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/test.yml) [![Black](https://github.com/jinglemansweep/rag-actions/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/black.yml) [![Flake8](https://github.com/jinglemansweep/rag-actions/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/flake8.yml) [![MyPy](https://github.com/jinglemansweep/rag-actions/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/mypy.yml)

![Logo](./docs/images/logo.png)

A collection of GitHub Actions that provide typical [Langchain](https://www.langchain.com/) RAG workflows such as content indexing, chunking and embedding. The resulting embeddings are then stored in [Supabase](https://supabase.com/) tables for retrieval and querying.

## Setup

Create a Supabase account and database and create required vector tables using the provided [example SQL file](./supabase/table.sql).

## Indexer Action

This action can currently index text files and other unstructured documents, usually located in a directory within a Git repository. An OpenAI API key is required as well as a Supabase URL and API key which should be created as GitHub secrets for use in the workflows.

Example Usage:

    - name: Run RAG Indexer Action
      uses: jinglemansweep/rag-actions/.github/actions/rag-indexer@main
      with:
        openai_api_key: ${{ secrets.OPENAI_API_KEY }}
        supabase_url: ${{ secrets.SUPABASE_URL }}
        supabase_key: ${{ secrets.SUPABASE_KEY }}
        supabase_table: "rag_chunks"
        embedding_model: "text-embedding-ada-002"
        chunk_size: "500"
        chunk_overlap: "50"
        docs_dir: "./docs"
