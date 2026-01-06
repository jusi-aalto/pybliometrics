# pybliometrics-mcp

MCP (Model Context Protocol) server for accessing Scopus, ScienceDirect, and SciVal APIs through pybliometrics.

## Overview

This MCP server exposes pybliometrics functionality as tools that AI assistants (like Claude) can use to search academic literature, retrieve publication metadata, analyze citations, and assess research impact.

## Features

### Core Capabilities

1. **Literature Search** - Search Scopus with complex queries
2. **Paper Retrieval** - Get full metadata, abstracts, and references
3. **Citation Analysis** - Track citation counts and patterns over time
4. **Author Profiles** - Retrieve researcher metrics and affiliations
5. **Institution Data** - Access institutional research metrics
6. **Journal Information** - Look up journal details by ISSN
7. **Altmetrics** - Get PlumX alternative impact metrics

### Available Tools

- `scopus_search` - Search publications with boolean queries
- `get_abstract` - Retrieve complete paper metadata and references
- `get_citation_overview` - Get citation metrics and time series
- `get_author` - Fetch author profiles with h-index and publications
- `search_authors` - Find authors by name or affiliation
- `get_affiliation` - Get institutional details
- `search_affiliations` - Search for institutions
- `get_serial_title` - Look up journal information by ISSN
- `get_plumx_metrics` - Get alternative impact metrics
- `configure_api` - Set up API keys

## Installation

### 1. Install pybliometrics with MCP support

```bash
cd /path/to/pybliometrics
pip install -e .
pip install mcp
```

### 2. Get a Scopus API Key

1. Go to https://dev.elsevier.com
2. Create an account (free for academic users)
3. Register an application to get an API key
4. Note: For abstract retrieval, your IP address must be registered with institutional access

### 3. Configure API Keys

Run pybliometrics initialization:

```bash
python3 -c "import pybliometrics; pybliometrics.init()"
```

This will create a config file (usually at `~/.pybliometrics/config.ini`). Edit it to add your API key:

```ini
[Authentication]
APIKey = YOUR_API_KEY_HERE
```

## Usage with Claude Desktop

### Configure Claude Desktop

Add to your Claude Desktop MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pybliometrics": {
      "command": "python3",
      "args": ["/path/to/pybliometrics/mcp_server.py"]
    }
  }
}
```

Replace `/path/to/pybliometrics` with the actual path to this repository.

### Restart Claude Desktop

After configuring, restart Claude Desktop to load the MCP server.

## Usage Examples

Once configured, you can ask Claude to use pybliometrics directly:

### Example 1: Find Supporting Citations

```
I'm writing about CRISPR applications in agriculture.
Find recent highly-cited papers on this topic.
```

Claude will use `scopus_search` with a query like:
```
TITLE-ABS-KEY("CRISPR" AND "agriculture") AND PUBYEAR > 2020
```

### Example 2: Verify a Reference

```
Check if this reference is correct:
Smith, J. et al. (2023). "Machine learning in drug discovery", Nature, 10.1038/nature12345
```

Claude will use `get_abstract` with the DOI to verify the information.

### Example 3: Citation Network Analysis

```
I have this paper: 10.1016/j.softx.2019.100263
Show me what papers it cites and find the most influential ones.
```

Claude will:
1. Use `get_abstract` with `view='REF'` to get references
2. Use `get_citation_overview` to get citation counts
3. Rank papers by citations

### Example 4: Author Impact Assessment

```
What's the h-index and recent work of author ID 57209617104?
```

Claude will use `get_author` to retrieve comprehensive author metrics.

### Example 5: Systematic Literature Review

```
I need all papers on "deep learning" AND "medical imaging" from 2020-2024
with at least 50 citations.
```

Claude will construct a complex Scopus query and retrieve results.

## Tool Details

### scopus_search

Search Scopus with complex boolean queries.

**Parameters:**
- `query` (required): Scopus search query
- `max_results` (optional): Maximum results to return (default 25, max 5000)
- `download` (optional): Whether to download full results (default true)
- `verbose` (optional): Show progress bar (default false)

**Query Syntax Examples:**
```
Simple: "machine learning"
Fields: TITLE("CRISPR") AND KEY("agriculture")
Author: AUTH("Einstein, A.")
Date: PUBYEAR > 2020 AND PUBYEAR < 2024
Combined: TITLE-ABS-KEY("deep learning") AND AUTH("Smith") AND PUBYEAR = 2023
```

**Returns:** List of documents with full metadata including titles, authors, DOIs, abstracts, citations, etc.

### get_abstract

Retrieve complete publication metadata.

**Parameters:**
- `identifier` (required): DOI, Scopus ID, PubMed ID, or PII
- `view` (optional): Detail level - META, FULL, or REF (default FULL)
- `id_type` (optional): Identifier type if not auto-detectable

**Views:**
- `META`: Basic metadata only
- `FULL`: Complete information with abstract
- `REF`: Includes all references (use for citation analysis)

**Returns:** Comprehensive document data including abstract, authors with ORCIDs, affiliations, references, funding, keywords, etc.

### get_citation_overview

Get citation metrics over time.

**Parameters:**
- `identifier` (required): Scopus ID(s), DOI(s) - single or array
- `start` (optional): Start year (YYYY)
- `end` (optional): End year (YYYY)
- `id_type` (optional): Identifier type

**Returns:** Citation counts by year, total citations, h-index, author info, citation growth patterns.

### get_author

Retrieve researcher profile.

**Parameters:**
- `author_id` (required): Scopus Author ID (numeric)
- `view` (optional): LIGHT, STANDARD, or ENHANCED (default ENHANCED)

**Returns:** H-index, citation counts, publications, current/historical affiliations, co-authors, subject areas, name variants.

### search_authors

Find authors by name or criteria.

**Parameters:**
- `query` (required): Author search query
- `max_results` (optional): Max results (default 25)

**Query Examples:**
```
AUTHLAST(Einstein) AND AUTHFIRST(Albert)
AUTHLAST(Smith) AND AFFIL(Harvard)
AUTHLAST(Johnson) AND SUBJAREA(COMP)
```

**Returns:** List of authors with IDs, names, affiliations, document/citation counts.

### Other Tools

Similar parameter patterns for:
- `get_affiliation` - Institution details by ID
- `search_affiliations` - Find institutions
- `get_serial_title` - Journal info by ISSN
- `get_plumx_metrics` - Alternative metrics

## Use Cases

### 1. Finding Supporting Citations

Ask Claude to search for papers related to your manuscript paragraph and suggest appropriate citations.

### 2. Systematic Literature Reviews

Construct complex queries to find all relevant papers on a topic, filtered by date, citations, journals, etc.

### 3. Citation Network Analysis

Start with a paper and trace its intellectual genealogy by analyzing what it cites and identifying seminal works.

### 4. Reference Verification

Check manuscript references for accuracy, completeness, and correct metadata.

### 5. Research Impact Assessment

Analyze author metrics, citation patterns, and research output for tenure reviews or grant applications.

### 6. Institutional Analysis

Compare research output across institutions or departments.

## Architecture

The MCP server:
1. Exposes pybliometrics classes as MCP tools
2. Returns complete JSON objects with all available properties
3. Lets Claude (or other AI assistants) compose primitive operations
4. Handles serialization of NamedTuples and complex objects
5. Provides error handling and helpful error messages

## Limitations

1. **API Rate Limits**: Scopus API has rate limits (varies by subscription)
2. **IP Restrictions**: Abstract retrieval requires institutional IP access
3. **Data Completeness**: Some fields may be missing from Scopus data
4. **Citation Delay**: Citations may lag by weeks/months
5. **Result Limits**: Searches limited to 5000 results without cursor

## Troubleshooting

### Server won't start

Check that:
- Python 3.10+ is installed
- MCP SDK is installed: `pip install mcp`
- pybliometrics is installed: `pip install -e .`

### API authentication errors

Verify:
- API key is correctly set in config file
- Config file exists at `~/.pybliometrics/config.ini`
- API key is valid (check https://dev.elsevier.com)

### No abstract content returned

Ensure:
- Your IP address has institutional access to Scopus
- Use `view='FULL'` parameter
- Some older papers may not have abstracts in Scopus

### Rate limit errors

- Wait before retrying
- Reduce `max_results` parameter
- Consider upgrading API subscription

## Development

### Running Tests

```bash
cd pybliometrics
python3 -m pytest
```

### Adding New Tools

1. Add new tool definition to `list_tools()` in `mcp_server.py`
2. Add handler in `call_tool()`
3. Update this documentation

## Resources

- **pybliometrics documentation**: https://pybliometrics.readthedocs.io
- **Scopus API docs**: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
- **MCP documentation**: https://modelcontextprotocol.io
- **Get API key**: https://dev.elsevier.com

## License

MIT License (same as pybliometrics)

## Contributing

Contributions welcome! Please see the main pybliometrics repository for contribution guidelines.
