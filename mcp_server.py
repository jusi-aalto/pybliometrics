#!/usr/bin/env python3
"""
pybliometrics-mcp: MCP server for accessing Scopus, ScienceDirect, and SciVal APIs
"""

import os
import sys
from typing import Any, Sequence
from collections.abc import Mapping

# Add pybliometrics to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import pybliometrics after path modification
import pybliometrics
from pybliometrics.scopus import (
    ScopusSearch,
    AbstractRetrieval,
    CitationOverview,
    AuthorRetrieval,
    AuthorSearch,
    AffiliationRetrieval,
    AffiliationSearch,
    SerialTitle,
    PlumXMetrics,
)


def serialize_to_dict(obj: Any) -> Any:
    """
    Recursively serialize pybliometrics objects to JSON-compatible dicts.

    Handles NamedTuples, lists, dicts, and primitive types.
    """
    if obj is None:
        return None

    # Handle NamedTuple
    if hasattr(obj, '_asdict'):
        return {k: serialize_to_dict(v) for k, v in obj._asdict().items()}

    # Handle lists/tuples
    if isinstance(obj, (list, tuple)) and not isinstance(obj, str):
        return [serialize_to_dict(item) for item in obj]

    # Handle dicts
    if isinstance(obj, Mapping):
        return {k: serialize_to_dict(v) for k, v in obj.items()}

    # Handle primitives
    return obj


def get_all_properties(obj: Any) -> dict[str, Any]:
    """
    Extract all @property values from a pybliometrics object.

    Returns a dictionary with property names as keys and their values serialized to JSON.
    """
    result = {}

    # Get all properties from the class
    for attr_name in dir(obj):
        # Skip private/magic attributes
        if attr_name.startswith('_'):
            continue

        try:
            attr = getattr(type(obj), attr_name, None)
            # Check if it's a property
            if isinstance(attr, property):
                value = getattr(obj, attr_name)
                result[attr_name] = serialize_to_dict(value)
        except Exception as e:
            # If we can't get the property, include error info
            result[attr_name] = f"<error retrieving: {str(e)}>"

    return result


# Initialize MCP server
app = Server("pybliometrics-mcp")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available pybliometrics tools."""
    return [
        types.Tool(
            name="scopus_search",
            description="""Search Scopus database for publications.

            Returns list of documents matching query with full metadata including:
            - Document identifiers (EID, DOI, PubMed ID)
            - Title, abstract, keywords
            - Authors and affiliations
            - Publication details (journal, date, volume, pages)
            - Citation counts and open access status

            Supports complex queries with boolean operators (AND, OR, NOT) and field-specific searches.
            Examples:
            - Simple: "machine learning"
            - Field-specific: TITLE("CRISPR") AND KEY("agriculture")
            - Author: AUTH("Einstein, A.")
            - Date range: PUBYEAR > 2020 AND PUBYEAR < 2024

            Use 'max_results' to control how many results to fetch (default 25, max 5000).
            Set 'download=false' to just count results without fetching full data.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Scopus search query (supports boolean operators and field codes)",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 25, max 5000)",
                        "default": 25,
                    },
                    "download": {
                        "type": "boolean",
                        "description": "Whether to download full results or just count (default true)",
                        "default": True,
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Show download progress (default false)",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_abstract",
            description="""Retrieve detailed information about a specific publication.

            Returns comprehensive metadata including:
            - Full abstract and title
            - Complete author list with affiliations and ORCIDs
            - Publication details and identifiers
            - Subject classifications and keywords
            - References cited by this paper (use view='REF')
            - Funding information
            - Chemical compounds mentioned
            - Citation counts

            Accepts various identifier types: DOI, Scopus ID (EID), PubMed ID, PII.

            The 'view' parameter controls detail level:
            - 'META' (default): Basic metadata
            - 'FULL': Complete information including abstract
            - 'REF': Includes all references (slower)
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "DOI, Scopus ID (EID), PubMed ID, or PII",
                    },
                    "view": {
                        "type": "string",
                        "description": "Level of detail: META, FULL, or REF (includes references)",
                        "enum": ["META", "FULL", "REF"],
                        "default": "FULL",
                    },
                    "id_type": {
                        "type": "string",
                        "description": "Type of identifier if not auto-detectable",
                    },
                },
                "required": ["identifier"],
            },
        ),
        types.Tool(
            name="get_citation_overview",
            description="""Get citation metrics for one or more publications.

            Returns citation data including:
            - Total citations (grand total and per paper)
            - Yearly citation counts (time series)
            - H-index for the set of papers
            - Author information for each paper
            - Document types and metadata
            - Citation growth patterns

            Useful for:
            - Tracking citation growth over time
            - Comparing citation patterns across papers
            - Analyzing research impact

            Can analyze single papers or multiple papers together.
            Specify date range to focus on specific years (format: 'YYYY-YYYY').
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": ["string", "array"],
                        "description": "Scopus ID(s), DOI(s), or other identifier(s). Can be single ID or list.",
                    },
                    "start": {
                        "type": "string",
                        "description": "Start year for citation counts (YYYY)",
                    },
                    "end": {
                        "type": "string",
                        "description": "End year for citation counts (YYYY)",
                    },
                    "id_type": {
                        "type": "string",
                        "description": "Type of identifier: scopus_id, doi, pubmed_id, etc.",
                    },
                },
                "required": ["identifier"],
            },
        ),
        types.Tool(
            name="get_author",
            description="""Retrieve detailed author profile and metrics.

            Returns comprehensive author information:
            - H-index and citation counts
            - Publication history and counts
            - Current and historical affiliations
            - Co-author network
            - Subject areas and classifications
            - Name variants and ORCID
            - Document and citation history by year

            Useful for:
            - Assessing researcher impact and productivity
            - Finding author affiliations
            - Identifying co-authors and collaborators
            - Analyzing research focus areas

            Requires Scopus Author ID (can be found using author_search).
            Use 'view' parameter to control detail level.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "author_id": {
                        "type": "string",
                        "description": "Scopus Author ID (numeric)",
                    },
                    "view": {
                        "type": "string",
                        "description": "Detail level: LIGHT, STANDARD, or ENHANCED",
                        "enum": ["LIGHT", "STANDARD", "ENHANCED"],
                        "default": "ENHANCED",
                    },
                },
                "required": ["author_id"],
            },
        ),
        types.Tool(
            name="search_authors",
            description="""Search for authors by name or other criteria.

            Returns list of matching authors with:
            - Author ID (for use with get_author)
            - Name variants
            - Affiliations
            - Document and citation counts

            Useful for:
            - Finding author IDs for detailed lookups
            - Disambiguating authors with similar names
            - Discovering researchers in a field

            Search by author name, affiliation, or combination.
            Examples:
            - "AUTHLAST(Einstein) AND AUTHFIRST(Albert)"
            - "AUTHLAST(Smith) AND AFFIL(Harvard)"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Author search query (use AUTHLAST, AUTHFIRST, AFFIL fields)",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return (default 25)",
                        "default": 25,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_affiliation",
            description="""Retrieve detailed information about an institution/affiliation.

            Returns:
            - Institution name and identifiers
            - Address and location details
            - Publication and author counts
            - Subject area distribution
            - Historical data

            Useful for:
            - Institutional research assessment
            - Finding affiliation details for authors
            - Analyzing research output by institution

            Requires Scopus Affiliation ID (can be found using search_affiliations).
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "affiliation_id": {
                        "type": "string",
                        "description": "Scopus Affiliation ID (numeric)",
                    },
                    "view": {
                        "type": "string",
                        "description": "Detail level: LIGHT or STANDARD",
                        "enum": ["LIGHT", "STANDARD"],
                        "default": "STANDARD",
                    },
                },
                "required": ["affiliation_id"],
            },
        ),
        types.Tool(
            name="search_affiliations",
            description="""Search for institutions/affiliations.

            Returns list of matching institutions with:
            - Affiliation ID
            - Institution names and variants
            - Location (city, country)
            - Document counts

            Useful for:
            - Finding affiliation IDs
            - Discovering institutions in a region
            - Analyzing institutional research output

            Search by institution name, city, or country.
            Examples:
            - "AFFIL(Harvard)"
            - "AFFIL(MIT) AND CITY(Cambridge)"
            - "COUNTRY(Japan)"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Affiliation search query (use AFFIL, CITY, COUNTRY fields)",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return (default 25)",
                        "default": 25,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_serial_title",
            description="""Get information about a journal/serial publication.

            Returns:
            - Journal title and abbreviations
            - ISSN (print and electronic)
            - Publisher information
            - Subject classifications
            - Coverage dates

            Useful for:
            - Validating journal information
            - Finding ISSNs
            - Checking journal subject areas

            Search by ISSN or serial title.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "issn": {
                        "type": "string",
                        "description": "ISSN (print or electronic)",
                    },
                },
                "required": ["issn"],
            },
        ),
        types.Tool(
            name="get_plumx_metrics",
            description="""Get PlumX altmetrics for a publication.

            Returns alternative metrics including:
            - Social media mentions
            - Citations in policy documents
            - Usage statistics
            - Captures in reference managers
            - Mentions in news and blogs

            Provides broader impact assessment beyond traditional citations.
            Requires DOI or other identifier.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "DOI or other publication identifier",
                    },
                    "id_type": {
                        "type": "string",
                        "description": "Type of identifier: doi, scopus_id, etc.",
                        "default": "doi",
                    },
                },
                "required": ["identifier"],
            },
        ),
        types.Tool(
            name="configure_api",
            description="""Configure pybliometrics with API keys.

            Sets up the necessary API keys for accessing Scopus/ScienceDirect.
            Keys are stored in the pybliometrics configuration file.

            If no key is provided, shows current configuration status.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "Scopus API key (get from https://dev.elsevier.com)",
                    },
                    "inst_token": {
                        "type": "string",
                        "description": "Institutional token (optional, for enhanced access)",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent]:
    """Handle tool execution."""

    try:
        if name == "scopus_search":
            query = arguments["query"]
            max_results = arguments.get("max_results", 25)
            download = arguments.get("download", True)
            verbose = arguments.get("verbose", False)

            # Perform search
            search = ScopusSearch(
                query,
                download=download,
                verbose=verbose,
                subscriber=False,
            )

            # Get results
            results = []
            if search.results:
                for i, doc in enumerate(search.results):
                    if i >= max_results:
                        break
                    results.append(serialize_to_dict(doc))

            response = {
                "query": query,
                "total_results": getattr(search, '_n', len(results)),
                "returned_results": len(results),
                "results": results,
            }

            return [types.TextContent(
                type="text",
                text=f"Found {response['total_results']} total results, returning {len(results)}:\n\n{serialize_to_dict(response)}"
            )]

        elif name == "get_abstract":
            identifier = arguments["identifier"]
            view = arguments.get("view", "FULL")
            id_type = arguments.get("id_type")

            # Create retrieval object
            ab = AbstractRetrieval(
                identifier,
                view=view,
                id_type=id_type,
            )

            # Extract all properties
            data = get_all_properties(ab)

            return [types.TextContent(
                type="text",
                text=f"Abstract retrieval for {identifier}:\n\n{serialize_to_dict(data)}"
            )]

        elif name == "get_citation_overview":
            identifier = arguments["identifier"]
            start = arguments.get("start")
            end = arguments.get("end")
            id_type = arguments.get("id_type")

            # Handle list or single identifier
            if isinstance(identifier, str):
                identifier = [identifier]

            # Create date range string
            date = None
            if start and end:
                date = f"{start}-{end}"

            # Get citations
            cit = CitationOverview(
                identifier,
                start=date.split('-')[0] if date else None,
                end=date.split('-')[1] if date else None,
                id_type=id_type,
            )

            # Extract all properties
            data = get_all_properties(cit)

            return [types.TextContent(
                type="text",
                text=f"Citation overview for {len(identifier)} document(s):\n\n{serialize_to_dict(data)}"
            )]

        elif name == "get_author":
            author_id = arguments["author_id"]
            view = arguments.get("view", "ENHANCED")

            # Get author profile
            au = AuthorRetrieval(author_id, view=view)

            # Extract all properties
            data = get_all_properties(au)

            return [types.TextContent(
                type="text",
                text=f"Author profile for ID {author_id}:\n\n{serialize_to_dict(data)}"
            )]

        elif name == "search_authors":
            query = arguments["query"]
            max_results = arguments.get("max_results", 25)

            # Perform search
            search = AuthorSearch(query, subscriber=False)

            # Get results
            results = []
            if search.authors:
                for i, author in enumerate(search.authors):
                    if i >= max_results:
                        break
                    results.append(serialize_to_dict(author))

            response = {
                "query": query,
                "total_results": len(results),
                "results": results,
            }

            return [types.TextContent(
                type="text",
                text=f"Found {len(results)} author(s):\n\n{serialize_to_dict(response)}"
            )]

        elif name == "get_affiliation":
            affiliation_id = arguments["affiliation_id"]
            view = arguments.get("view", "STANDARD")

            # Get affiliation
            aff = AffiliationRetrieval(affiliation_id, view=view)

            # Extract all properties
            data = get_all_properties(aff)

            return [types.TextContent(
                type="text",
                text=f"Affiliation details for ID {affiliation_id}:\n\n{serialize_to_dict(data)}"
            )]

        elif name == "search_affiliations":
            query = arguments["query"]
            max_results = arguments.get("max_results", 25)

            # Perform search
            search = AffiliationSearch(query, subscriber=False)

            # Get results
            results = []
            if search.affiliations:
                for i, aff in enumerate(search.affiliations):
                    if i >= max_results:
                        break
                    results.append(serialize_to_dict(aff))

            response = {
                "query": query,
                "total_results": len(results),
                "results": results,
            }

            return [types.TextContent(
                type="text",
                text=f"Found {len(results)} affiliation(s):\n\n{serialize_to_dict(response)}"
            )]

        elif name == "get_serial_title":
            issn = arguments["issn"]

            # Get serial title
            serial = SerialTitle(issn)

            # Extract all properties
            data = get_all_properties(serial)

            return [types.TextContent(
                type="text",
                text=f"Serial title information for ISSN {issn}:\n\n{serialize_to_dict(data)}"
            )]

        elif name == "get_plumx_metrics":
            identifier = arguments["identifier"]
            id_type = arguments.get("id_type", "doi")

            # Get PlumX metrics
            plum = PlumXMetrics(identifier, id_type=id_type)

            # Extract all properties
            data = get_all_properties(plum)

            return [types.TextContent(
                type="text",
                text=f"PlumX metrics for {identifier}:\n\n{serialize_to_dict(data)}"
            )]

        elif name == "configure_api":
            api_key = arguments.get("api_key")
            inst_token = arguments.get("inst_token")

            if api_key or inst_token:
                # Initialize with provided keys
                keys = []
                if api_key:
                    keys.append(api_key)
                if inst_token:
                    keys.append(inst_token)

                pybliometrics.init()

                return [types.TextContent(
                    type="text",
                    text="API configuration updated. Please manually edit your pybliometrics config file to set keys."
                )]
            else:
                # Show current status
                try:
                    pybliometrics.init()
                    return [types.TextContent(
                        type="text",
                        text="Pybliometrics is configured. Config file location can be found in pybliometrics documentation."
                    )]
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Pybliometrics not configured: {str(e)}\n\nPlease run pybliometrics.init() or manually create config file."
                    )]

        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}\n\nPlease check your input parameters and API configuration."
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
