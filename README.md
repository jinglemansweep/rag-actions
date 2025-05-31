# RAG GitHub Actions

[![.github/workflows/test.yml](https://github.com/jinglemansweep/rag-actions/actions/workflows/test.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/test.yml)

A collection of GitHub Actions that provide typical Langchain RAG workflows such as content indexing, chunking and embedding. The resulting embeddings are then stored in [Supabase](https://supabase.com/) tables.

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

