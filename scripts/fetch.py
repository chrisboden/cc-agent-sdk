#!/usr/bin/env python3
"""
Claude Agent SDK documentation fetcher for cc-agent-sdk skill.

Fetches official Agent SDK docs and updates the skill's references.
Run from anywhere - automatically detects skill directory structure.

Usage:
    python fetch.py                 # Fetch docs and validate SKILL.md
    python fetch.py --validate      # Only check SKILL.md refs vs files
    python fetch.py --update-skill  # Add new files to SKILL.md

Environment overrides:
    AGENT_SDK_DOCS_LLMS_URL        # Use a specific llms.txt URL
    AGENT_SDK_DOCS_SITEMAP_URL     # Use a specific sitemap URL
"""

import argparse
import hashlib
import json
import logging
import os
import random
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Known sources to try
LLMS_URLS = [
    "https://platform.claude.com/docs/llms.txt",
    "https://code.claude.com/docs/llms.txt",
    "https://docs.anthropic.com/docs/llms.txt",
    "https://docs.anthropic.com/llms.txt",
]

SITEMAP_URLS = [
    "https://platform.claude.com/docs/sitemap.xml",
    "https://code.claude.com/docs/sitemap.xml",
    "https://docs.anthropic.com/sitemap.xml",
]

AGENT_SDK_PATH_MARKERS = [
    "/docs/en/agent-sdk/",
    "/en/docs/agent-sdk/",
    "/agent-sdk/",
]

MANIFEST_FILE = "docs_manifest.json"
SKILL_FILE = "SKILL.md"
CUSTOM_FILES = {
    "openrouter-support.md",
}

# Headers for requests
HEADERS = {
    'User-Agent': 'Claude-Agent-SDK-Docs-Fetcher/1.0 (cc-agent-sdk-skill)',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_RETRY_DELAY = 30


def get_skill_dir() -> Path:
    """Get the skill directory (parent of scripts/)."""
    return Path(__file__).parent.parent


def get_references_dir() -> Path:
    """Get the references directory."""
    return get_skill_dir() / "references"


def load_manifest() -> dict:
    """Load the manifest of previously fetched files."""
    manifest_path = get_references_dir() / MANIFEST_FILE
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            if "files" not in manifest:
                manifest["files"] = {}
            return manifest
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")
    return {"files": {}, "last_updated": None}


def save_manifest(manifest: dict) -> None:
    """Save the manifest of fetched files."""
    manifest_path = get_references_dir() / MANIFEST_FILE
    manifest["last_updated"] = datetime.now().isoformat()
    manifest["description"] = "Claude Agent SDK documentation manifest for cc-agent-sdk skill."
    manifest_path.write_text(json.dumps(manifest, indent=2))


def url_to_safe_filename(url_or_path: str) -> str:
    """Convert a URL or path to a safe filename."""
    if "//" in url_or_path:
        path = urlparse(url_or_path).path
    else:
        path = url_or_path

    path = path.rstrip('/')

    if path.endswith('.md'):
        path = path[:-3]
    elif path.endswith('.html'):
        path = path[:-5]

    slug = None
    for marker in AGENT_SDK_PATH_MARKERS:
        if marker in path:
            slug = path.split(marker, 1)[1]
            break

    if not slug:
        slug = path.strip('/').split('/')[-1]

    slug = slug.strip('/') if slug else "index"
    if not slug:
        slug = "index"

    safe_name = slug.replace('/', '__')
    if not safe_name.endswith('.md'):
        safe_name += '.md'
    return safe_name


def normalize_doc_url(url: str) -> Tuple[str, str]:
    """Normalize a doc URL to (original_url, markdown_url)."""
    url = url.strip()
    if url.endswith('/'):
        url = url[:-1]

    if url.endswith('.md'):
        original_url = url[:-3]
        markdown_url = url
    elif url.endswith('.html'):
        original_url = url[:-5]
        markdown_url = f"{original_url}.md"
    else:
        original_url = url
        markdown_url = f"{url}.md"

    return original_url, markdown_url


def is_agent_sdk_url(url: str) -> bool:
    """Check if URL points to Agent SDK docs."""
    return any(marker in url for marker in AGENT_SDK_PATH_MARKERS)


def parse_llms_txt(text: str, base_url: str) -> List[str]:
    """Parse llms.txt and return filtered Agent SDK URLs."""
    urls = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('-'):
            line = line.lstrip('-').strip()

        if line.startswith('/'):
            line = base_url + line

        if line.startswith('http') and is_agent_sdk_url(line):
            urls.append(line)
    return urls


def discover_pages_from_llms(session: requests.Session) -> List[str]:
    """Discover Agent SDK pages from llms.txt."""
    env_llms = os.getenv("AGENT_SDK_DOCS_LLMS_URL")
    llms_urls = [env_llms] + LLMS_URLS if env_llms else LLMS_URLS

    for llms_url in llms_urls:
        if not llms_url:
            continue
        try:
            logger.info(f"Trying llms.txt: {llms_url}")
            resp = session.get(llms_url, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                continue
            base = f"{urlparse(llms_url).scheme}://{urlparse(llms_url).netloc}"
            urls = parse_llms_txt(resp.text, base)
            if urls:
                logger.info(f"Discovered {len(urls)} Agent SDK pages from llms.txt")
                return sorted(list(set(urls)))
        except Exception as e:
            logger.warning(f"Failed to fetch {llms_url}: {e}")
            continue

    return []


def fetch_sitemap_urls(session: requests.Session, sitemap_url: str, seen: Optional[Set[str]] = None) -> List[str]:
    """Fetch URLs from a sitemap or sitemap index."""
    if seen is None:
        seen = set()

    if sitemap_url in seen:
        return []
    seen.add(sitemap_url)

    resp = session.get(sitemap_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    try:
        parser = ET.XMLParser(forbid_dtd=True, forbid_entities=True, forbid_external=True)
        root = ET.fromstring(resp.content, parser=parser)
    except TypeError:
        root = ET.fromstring(resp.content)

    tag = root.tag.lower()
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Sitemap index
    if 'sitemapindex' in tag:
        urls = []
        for loc_elem in root.findall('.//ns:loc', namespace):
            if loc_elem.text:
                urls.extend(fetch_sitemap_urls(session, loc_elem.text, seen))
        return urls

    # Standard urlset sitemap
    urls = []
    for loc_elem in root.findall('.//ns:loc', namespace):
        if loc_elem.text:
            urls.append(loc_elem.text)

    if not urls:
        # Fallback without namespace
        for loc_elem in root.findall('.//loc'):
            if loc_elem.text:
                urls.append(loc_elem.text)

    return urls


def discover_pages_from_sitemap(session: requests.Session) -> List[str]:
    """Discover Agent SDK pages from sitemap."""
    env_sitemap = os.getenv("AGENT_SDK_DOCS_SITEMAP_URL")
    sitemap_urls = [env_sitemap] + SITEMAP_URLS if env_sitemap else SITEMAP_URLS

    for sitemap_url in sitemap_urls:
        if not sitemap_url:
            continue
        try:
            logger.info(f"Trying sitemap: {sitemap_url}")
            urls = fetch_sitemap_urls(session, sitemap_url)
            if not urls:
                continue
            agent_urls = [u for u in urls if is_agent_sdk_url(u)]
            if agent_urls:
                logger.info(f"Discovered {len(agent_urls)} Agent SDK pages from sitemap")
                return sorted(list(set(agent_urls)))
        except Exception as e:
            logger.warning(f"Failed to fetch {sitemap_url}: {e}")
            continue

    return []


def get_fallback_pages() -> List[str]:
    """Fallback list of essential Agent SDK pages."""
    return [
        "https://platform.claude.com/docs/en/agent-sdk/overview",
        "https://platform.claude.com/docs/en/agent-sdk/quickstart",
        "https://platform.claude.com/docs/en/agent-sdk/python",
        "https://platform.claude.com/docs/en/agent-sdk/typescript",
        "https://platform.claude.com/docs/en/agent-sdk/permissions",
        "https://platform.claude.com/docs/en/agent-sdk/settings",
        "https://platform.claude.com/docs/en/agent-sdk/sessions",
        "https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode",
        "https://platform.claude.com/docs/en/agent-sdk/structured-outputs",
        "https://platform.claude.com/docs/en/agent-sdk/mcp",
        "https://platform.claude.com/docs/en/agent-sdk/custom-tools",
        "https://platform.claude.com/docs/en/agent-sdk/hooks",
        "https://platform.claude.com/docs/en/agent-sdk/subagents",
        "https://platform.claude.com/docs/en/agent-sdk/skills",
        "https://platform.claude.com/docs/en/agent-sdk/slash-commands",
        "https://platform.claude.com/docs/en/agent-sdk/plugins",
        "https://platform.claude.com/docs/en/agent-sdk/todo-tracking",
        "https://platform.claude.com/docs/en/agent-sdk/cost-tracking",
        "https://platform.claude.com/docs/en/agent-sdk/hosting",
        "https://platform.claude.com/docs/en/agent-sdk/secure-deployment",
        "https://platform.claude.com/docs/en/agent-sdk/modifying-system-prompts",
        "https://platform.claude.com/docs/en/agent-sdk/migration-guide",
    ]


def discover_doc_urls(session: requests.Session) -> List[str]:
    """Discover all Agent SDK documentation pages."""
    urls = discover_pages_from_llms(session)
    if urls:
        return urls

    urls = discover_pages_from_sitemap(session)
    if urls:
        return urls

    logger.warning("Falling back to static Agent SDK page list")
    return get_fallback_pages()


def clean_mdx_content(content: str) -> str:
    """Remove JSX/React components from MDX content and convert to plain markdown."""

    # Remove export const component definitions (multi-line)
    def remove_export_components(text: str) -> str:
        result = []
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r'^export\s+const\s+\w+\s*=', line):
                i += 1
                while i < len(lines):
                    if re.match(r'^\};\s*$', lines[i]):
                        i += 1
                        break
                    i += 1
            else:
                result.append(line)
                i += 1
        return '\n'.join(result)

    content = remove_export_components(content)

    # Convert <Warning>...</Warning> to blockquote
    content = re.sub(
        r'<Warning>\s*(.*?)\s*</Warning>',
        r'> **Warning:** \1',
        content,
        flags=re.DOTALL
    )

    # Convert <Note>...</Note> to blockquote
    content = re.sub(
        r'<Note>\s*(.*?)\s*</Note>',
        r'> **Note:** \1',
        content,
        flags=re.DOTALL
    )

    # Convert <Tip>...</Tip> to blockquote
    content = re.sub(
        r'<Tip>\s*(.*?)\s*</Tip>',
        r'> **Tip:** \1',
        content,
        flags=re.DOTALL
    )

    # Remove <Tabs> wrapper
    content = re.sub(r'</?Tabs.*?>', '', content)

    # Convert <Tab title="..."> to heading
    content = re.sub(
        r'<Tab\s+title="([^"]+)">',
        r'\n#### \1\n',
        content
    )
    content = re.sub(r'</Tab>', '', content)

    # Convert <CodeGroup> to separator
    content = re.sub(r'</?CodeGroup.*?>', '', content)

    # Convert <CardGroup> and <Card> to list items
    content = re.sub(r'</?CardGroup.*?>', '', content)

    def convert_card(match):
        title = match.group(1)
        href = match.group(2)
        body = match.group(3).strip()
        parts = [f"- **{title}**"]
        if href:
            parts.append(f"  - {href}")
        if body:
            for line in body.split('\n'):
                parts.append(f"  - {line.strip()}")
        return '\n'.join(parts)

    content = re.sub(
        r'<Card\s+title="([^"]+)"\s+icon="[^"]*"\s+href="([^"]+)">\s*(.*?)\s*</Card>',
        convert_card,
        content,
        flags=re.DOTALL
    )

    # Convert <Steps>...<Step title="..."> to numbered lists
    def convert_steps(match):
        steps_content = match.group(1)
        step_pattern = r'<Step\s+title="([^"]+)">\s*(.*?)\s*</Step>'
        steps = re.findall(step_pattern, steps_content, flags=re.DOTALL)
        if not steps:
            return ''
        result_lines = []
        for idx, (title, body) in enumerate(steps, 1):
            result_lines.append(f"{idx}. **{title}**")
            body_lines = body.strip().split('\n')
            for line in body_lines:
                result_lines.append(f"   {line}")
            result_lines.append('')
        return '\n'.join(result_lines)

    content = re.sub(
        r'<Steps>\s*(.*?)\s*</Steps>',
        convert_steps,
        content,
        flags=re.DOTALL
    )

    # Remove self-closing JSX component tags like <ComponentName ... />
    content = re.sub(r'<[A-Z][a-zA-Z]*(?:\s+[^>]*)?\s*/>', '', content)

    # Remove import statements
    content = re.sub(r'^import\s+.*?[\'"];?\s*$', '', content, flags=re.MULTILINE)

    # Clean up excessive blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    return content.strip()


def validate_markdown_content(content: str, filename: str) -> None:
    """Validate that content is proper markdown."""
    if not content or content.startswith('<!DOCTYPE') or '<html' in content[:100]:
        raise ValueError("Received HTML instead of markdown")

    if len(content.strip()) < 50:
        raise ValueError(f"Content too short ({len(content)} bytes)")

    lines = content.split('\n')
    markdown_indicators = ['# ', '## ', '### ', '```', '- ', '* ', '1. ', '[', '**', '_', '> ']

    indicator_count = 0
    for line in lines[:50]:
        for indicator in markdown_indicators:
            if line.strip().startswith(indicator) or indicator in line:
                indicator_count += 1
                break

    if indicator_count < 3:
        raise ValueError(f"Content doesn't appear to be markdown (only {indicator_count} indicators)")


def fetch_markdown_url(doc_url: str, session: requests.Session) -> Tuple[str, str, str]:
    """Fetch markdown content with retry logic."""
    original_url, markdown_url = normalize_doc_url(doc_url)
    filename = url_to_safe_filename(original_url)

    logger.info(f"Fetching: {markdown_url} -> {filename}")

    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(markdown_url, headers=HEADERS, timeout=30, allow_redirects=True)

            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            content = response.text

            original_len = len(content)
            content = clean_mdx_content(content)
            if len(content) < original_len:
                logger.info(f"Cleaned MDX content: {original_len} -> {len(content)} bytes")

            validate_markdown_content(content, filename)

            logger.info(f"Successfully fetched {filename} ({len(content)} bytes)")
            return filename, content, original_url

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {filename}: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = min(RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY)
                jittered_delay = delay * random.uniform(0.5, 1.0)
                time.sleep(jittered_delay)
            else:
                raise Exception(f"Failed to fetch {filename} after {MAX_RETRIES} attempts: {e}")

        except ValueError as e:
            logger.error(f"Content validation failed for {filename}: {e}")
            raise


def save_markdown_file(filename: str, content: str) -> str:
    """Save markdown content and return its hash."""
    file_path = get_references_dir() / filename
    file_path.write_text(content, encoding='utf-8')
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    logger.info(f"Saved: {filename}")
    return content_hash


def cleanup_old_files(current_files: Set[str], manifest: dict) -> None:
    """Remove files that were previously fetched but no longer exist."""
    previous_files = set(manifest.get("files", {}).keys())
    files_to_remove = previous_files - current_files

    protected_files = {MANIFEST_FILE} | CUSTOM_FILES

    for filename in files_to_remove:
        if filename in protected_files:
            continue
        file_path = get_references_dir() / filename
        if file_path.exists():
            logger.info(f"Removing obsolete file: {filename}")
            file_path.unlink()


def get_skill_md_references() -> Set[str]:
    """Parse SKILL.md and extract all referenced files."""
    skill_path = get_skill_dir() / SKILL_FILE
    if not skill_path.exists():
        return set()

    content = skill_path.read_text()
    pattern = r'`?references/([^`\s]+\.(?:md|json))`?'
    matches = re.findall(pattern, content)
    return set(matches)


def validate_skill_md(fetched_files: Set[str]) -> Dict[str, List[str]]:
    """Validate SKILL.md references against fetched files."""
    referenced = get_skill_md_references()

    orphaned = referenced - fetched_files - {MANIFEST_FILE} - CUSTOM_FILES
    unreferenced = fetched_files - referenced - {MANIFEST_FILE}

    return {
        "orphaned": sorted(list(orphaned)),
        "unreferenced": sorted(list(unreferenced)),
        "custom": sorted(list(referenced & CUSTOM_FILES)),
    }


def update_skill_md_uncategorized(new_files: List[str]) -> None:
    """Append new files to an Uncategorized section in SKILL.md."""
    if not new_files:
        return

    skill_path = get_skill_dir() / SKILL_FILE
    content = skill_path.read_text()

    if "### Uncategorized (New)" not in content:
        uncategorized_section = "\n\n### Uncategorized (New)\n\n"
        uncategorized_section += "<!-- Review and move these to appropriate sections -->\n\n"
    else:
        uncategorized_section = ""

    for filename in new_files:
        uncategorized_section += f"- `references/{filename}` - (new, needs categorization)\n"

    content = content.rstrip() + uncategorized_section
    skill_path.write_text(content)
    logger.info(f"Added {len(new_files)} new files to Uncategorized section in SKILL.md")


def fetch_docs() -> Tuple[int, int, Set[str]]:
    """Fetch all documentation. Returns (successful, failed, fetched_files)."""
    logger.info("Starting Claude Agent SDK documentation fetch")

    refs_dir = get_references_dir()
    refs_dir.mkdir(exist_ok=True)

    manifest = load_manifest()

    successful = 0
    failed = 0
    failed_pages = []
    fetched_files = set()
    new_manifest = {"files": {}}

    with requests.Session() as session:
        documentation_urls = discover_doc_urls(session)

        for idx, doc_url in enumerate(documentation_urls, 1):
            logger.info(f"Processing {idx}/{len(documentation_urls)}: {doc_url}")

            try:
                filename, content, original_url = fetch_markdown_url(doc_url, session)
                if filename in CUSTOM_FILES:
                    logger.info(f"Skipping custom doc (preserved): {filename}")
                    continue
                content_hash = save_markdown_file(filename, content)

                fetched_files.add(filename)
                new_manifest["files"][filename] = {
                    "original_url": original_url,
                    "hash": content_hash,
                    "last_updated": datetime.now().isoformat()
                }
                successful += 1

            except Exception as e:
                logger.error(f"Failed to process {doc_url}: {e}")
                failed += 1
                failed_pages.append(doc_url)

    cleanup_old_files(fetched_files, manifest)

    new_manifest["fetch_metadata"] = {
        "successful": successful,
        "failed": failed,
        "failed_pages": failed_pages,
    }

    save_manifest(new_manifest)

    return successful, failed, fetched_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Claude Agent SDK documentation")
    parser.add_argument('--validate', action='store_true', help='Only validate SKILL.md references')
    parser.add_argument('--update-skill', action='store_true', help='Update SKILL.md with uncategorized references')
    args = parser.parse_args()

    if args.validate:
        fetched_files = set(p.name for p in get_references_dir().glob('*.md'))
        fetched_files.add(MANIFEST_FILE)
        validation = validate_skill_md(fetched_files)

        if validation["orphaned"]:
            logger.warning("\nOrphaned references in SKILL.md (files don't exist):")
            for filename in validation["orphaned"]:
                logger.warning(f"  - {filename}")

        if validation["unreferenced"]:
            logger.info("\nUnreferenced files (not in SKILL.md):")
            for filename in validation["unreferenced"]:
                logger.info(f"  - {filename}")

        if not validation["orphaned"] and not validation["unreferenced"]:
            logger.info("\nSKILL.md is in sync with fetched files!")
        if validation["custom"]:
            logger.info("\nCustom/local docs preserved (not fetched):")
            for filename in validation["custom"]:
                logger.info(f"  - {filename}")

        return 0

    successful, failed, fetched_files = fetch_docs()

    logger.info(f"\nFetch completed: {successful} successful, {failed} failed")

    validation = validate_skill_md(fetched_files)
    if validation["orphaned"]:
        logger.warning("\nOrphaned references in SKILL.md (files don't exist):")
        for filename in validation["orphaned"]:
            logger.warning(f"  - {filename}")

    if validation["unreferenced"]:
        logger.info("\nUnreferenced files (not in SKILL.md):")
        for filename in validation["unreferenced"]:
            logger.info(f"  - {filename}")
        if args.update_skill:
            update_skill_md_uncategorized(validation["unreferenced"])
    if validation["custom"]:
        logger.info("\nCustom/local docs preserved (not fetched):")
        for filename in validation["custom"]:
            logger.info(f"  - {filename}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
