# pybliometrics-mcp

MCP server for pybliometrics - Access Scopus, ScienceDirect, and SciVal APIs through the Model Context Protocol.

## Overview

This MCP server provides tools to access scientific publication data through the pybliometrics library, which wraps Elsevier's Scopus, ScienceDirect, and SciVal APIs.

## Features

The server provides the following tools:

- **get_abstract**: Retrieve metadata for a scientific paper by DOI or Scopus ID
- **get_author**: Retrieve information about an author by their Scopus Author ID
- **get_affiliation**: Retrieve information about an institution by its Scopus Affiliation ID
- **search_authors**: Search for authors by name, affiliation, or other criteria
- **search_documents**: Search for documents/papers using Scopus advanced search

## Installation

### Prerequisites

1. **Python 3.10+** is required
2. **Scopus API Key**: You need an API key from Elsevier. Get one at https://dev.elsevier.com/

### Install the MCP server

```bash
cd pybliometrics-mcp
pip install -e .
```

### Configure pybliometrics

Before using the server, you need to configure pybliometrics with your API keys:

```bash
python -c "import pybliometrics; pybliometrics.scopus.utils.create_config()"
```

This will create a configuration file at `~/.config/pybliometrics.cfg` (or `%LOCALAPPDATA%/pybliometrics.cfg` on Windows).

Edit the configuration file to add your API key:

```ini
[Authentication]
APIKey = YOUR_API_KEY_HERE
```

## Usage

### Running the server

```bash
pybliometrics-mcp
```

The server uses stdio for communication, following the MCP protocol.

### Using with Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pybliometrics": {
      "command": "pybliometrics-mcp"
    }
  }
}
```

If you installed with `pip install -e .`, you may need to use the full path:

```json
{
  "mcpServers": {
    "pybliometrics": {
      "command": "python",
      "args": ["-m", "pybliometrics_mcp.server"]
    }
  }
}
```

Or specify the absolute path to the script:

```json
{
  "mcpServers": {
    "pybliometrics": {
      "command": "/path/to/pybliometrics-mcp/src/pybliometrics_mcp/server.py"
    }
  }
}
```

### Example Queries

Once connected, you can ask Claude:

- "Get me information about the paper with DOI 10.1016/j.softx.2019.100263"
- "Search for papers about machine learning published after 2020"
- "Get information about author with ID 7004212771"
- "Search for authors named John Kitchin"

## API Reference

### get_abstract

Retrieve metadata for a scientific paper.

**Parameters:**
- `identifier` (required): DOI or Scopus ID
- `view` (optional): View mode (default: "FULL")

**Example:**
```
DOI: 10.1016/j.softx.2019.100263
Scopus ID: 2-s2.0-85066652432
```

### get_author

Retrieve author information.

**Parameters:**
- `author_id` (required): Scopus Author ID

**Example:**
```
Author ID: 7004212771
```

### get_affiliation

Retrieve institution information.

**Parameters:**
- `affiliation_id` (required): Scopus Affiliation ID

**Example:**
```
Affiliation ID: 60027950
```

### search_authors

Search for authors.

**Parameters:**
- `query` (required): Scopus search query
- `max_results` (optional): Maximum results (default: 10)

**Example queries:**
```
AUTHLAST(Kitchin) AND AUTHFIRST(John)
AUTHLAST(Smith) AND AFFIL(MIT)
```

### search_documents

Search for documents.

**Parameters:**
- `query` (required): Scopus search query
- `max_results` (optional): Maximum results (default: 10)

**Example queries:**
```
TITLE(machine learning) AND PUBYEAR > 2020
KEY(deep learning) AND DOCTYPE(ar)
AU-ID(7004212771)
```

## Troubleshooting

### API Key Issues

If you get authentication errors:
1. Verify your API key is correct in `~/.config/pybliometrics.cfg`
2. Ensure you have access to Scopus (usually requires institutional access)
3. Check your API key quota at https://dev.elsevier.com/

### Import Errors

If you get import errors, ensure pybliometrics is installed:
```bash
pip install pybliometrics
```

### MCP Connection Issues

If Claude Desktop can't connect to the server:
1. Check that the server starts without errors: `pybliometrics-mcp`
2. Verify the path in your configuration is correct
3. Try using the full Python path in the configuration

## License

MIT License - see LICENSE file for details

## More Information

- pybliometrics documentation: https://pybliometrics.readthedocs.io
- Scopus API documentation: https://dev.elsevier.com/
- MCP specification: https://modelcontextprotocol.io
