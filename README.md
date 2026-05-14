# WikiQuest AI

WikiQuest AI is a lightweight game wiki assistant built with Streamlit. A user can ask a Stardew Valley question, and the app searches a curated local wiki dataset before returning an answer. I wanted the project to feel like a small useful player tool, not just a model demo. The answer is tied to wiki-style data, so the model is not only responding from memory.

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

The project changed a lot while I was building it. My first version looked more like a data dashboard than a game assistant. It had a sidebar, category filters, a dataset table, source cards, and several controls on the page. Those pieces were useful for testing, but they made the app feel busy. For a player, the important action is just asking a question. I ended up cutting most of the visible interface and keeping one centered input bar. That made the project feel more direct.

The hardest design decision was how much freedom to give the model. A game wiki assistant should not make up item locations, gift preferences, or strategy details. If the app answers a Stardew Valley question incorrectly, it stops being useful. Because of that, I treated the dataset as the main source of knowledge. The embedding model finds the closest wiki entries first, and the answer is built from that context. The generation model is only there to make the response easier to read. This was a useful lesson for me because it made the data feel necessary. The CSV is not just something included for the assignment; it controls what the assistant can answer.

I also ran into problems with local dependencies. The full version uses Hugging Face tools, but my local environment did not always have the same packages installed. `sentence-transformers`, `transformers`, `torch`, and `scikit-learn` can also make deployment slower or more fragile. I added fallback search methods so the app would still run even when the main model was unavailable. The best version uses the Hugging Face embedding model, but the app can fall back to TF-IDF or a simple keyword method. That made the project more stable during testing.

The interface took more time than I expected. Streamlit is easy to start with, but customizing its components is not always simple. The default buttons, select boxes, and text inputs had rounded corners, extra spacing, and layout behavior that did not match the minimal black interface I wanted. I had to repeatedly adjust CSS, refresh the browser, and test the result. Making the answer style selector, question input, and Ask button look like one continuous bar was especially tricky.

Another issue was vague questions. If someone types "help" or "strategy", the app technically can search the dataset, but the result may not match what the user actually wants. Instead of forcing an answer, I added a clarification step. When the question is too broad or the retrieval score is weak, the app offers four more specific questions. This makes the interaction clearer and prevents the assistant from pretending it has enough information.

If I had more time, I would expand the wiki dataset and add more pages from Stardew Valley. I would also like to test the answers against the source snippets more carefully, so the generated response stays faithful to the retrieved data.
