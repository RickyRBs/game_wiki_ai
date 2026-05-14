# WikiQuest AI

WikiQuest AI is a lightweight game wiki assistant built with Streamlit. The application lets a user ask a Stardew Valley question, searches a curated local wiki dataset, and returns an answer based on the most relevant retrieved entries. The goal of the project is to make a small AI tool that feels useful to a player, while still keeping the model behavior grounded in visible data instead of relying only on a language model's memory.

## Project Background

Many game players use wikis to answer practical questions: where to find an item, which gift a character likes, how to prepare for a difficult area, or what to prioritize early in the game. A normal wiki search can be useful, but the player still has to choose the right page and read through the information. WikiQuest AI explores a different interface: the player asks a natural language question, and the app searches the dataset for the most relevant wiki entries.

I chose Stardew Valley because its knowledge is structured but still varied. The game has crops, villagers, tools, locations, fishing, mining, crafting, quests, and strategy. This made it a good subject for a small retrieval-based AI project.

## Models

The project uses two Hugging Face model layers:

- `sentence-transformers/all-MiniLM-L6-v2` for semantic search. It embeds the user's question and the wiki entries, then ranks entries by similarity.
- `google/flan-t5-small` for optional text generation. It receives retrieved wiki snippets and rewrites them into a more natural answer.

The application also includes fallback behavior:

- If the embedding model cannot load, the app falls back to TF-IDF search.
- If scikit-learn is unavailable, it falls back to a small pure Python keyword search.
- If the generation model cannot load, the app falls back to a deterministic template answer.

This fallback design makes the app easier to test locally and safer to deploy.

## Data

The dataset is stored in `data/stardew_wiki_seed.csv`.

Columns:

- `title`: wiki entry name
- `category`: topic such as Character, Item, Location, Farming, Fishing, Tool, Crafting, Quest, Strategy, or Combat
- `tags`: search keywords
- `content`: curated summary used by the assistant
- `source_url`: source page for reference

The seed dataset includes entries about crops, tools, villagers, locations, fishing, combat, crafting machines, important items, and beginner strategy. The dataset is intentionally small and curated so the retrieval process is understandable. A larger version of the project could scrape or manually add more wiki pages.

## Interface

The current interface is intentionally minimal. The page uses a black background and a single centered input bar. The bar includes:

- an answer style selector
- a question input field
- an Ask button

If the user asks a clear question, the app answers directly. If the question is too vague or the search confidence is low, the app shows four more specific question options. This helps avoid giving a weak answer when the assistant does not have enough context.

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

## Deployment

This repository can be deployed to Streamlit Community Cloud:

1. Push the project to GitHub.
2. Create a new Streamlit app.
3. Set the app file to `app.py`.
4. Make sure `requirements.txt` and `runtime.txt` are in the same project folder.

The first deployment may take longer because the Hugging Face models have to download.

## Reflection

Building this project involved several design and technical challenges. At the beginning, the project was a simple wiki search page with a dataset preview, filters, and source cards. That version worked technically, but the interface felt too much like a dashboard and not enough like a focused AI tool. I gradually removed extra interface elements and moved toward a single centered question bar. This made the app easier to understand immediately: the user only has to ask a question.

One major challenge was deciding how much the model should generate. A fully generative chatbot could sound more natural, but it might invent game details that are not in the dataset. Since game wiki information needs to be accurate, I decided to use retrieval first. The app searches the curated CSV, ranks relevant entries, and then builds an answer from that retrieved context. This makes the answer more reliable and also makes the project easier to explain: the dataset is not just decoration, it is the source of the assistant's knowledge.

Another challenge was dependency reliability. Hugging Face models can be large, and local environments do not always have `sentence-transformers`, `transformers`, `torch`, or `scikit-learn` installed. To solve this, I added fallback layers. If the embedding model cannot load, the app can still search with TF-IDF. If that is also unavailable, it uses a basic keyword similarity method. If the generation model cannot load, the app still returns a template-based answer. This was important because the project needs to run both locally and when deployed online.

The Streamlit interface also took a lot of iteration. Some early versions had sidebars, dataset tables, large buttons, and source panels. Those made the app look cluttered. I simplified the design to a black background with a single input bar. I also had to adjust CSS carefully because Streamlit components have default spacing, rounded corners, and layout behavior. Making the style selector, text input, and Ask button look like one continuous bar required custom CSS and repeated browser previews.

A final problem was vague user input. If someone types only "help" or "strategy", the assistant should not pretend it knows exactly what the user means. I added a confidence and clarification system. If the question is too broad or the retrieval score is low, the app shows four specific question choices. This makes the experience more useful because the assistant guides the user toward a clearer query instead of producing a weak answer.

If I continued developing this project, I would expand the dataset, add more Stardew Valley pages, and possibly support multiple games. I would also improve the evaluation process by checking whether generated answers stay faithful to the retrieved source snippets.
