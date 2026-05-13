# Reflection

For this final project, I wanted to build something that felt like a real user-facing tool instead of only a model demo. A game wiki assistant is a useful fit because players often ask practical questions: where to find an item, how to prepare for an area, what gifts a character likes, or how to plan early-game progress.

The first design decision was to keep the dataset controlled. Instead of scraping an entire wiki immediately, I created a curated CSV with entries across farming, fishing, villagers, tools, items, locations, combat, quests, crafting, and strategy. This made it easier to understand what the model was retrieving and how the interface should present sources.

The main retrieval model is `sentence-transformers/all-MiniLM-L6-v2`, a lightweight Hugging Face embedding model. I chose an embedding model because the app needs to match user questions to wiki entries even when the exact words are different. For example, a user might ask about making money in spring, and the app should still find entries about spring crops, early-game strategy, or artisan machines.

I also added an optional Hugging Face text generation model, `google/flan-t5-small`, to make the final answer sound more natural. The generation step only receives retrieved wiki snippets, which keeps the answer connected to the dataset. If the model cannot load, the app still works with a template answer. This fallback design was important because deployment environments can have different dependency or memory limits.

The interface is built with Streamlit because it is fast to prototype and easy to deploy from a GitHub repository. I changed the app from a simple search form into a chat-style wiki assistant with example questions, category filters, source cards, similarity scores, and a dataset explorer. Showing sources is important because it makes the AI more transparent: the user can see what information the answer came from.

The main challenge was balancing AI behavior with reliability. A fully generative chatbot might sound more natural, but it could also invent game details. This prototype uses retrieval first, then generation second. If I continued developing it, I would expand the dataset with more wiki pages, add automatic scraping and cleaning, support multiple games, and improve answer evaluation by checking whether generated responses stay faithful to the retrieved source snippets.
