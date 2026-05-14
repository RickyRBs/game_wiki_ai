# WikiQuest AI

WikiQuest AI is a lightweight game wiki assistant built with Streamlit. A user can ask a Stardew Valley question, and the app searches a small local wiki dataset before returning an answer. I wanted the project to feel like a useful player tool, not just a model demo. The answer is tied to wiki-style data, so the model is not only responding from memory.

## Project Background

Many game players use wikis to answer practical questions: where to find an item, which gift a character likes, how to prepare for a difficult area, or what to do first early in the game. A normal wiki search can be useful, but the player still has to choose the right page and read through the information. WikiQuest AI uses a different interface: the player asks a normal question, and the app searches the dataset for the closest wiki entries.

I chose Stardew Valley because its information is organized but still varied. The game has crops, villagers, tools, locations, fishing, mining, crafting, quests, and strategy. This made it a good subject for a small search-based AI project.

## Models

The project uses two Hugging Face model parts:

- `sentence-transformers/all-MiniLM-L6-v2` for meaning-based search. It turns the user's question and the wiki entries into vectors, then ranks entries by similarity.
- `google/flan-t5-small` for optional text generation. It receives the found wiki snippets and rewrites them into a more natural answer.

The application also includes fallback behavior:

- If the embedding model cannot load, the app falls back to TF-IDF search.
- If scikit-learn is not installed, it falls back to a small pure Python keyword search.
- If the generation model cannot load, the app falls back to a fixed template answer.

This fallback design makes the app easier to test locally and safer to deploy.

## Data

The dataset is stored in `data/stardew_wiki_seed.csv`.

Columns:

- `title`: wiki entry name
- `category`: topic such as Character, Item, Location, Farming, Fishing, Tool, Crafting, Quest, Strategy, or Combat
- `tags`: search keywords
- `content`: short summary used by the assistant
- `source_url`: source page for reference

The seed dataset includes entries about crops, tools, villagers, locations, fishing, combat, crafting machines, important items, and beginner strategy. The dataset is small on purpose, so it is easy to understand how the app searches it. A larger version of the project could scrape or manually add more wiki pages.

## Interface

The current interface is simple. The page uses a black background and a single centered input bar. The bar includes:

- an answer style selector
- a question input field
- an Ask button

If the user asks a clear question, the app answers directly. If the question is too vague or the search result is weak, the app shows four more specific question options. This helps avoid giving a weak answer when the assistant does not have enough context.

## Run Locally

If you already have the packages installed, you can run:

```bash
streamlit run app.py
```

If you are not familiar with Python projects, use these steps.

### 1. Download the project

You can download the repository from GitHub, or clone it with:

```bash
git clone https://github.com/RickyRBs/game_wiki_ai.git
cd game_wiki_ai
```

### 2. Create a virtual environment

A virtual environment keeps this project's packages separate from other Python projects on the computer.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After this command, the terminal should show `(.venv)` at the start of the line.

### 3. Install the packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Streamlit, pandas, Hugging Face tools, and the model packages.

### 4. Start the app

```bash
streamlit run app.py
```

Streamlit will print a local address, usually:

```text
http://localhost:8501
```

Open that address in a browser. Then type a Stardew Valley question into the center input bar.

### 5. Stop the app

Go back to the terminal and press:

```text
Control + C
```

### 6. Leave the virtual environment

When you are done working, run:

```bash
deactivate
```

## Beginner Notes

Here are a few terms that may be unfamiliar:

- `README.md`: the main project explanation file.
- `requirements.txt`: the list of Python packages the app needs.
- `runtime.txt`: tells Streamlit Cloud which Python version to use.
- `app.py`: the main Streamlit page.
- `data/stardew_wiki_seed.csv`: the local wiki dataset.
- `src/wiki_engine.py`: the search and answer logic.
- `venv` or `.venv`: a local Python environment for this project.
- `localhost`: a web address that runs only on your own computer.

The Hugging Face models may take time to load the first time. If the model packages are not installed or the model cannot load, the app still has backup search methods. This is why the app can still run in a simpler mode.

## Common Problems

If `streamlit` is not found, make sure the virtual environment is active and run:

```bash
pip install -r requirements.txt
```

If the app opens but answers feel too simple, the Hugging Face generation model may not be loaded. The app will still answer from the dataset with the backup answer format.

If deployment is slow, it is usually because Hugging Face and PyTorch packages are large. The first build often takes longer than later runs.

## Deployment

This repository can be deployed to Streamlit Community Cloud:

1. Push the project to GitHub.
2. Create a new Streamlit app.
3. Set the app file to `app.py`.
4. Make sure `requirements.txt` and `runtime.txt` are in the same project folder.

The first deployment may take longer because the Hugging Face models have to download.

## Reflection

The project changed a lot while I was building it. My first version looked more like a data dashboard than a game assistant. It had a sidebar, category filters, a dataset table, source cards, and several controls on the page. Those pieces were useful for testing, but they made the app feel busy. For a player, the important action is just asking a question. I ended up cutting most of the visible interface and keeping one centered input bar. That made the project feel more direct.

The hardest design choice was how much freedom to give the model. A game wiki assistant should not make up item locations, gift preferences, or strategy details. If the app answers a Stardew Valley question incorrectly, it stops being useful. Because of that, I treated the dataset as the main source of knowledge. The embedding model finds the closest wiki entries first, and the answer is built from that context. The generation model is only there to make the response easier to read. This was useful because it made the data feel necessary. The CSV is not just something included for the assignment; it controls what the assistant can answer.

I also ran into problems with local packages. The full version uses Hugging Face tools, but my local environment did not always have the same packages installed. `sentence-transformers`, `transformers`, `torch`, and `scikit-learn` can also make deployment slower or more likely to fail. I added backup search methods so the app would still run even when the main model was not available. The best version uses the Hugging Face embedding model, but the app can fall back to TF-IDF or a simple keyword method. That made the project more stable during testing.

The interface took more time than I expected. Streamlit is easy to start with, but changing its built-in parts is not always simple. The default buttons, select boxes, and text inputs had rounded corners, extra spacing, and layout behavior that did not match the plain black interface I wanted. I had to adjust CSS, refresh the browser, and test the result many times. Making the answer style selector, question input, and Ask button look like one continuous bar was especially tricky.

Another issue was vague questions. If someone types "help" or "strategy", the app can search the dataset, but the result may not match what the user actually wants. Instead of forcing an answer, I added a follow-up step. When the question is too broad or the search score is weak, the app offers four more specific questions. This makes the interaction clearer and prevents the assistant from pretending it has enough information.

If I had more time, I would expand the wiki dataset and add more pages from Stardew Valley. I would also like to test the answers against the source snippets more carefully, so the generated response stays close to the found data.
