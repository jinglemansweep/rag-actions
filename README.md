# RAG GitHub Actions

[![Docker Build/Push](https://github.com/jinglemansweep/rag-actions/actions/workflows/docker.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/docker.yml) [![Tests: Ingestion](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-ingest.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-ingest.yml) [![Tests: Inferrence](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-infer.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/test-infer.yml) [![Black](https://github.com/jinglemansweep/rag-actions/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/black.yml) [![Flake8](https://github.com/jinglemansweep/rag-actions/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/flake8.yml) [![MyPy](https://github.com/jinglemansweep/rag-actions/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/rag-actions/actions/workflows/mypy.yml)

![Logo](./docs/images/logo.png)

A collection of GitHub Actions that provide typical [Langchain](https://www.langchain.com/) RAG workflows such as content indexing, chunking and embedding. The resulting embeddings are then stored in [Supabase](https://supabase.com/) tables for retrieval and querying.

## Setup

Create a Supabase account and database and create required vector tables and functions using the provided [example SQL file](./supabase/setup.sql).

All workflows require the same base configuration, consisting of an OpenAI API Key, Supabase URL and API Key which should be created as GitHub secrets so they can be reused across multiple workflows.

## Ingestion

Inputs:

* `openai_api_key`: OpenAI API key
* `embedding_model`: Embedding model alias *(default: `text-embedding-3-small`)*
* `supabase_url`: Supabase URL
* `supabase_key`: Supabase API key
* `supabase_table`: Supabase table
* `metadata`: Metadata **(dict)**
* `args`: General arguments **(dict)**
* `loader_class`: Document loader class alias *(default: `markdown`)*
* `loader_args`: Document loader class arguments *(default: `{}`)*
* `chunker_class`: Chunker class alias *(default: `recursive_character`)*
* `chunker_args`: Chunker class arguments *(default: `{"chunk_size": 1000, "chunk_overlap": 200}`)*
* `user_agent`: User agent string *(default: recent Firefox/Linux)*

Markdown Directory Example:

    - name: Markdown Directory Ingestion
      uses: jinglemansweep/rag-actions/.github/actions/ingest-loader@main
      with:
        openai_api_key: ${{ secrets.OPENAI_API_KEY }}
        supabase_url: ${{ secrets.SUPABASE_URL }}
        supabase_key: ${{ secrets.SUPABASE_KEY }}
        supabase_table: ${{ vars.SUPABASE_TABLE }}
        metadata: |
          {
            "collection": "${{ vars.SUPABASE_COLLECTION }}",
            "github": {
              "run": "${{ github.run_id }}"
            }
          }
        args: |
          {
            "path": "./test/content/test",
            "glob": "**/*.md"
          }
        loader_class: "markdown"
        loader_args: '{}'
        chunker_class: "recursive_character"
        chunker_args: '{"chunk_size": 1000, "chunk_overlap": 200}'

RSS Feed Example:

      - name: RSS Feed Ingestion
        uses: jinglemansweep/rag-actions/.github/actions/ingest-loader@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          supabase_url: ${{ secrets.SUPABASE_URL }}
          supabase_key: ${{ secrets.SUPABASE_KEY }}
          supabase_table: ${{ vars.SUPABASE_TABLE }}
          metadata: |
            {
              "collection": "${{ vars.SUPABASE_COLLECTION }}",
              "feed": "news",
              "source": "bbc"
            }
          loader_class: "rss"
          loader_args: |
            {
              "urls": [
                "https://feeds.bbci.co.uk/news/rss.xml"
              ]
            }

Web Page Example:

      - name: Web Page Ingestion
        uses: jinglemansweep/rag-actions/.github/actions/ingest-loader@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          supabase_url: ${{ secrets.SUPABASE_URL }}
          supabase_key: ${{ secrets.SUPABASE_KEY }}
          supabase_table: ${{ vars.SUPABASE_TABLE }}
          metadata: |
            {
              "collection": "${{ vars.SUPABASE_COLLECTION }}"
            }
          loader_class: "web"
          loader_args: |
            {
              "web_path": "https://www.bbc.co.uk"
            }

# Inferrence

Inputs:

* `openai_api_key`: OpenAI API key
* `embedding_model`: Embedding model alias *(default: `text-embedding-3-small`)*
* `chat_model`: Chat model alias *(default: `gpt-4o-mini`)*
* `supabase_url`: Supabase URL
* `supabase_key`: Supabase API key
* `supabase_table`: Supabase table
* `supabase_filter`: Supabase filter *(default: `{}`)*
* `chat_prompt`: Chat prompt *(default: `You are a helpful assistant. Answer the question based on the provided context.`)*
* `query`: Query for RAG retrieval
* `top_k`: Number of top results to return *(default: `5`)*
* `output_file`: Output file path

Chat Example:

      - name: Chat
        uses: jinglemansweep/rag-actions/.github/actions/infer-chat@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          supabase_url: ${{ secrets.SUPABASE_URL }}
          supabase_key: ${{ secrets.SUPABASE_KEY }}
          supabase_table: ${{ vars.SUPABASE_TABLE }}
          supabase_filter: '{"collection": "${{ vars.SUPABASE_COLLECTION }}"}'
          chat_model: "gpt-4o-mini"
          chat_prompt: "You are a helpful assistant. Answer the question based on the provided context."
          query: "UK News"
          top_k: "5"
          output_file: "./uknews.md
