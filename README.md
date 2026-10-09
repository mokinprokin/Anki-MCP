# 🗂️ Anki MCP Server

[![MCP](https://img.shields.io/badge/MCP-Protocol-blue?style=flat-square)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/managed%20by-uv-261230?style=flat-square&logo=astral&logoColor=white)](https://astral.sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

An asynchronous **Model Context Protocol (MCP)** server that connects AI assistants (Claude Desktop, Cursor, Cline, LM Studio, etc.) directly to your local **[Anki](https://apps.ankiweb.net/)** flashcard collection via [AnkiConnect](https://git.sr.ht/~foosoft/anki-connect).

Turn any LLM into an autonomous language tutor, note organizer, and flashcard manager that inspects your decks, prevents duplicates, formats vocabulary, and writes cards without leaving your chat or IDE.

---

## ⚡ Highlights

- **Full AnkiConnect Integration:** Create, update, tag, and delete notes, inspect decks, read study cards, and trigger AnkiWeb synchronization.
- **Built for AI Agents:** Includes a battle-tested [`instruction.md`](instruction.md) prompt for seamless zero-friction vocabulary workflows.
- **Strict Pydantic Validation:** All inputs and domain models are validated against strict Pydantic schemas.
- **Zero-Setup Execution with `uvx`:** Run directly from GitHub without cloning or managing virtual environments manually.
- **Safe Network Layer:** Custom async HTTP transport powered by `aiohttp` with built-in retry mechanisms and connection-drop guards.

---

## 🧠 Recommended Agent Instructions

This server is designed to work in synergy with autonomous AI agents. 

We provide a comprehensive, production-ready system prompt file:
👉 **[instruction.md](instruction.md)**

It instructs the model how to:
1. Automatically differentiate between single words, synonym clusters, and idioms.
2. Validate existing notes before adding to prevent duplicates.
3. Generate phonetics (IPA), parts of speech, and natural cloze/context examples.
4. Call tools autonomously without asking for confirmation every turn.

---

## 🛠️ Prerequisites

1. **Anki Desktop:** Install and keep Anki running on your computer.
2. **AnkiConnect Addon:** 
   - Open Anki $\rightarrow$ *Tools* $\rightarrow$ *Add-ons* $\rightarrow$ *Get Add-ons...*
   - Enter code: `2055492159`
   - Restart Anki. AnkiConnect runs locally on `http://127.0.0.1:8765`.
3. **[uv](https://docs.astral.sh/uv/):** The fast Python package manager.

---

## 🚀 Getting Started

You can run the server either directly from GitHub using `uvx` (recommended) or from a local clone.

### Option 1: Direct Run from GitHub (Zero Installation)

Add the following to your MCP client configuration (e.g. `claude_desktop_config.json` or Cline):

```json
{
  "mcpServers": {
    "anki-github": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/mokinprokin/Anki-MCP.git",
        "anki_mcp_server"
      ]
    }
  }
}
```

Option 2: Local Development

1.  Clone the repository:

    git clone https://github.com/mokinprokin/Anki-MCP.git
    cd Anki-MCP

2.  Install dependencies with uv:

    uv sync

3.  Configure your MCP client using local paths:
```json
    {
      "mcpServers": {
        "anki-agent": {
          "command": "uv",
          "args": [
            "--directory",
            "C:/path/to/Anki-MCP",
            "run",
            "anki_mcp_server"
          ]
        }
      }
    }
```
🧰 Available MCP Tools

| Tool                | Description                                                                 |
| :------------------ | :-------------------------------------------------------------------------- |
| `add_card_to_anki`  | Creates a new flashcard in the specified deck.                              |
| `update_note`       | Updates fields (`Front`, `Back`, etc.) of an existing note by ID.           |
| `delete_notes`      | Permanently deletes notes and their associated cards.                       |
| `add_tags`          | Attaches space-separated tags to specified note IDs.                        |
| `create_deck`       | Creates a new empty deck in Anki.                                           |
| `list_decks`        | Lists all deck names currently available in Anki.                           |
| `get_notes_in_deck` | Retrieves sanitized notes from a deck without scheduling noise.             |
| `get_cards_in_deck` | Retrieves cards including spaced repetition statistics (`interval`, `due`). |
| `sync_anki`         | Pushes local changes to AnkiWeb cloud.                                      |

⚙️ Configuration & Environment

Configuration is managed via Pydantic Settings. You can customize runtime
parameters via a .env file or directly inside your client's "env" block:

# .env.example
ANKI_CONNECT_URL=http://127.0.0.1:8765
DEFAULT_DECK=English
REQUEST_TIMEOUT=5
INSTRUCTIONS_FILENAME=instruction.md

Example setting custom env in client JSON:
```json
{
  "mcpServers": {
    "anki": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mokinprokin/Anki-MCP.git", "anki_mcp_server"]
    }
  }
}
```
🧪 Testing with MCP Inspector

You can test the server locally inside your browser without connecting an LLM:

npx @modelcontextprotocol/inspector uv run anki_mcp_server

📄 License

This project is licensed under the MIT License.
