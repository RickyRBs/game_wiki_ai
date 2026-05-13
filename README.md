# WikiQuest AI

WikiQuest AI is a lightweight game wiki assistant built with Streamlit. The app lets a user ask a Stardew Valley question, retrieves the most relevant entries from a curated wiki dataset, and then answers with source snippets visible beside the chat.

The project is designed as a small retrieval-augmented AI application: the model does not answer from memory alone. It searches a local dataset first, then uses the retrieved context to produce an answer.

## Models

The project uses two Hugging Face model layers:

- `sentence-transformers/all-MiniLM-L6-v2` for semantic search. It embeds the user's question and wiki entries, then ranks entries by similarity.
- `google/flan-t5-small` for optional text generation. It receives the retrieved wiki snippets and rewrites them into a more natural answer.

Fallback behavior is built in for reliability:

- If the embedding model cannot load, the app falls back to TF-IDF search.
- If scikit-learn is unavailable, it falls back to a small pure Python keyword search.
- If the generation model cannot load, it falls back to a deterministic template answer.

This makes the app usable locally even before the full Hugging Face dependencies are installed.

## Data

The dataset is stored in `data/stardew_wiki_seed.csv`.

Columns:

- `title`: wiki entry name
- `category`: topic such as Character, Item, Location, Farming, Fishing, Tool, Crafting, Quest, Strategy, or Combat
- `tags`: search keywords
- `content`: curated summary used by the assistant
- `source_url`: source page for reference

The seed dataset covers crops, tools, characters, locations, fishing, combat, crafting machines, important items, and beginner strategy. A stronger version of the project could expand this CSV with scraped wiki pages or a larger manually curated set.

## Interface

The Streamlit interface includes:

- a chat-style question and answer flow
- example question buttons
- category filtering
- answer style controls
- retrieved source cards with similarity scores
- a dataset explorer table
- visual styling inspired by a game wiki tool

## Run Locally

Quick run:

```bash
streamlit run app.py
```

Full setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

This repository can be deployed to Streamlit Community Cloud:

1. Push the project to GitHub.
2. Create a new Streamlit app.
3. Set the app file to `app.py`.
4. Make sure `requirements.txt` and `runtime.txt` are in the same project folder.

The first deployment may take longer because the Hugging Face models have to download.
