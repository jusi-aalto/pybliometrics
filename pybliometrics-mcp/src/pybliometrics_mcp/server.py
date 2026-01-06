#!/usr/bin/env python3
"""
MCP Server for pybliometrics - Access Scopus, ScienceDirect, and SciVal APIs
"""

import json
import logging
from typing import Any

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import pybliometrics modules
try:
    from pybliometrics.scopus import (
        AbstractRetrieval,
        AuthorRetrieval,
        AffiliationRetrieval,
        AuthorSearch,
        ScopusSearch,
    )
    import pybliometrics
except ImportError as e:
    raise ImportError(
        "pybliometrics is not installed. Install it with: pip install pybliometrics"
    ) from e

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pybliometrics-mcp")

# Create server instance
app = Server("pybliometrics-mcp")


def format_author(author) -> dict:
    """Format author object to dict"""
    return {
        "auid": getattr(author, "auid", None),
        "indexed_name": getattr(author, "indexed_name", None),
        "surname": getattr(author, "surname", None),
        "given_name": getattr(author, "given_name", None),
        "affiliation": getattr(author, "affiliation", None),
    }


def format_affiliation(aff) -> dict:
    """Format affiliation object to dict"""
    return {
        "id": getattr(aff, "id", None),
        "parent": getattr(aff, "parent", None),
        "type": getattr(aff, "type", None),
        "relationship": getattr(aff, "relationship", None),
        "preferred_name": getattr(aff, "preferred_name", None),
        "country": getattr(aff, "country", None),
        "city": getattr(aff, "city", None),
    }


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_abstract",
            description="Retrieve metadata for a scientific paper/abstract by DOI or Scopus ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "DOI (e.g., '10.1016/j.softx.2019.100263') or Scopus ID (e.g., '2-s2.0-85066652432')",
                    },
                    "view": {
                        "type": "string",
                        "description": "The view of the file that should be downloaded (default: 'FULL')",
                        "default": "FULL",
                    },
                },
                "required": ["identifier"],
            },
        ),
        types.Tool(
            name="get_author",
            description="Retrieve information about an author by their Scopus Author ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "author_id": {
                        "type": "string",
                        "description": "Scopus Author ID (e.g., '7004212771')",
                    },
                },
                "required": ["author_id"],
            },
        ),
        types.Tool(
            name="get_affiliation",
            description="Retrieve information about an affiliation/institution by its Scopus Affiliation ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "affiliation_id": {
                        "type": "string",
                        "description": "Scopus Affiliation ID (e.g., '60027950')",
                    },
                },
                "required": ["affiliation_id"],
            },
        ),
        types.Tool(
            name="search_authors",
            description="Search for authors by name, affiliation, or other criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query using Scopus syntax (e.g., 'AUTHLAST(Kitchin) AND AUTHFIRST(John)')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="search_documents",
            description="Search for documents/papers using Scopus advanced search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query using Scopus syntax (e.g., 'TITLE(machine learning) AND PUBYEAR > 2020')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_abstract":
            identifier = arguments["identifier"]
            view = arguments.get("view", "FULL")

            logger.info(f"Retrieving abstract for: {identifier}")
            ab = AbstractRetrieval(identifier, view=view)

            result = {
                "title": ab.title,
                "doi": ab.doi,
                "eid": ab.eid,
                "publication_name": ab.publicationName,
                "coverDate": ab.coverDate,
                "description": ab.description,
                "authors": [format_author(a) for a in (ab.authors or [])],
                "citedby_count": ab.citedby_count,
                "subject_areas": [
                    {"area": area.area, "abbreviation": area.abbreviation, "code": area.code}
                    for area in (ab.subject_areas or [])
                ],
                "abstract": ab.abstract,
                "keywords": ab.authkeywords,
                "source_type": ab.srctype,
                "aggregationType": ab.aggregationType,
                "volume": ab.volume,
                "issueIdentifier": ab.issueIdentifier,
                "article_number": ab.article_number,
                "pageRange": ab.pageRange,
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_author":
            author_id = arguments["author_id"]

            logger.info(f"Retrieving author: {author_id}")
            au = AuthorRetrieval(author_id)

            result = {
                "identifier": au.identifier,
                "indexed_name": au.indexed_name,
                "surname": au.surname,
                "given_name": au.given_name,
                "document_count": au.document_count,
                "citation_count": au.citation_count,
                "h_index": au.h_index,
                "affiliation_current": [format_affiliation(a) for a in (au.affiliation_current or [])],
                "orcid": au.orcid,
                "subject_areas": [
                    {"area": area.area, "abbreviation": area.abbreviation, "code": area.code}
                    for area in (au.subject_areas or [])
                ],
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_affiliation":
            affiliation_id = arguments["affiliation_id"]

            logger.info(f"Retrieving affiliation: {affiliation_id}")
            aff = AffiliationRetrieval(affiliation_id)

            result = {
                "affiliation_id": aff.affiliation_id,
                "name": aff.affiliation_name,
                "city": aff.city,
                "country": aff.country,
                "author_count": aff.author_count,
                "document_count": aff.document_count,
                "postal_code": aff.postal_code,
                "address": aff.address,
                "org_type": aff.org_type,
                "org_domain": aff.org_domain,
                "org_URL": aff.org_URL,
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_authors":
            query = arguments["query"]
            max_results = arguments.get("max_results", 10)

            logger.info(f"Searching authors: {query}")
            search = AuthorSearch(query)

            results = []
            for i, author in enumerate(search.authors or []):
                if i >= max_results:
                    break
                results.append({
                    "eid": author.eid,
                    "name": author.given_name + " " + author.surname if author.given_name and author.surname else author.surname,
                    "surname": author.surname,
                    "given_name": author.given_name,
                    "document_count": author.document_count,
                    "affiliation": author.affiliation,
                    "city": author.city,
                    "country": author.country,
                })

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "search_documents":
            query = arguments["query"]
            max_results = arguments.get("max_results", 10)

            logger.info(f"Searching documents: {query}")
            search = ScopusSearch(query)

            results = []
            for i, doc in enumerate(search.results or []):
                if i >= max_results:
                    break
                results.append({
                    "eid": doc.eid,
                    "doi": doc.doi,
                    "title": doc.title,
                    "creator": doc.creator,
                    "publicationName": doc.publicationName,
                    "coverDate": doc.coverDate,
                    "citedby_count": doc.citedby_count,
                    "author_names": doc.author_names,
                    "author_ids": doc.author_ids,
                    "author_afids": doc.author_afids,
                })

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting pybliometrics MCP server")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
