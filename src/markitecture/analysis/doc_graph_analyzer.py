import os
from pathlib import Path
import re
from collections import defaultdict

# Attempt to import LinkValidator.
from markitecture.processing.link_validator import CrossLinksValidator
from markitecture.settings.validators import ValidatorSettings

class DocumentationGraphAnalyzer:
    """
    Analyzes the relationships between documentation files to build a knowledge graph.
    Focuses on identifying how documents are connected and uncovering insights
    about the documentation structure.
    """

    def __init__(self, root_path: str, link_validator_timeout: int = 10):
        """
        Initializes the DocumentationGraphAnalyzer.

        Args:
            root_path (str): The root directory of the documentation to analyze.
            link_validator_timeout (int): Timeout for the link validator's checks.
        """
        self.root_path = Path(root_path).resolve()
        self.graph = defaultdict(set)  # doc_path -> set of linked doc_paths
        self.incoming_links = defaultdict(set)  # doc_path -> set of docs linking to it
        self.documents_metadata = {}  # file_path: {"title": "...", "concepts": [], "raw_links": []}
        self.link_validator_timeout = link_validator_timeout

    def _normalize_path(self, path_str: str, base_doc_dir: Path) -> Path | None:
        """
        Normalizes a given path string relative to the document's directory or root_path.
        Returns an absolute Path object if the file is a Markdown file within the root_path,
        otherwise None.
        """
        # Ignore if it's an absolute path outside our root, an external link, or an anchor
        if path_str.startswith(("http://", "https://", "#", "mailto:")):
            return None

        path_obj = Path(path_str)

        if path_obj.is_absolute():
            # If it's already absolute, check if it's within our root
            abs_path = path_obj.resolve()
        else:
            # Resolve relative to the directory of the current document
            abs_path = (base_doc_dir / path_str).resolve()

        # Ensure the path is within the documentation root directory
        try:
            abs_path.relative_to(self.root_path)
        except ValueError:
            # Not within the root_path, so ignore
            return None

        # We are only interested in markdown files that exist
        if abs_path.exists() and abs_path.is_file() and abs_path.suffix.lower() in ['.md', '.mdx']:
            return abs_path
        return None

    def _extract_document_details(self, doc_path: Path) -> None:
        """
        Extracts title, concepts (placeholder), and raw hyperlinks from a document.
        """
        if doc_path in self.documents_metadata: # Already processed
            return

        try:
            content = doc_path.read_text(encoding="utf-8")
        except Exception as e:
            # print(f"Warning: Could not read {doc_path}: {e}")
            self.documents_metadata[doc_path] = {
                "title": doc_path.name, "concepts": [], "raw_links": [], "error": str(e)
            }
            return

        title = doc_path.name
        lines = content.splitlines()
        if lines:
            first_line = lines[0].strip()
            if first_line.startswith("# "):
                title = first_line[2:].strip()
            elif len(lines) > 1 and lines[1].startswith("===") and first_line: # Setext H1
                title = first_line

        link_extractor = CrossLinksValidator(
            settings=ValidatorSettings(timeout=self.link_validator_timeout)
        )
        raw_links_tuples = link_extractor.extract_links(content)
        raw_links = [link_info[1] for link_info in raw_links_tuples]  # Just the URLs

        self.documents_metadata[doc_path] = {
            "title": title,
            "concepts": [],  # Placeholder for actual concept extraction
            "raw_links": raw_links,
        }

    def build_graph(self, doc_file_paths: list[str] | None = None):
        """
        Builds the knowledge graph from a list of document file paths.
        If doc_file_paths is None, it scans the root_path for all .md and .mdx files.
        The graph currently represents hyperlink connections.

        Args:
            doc_file_paths (list[str] | None, optional): A list of absolute or relative paths
                                                         to markdown files. Defaults to None.
        """
        self.graph.clear()
        self.incoming_links.clear()
        self.documents_metadata.clear()

        actual_doc_paths: list[Path] = []
        if doc_file_paths is None:
            # Scan root_path for markdown files
            md_files = list(self.root_path.rglob("*.md"))
            mdx_files = list(self.root_path.rglob("*.mdx"))
            actual_doc_paths = [p.resolve() for p in md_files + mdx_files]
        else:
            for file_str in doc_file_paths:
                path = Path(file_str)
                if not path.is_absolute():
                    path = (self.root_path / path).resolve()

                if path.exists() and path.is_file() and path.suffix.lower() in ['.md', '.mdx']:
                    actual_doc_paths.append(path)
                # else:
                #     print(f"Warning: Document file not found, not a file, or wrong type: {path}")

        if not actual_doc_paths:
            # print("Warning: No document files found to build the graph.")
            return

        # First pass: Initialize all nodes and extract details
        for doc_path in actual_doc_paths:
            self.graph[doc_path] = set()
            self.incoming_links[doc_path] = set()
            self._extract_document_details(doc_path)

        # Second pass: Populate edges
        for doc_path in actual_doc_paths:
            if "error" in self.documents_metadata[doc_path]:
                continue

            doc_dir = doc_path.parent
            for linked_url_str in self.documents_metadata[doc_path]["raw_links"]:
                normalized_target_path = self._normalize_path(linked_url_str, doc_dir)

                # Ensure the target is one of the documents we are processing
                if normalized_target_path and normalized_target_path in actual_doc_paths:
                    self.graph[doc_path].add(normalized_target_path)
                    self.incoming_links[normalized_target_path].add(doc_path)

    def analyze_knowledge_flow(self) -> dict:
        """
        Analyzes the graph to find insights.
        Currently focuses on hyperlink-based analysis:
        - Orphaned documents (no incoming internal links from the analyzed set)
        - Hub documents (many outgoing internal links within the analyzed set)
        - Authority documents (many incoming internal links from the analyzed set)
        - Basic link counts per document
        - Suggestions for missing bridge content

        Returns:
            dict: A dictionary containing analysis results.
        """
        if not self.graph and not self.documents_metadata:
            self.build_graph()

        orphaned_documents = []
        document_link_stats = {}

        all_docs_considered = set(self.documents_metadata.keys())

        for doc_path in all_docs_considered:
            doc_meta = self.documents_metadata.get(doc_path, {})
            title = doc_meta.get("title", doc_path.name)

            if "error" in doc_meta:
                document_link_stats[str(doc_path)] = {
                    "title": title, "error": doc_meta["error"],
                    "outgoing_links_count": 0, "incoming_links_count": 0,
                    "outgoing_links_to": [],
                }
                continue

            if not self.incoming_links.get(doc_path): # Relies on incoming_links being initialized for all docs
                orphaned_documents.append(str(doc_path))

            document_link_stats[str(doc_path)] = {
                "title": title,
                "outgoing_links_count": len(self.graph.get(doc_path, set())),
                "incoming_links_count": len(self.incoming_links.get(doc_path, set())),
                "outgoing_links_to": [str(p) for p in self.graph.get(doc_path, set())],
            }

        valid_doc_stats = {k: v for k, v in document_link_stats.items() if "error" not in v}

        sorted_by_outgoing = sorted(valid_doc_stats.items(), key=lambda item: item[1]["outgoing_links_count"], reverse=True)
        sorted_by_incoming = sorted(valid_doc_stats.items(), key=lambda item: item[1]["incoming_links_count"], reverse=True)

        hub_documents = [{"doc": item[0], "title": item[1]["title"], "count": item[1]["outgoing_links_count"]}
                         for item in sorted_by_outgoing if item[1]["outgoing_links_count"] > 0]
        authority_documents = [{"doc": item[0], "title": item[1]["title"], "count": item[1]["incoming_links_count"]}
                               for item in sorted_by_incoming if item[1]["incoming_links_count"] > 0]

        missing_bridge_suggestions = self._suggest_missing_bridge_content(all_docs_considered)

        return {
            "orphaned_documents": orphaned_documents,
            "hub_documents": hub_documents,
            "authority_documents": authority_documents,
            "missing_bridge_suggestions": missing_bridge_suggestions,
            "document_link_stats": document_link_stats,
            "total_documents_processed": len(all_docs_considered),
            "documents_with_errors": sum(1 for doc_meta in self.documents_metadata.values() if "error" in doc_meta),
        }

    def _suggest_missing_bridge_content(self, doc_paths: set[Path]) -> list[dict]:
        """
        Suggests missing bridge content based on directory structure and link patterns.
        Aims to find pairs of documents that are likely related but not directly linked.
        """
        suggestions = []
        # To avoid duplicate suggestions like (A,B) and (B,A) or suggesting multiple times for the same pair
        # Store as frozenset of string paths for hashability in the set
        suggested_pairs = set()

        valid_doc_paths = [p for p in doc_paths if "error" not in self.documents_metadata.get(p, {})]

        for i in range(len(valid_doc_paths)):
            doc_a_path = valid_doc_paths[i]
            doc_a_meta = self.documents_metadata[doc_a_path]

            for j in range(i + 1, len(valid_doc_paths)):
                doc_b_path = valid_doc_paths[j]
                doc_b_meta = self.documents_metadata[doc_b_path]

                pair_identifier = frozenset({str(doc_a_path), str(doc_b_path)})
                if pair_identifier in suggested_pairs:
                    continue

                # 1. Check for direct links (A->B or B->A)
                are_directly_linked = (doc_b_path in self.graph.get(doc_a_path, set()) or \
                                       doc_a_path in self.graph.get(doc_b_path, set()))
                if are_directly_linked:
                    continue

                # Heuristic 1: Common parent or grandparent directory (structural proximity)
                parent_a = doc_a_path.parent
                parent_b = doc_b_path.parent

                # Check for common parent (documents in the same directory)
                # Avoid suggesting for files directly under root_path unless specifically desired
                if parent_a == parent_b and parent_a != self.root_path:
                    reason = f"Documents are in the same directory '{parent_a.relative_to(self.root_path)}' but not directly linked."
                    suggestions.append({
                        "type": "common_directory",
                        "doc1_path": str(doc_a_path), "doc1_title": doc_a_meta.get("title", doc_a_path.name),
                        "doc2_path": str(doc_b_path), "doc2_title": doc_b_meta.get("title", doc_b_path.name),
                        "reason": reason
                    })
                    suggested_pairs.add(pair_identifier)
                    continue # This is a strong signal, so prioritize this suggestion for the pair

                # Check for common grandparent (i.e., parent directories are siblings)
                # Avoid if one of the parents is the root path itself.
                if parent_a.parent == parent_b.parent and parent_a != self.root_path and parent_b != self.root_path and parent_a.parent != self.root_path:
                    reason = (f"Documents are in sibling directories ('{parent_a.name}' and '{parent_b.name}') "
                              f"under '{parent_a.parent.relative_to(self.root_path)}' but not directly linked.")
                    suggestions.append({
                        "type": "sibling_directories",
                        "doc1_path": str(doc_a_path), "doc1_title": doc_a_meta.get("title", doc_a_path.name),
                        "doc2_path": str(doc_b_path), "doc2_title": doc_b_meta.get("title", doc_b_path.name),
                        "reason": reason
                    })
                    suggested_pairs.add(pair_identifier)
                    continue

                # Heuristic 2: Both link to the same document(s) (co-citation of an outbound link)
                # More valuable if they share more than one common target.
                common_outgoing_links = self.graph.get(doc_a_path, set()).intersection(self.graph.get(doc_b_path, set()))
                if len(common_outgoing_links) >= 1: # Threshold can be adjusted (e.g. >= 2 for higher confidence)
                    common_targets_titles = [self.documents_metadata.get(p, {}).get("title", p.name) for p in common_outgoing_links]
                    # Limit display for brevity
                    display_targets = common_targets_titles[:3]
                    if len(common_targets_titles) > 3:
                        display_targets.append("...")
                    reason = f"Both documents link to common target(s): {', '.join(display_targets)}."
                    suggestions.append({
                        "type": "shared_outgoing_link",
                        "doc1_path": str(doc_a_path), "doc1_title": doc_a_meta.get("title", doc_a_path.name),
                        "doc2_path": str(doc_b_path), "doc2_title": doc_b_meta.get("title", doc_b_path.name),
                        "shared_targets": [str(p) for p in common_outgoing_links],
                        "reason": reason
                    })
                    suggested_pairs.add(pair_identifier)
                    continue

                # Heuristic 3: Both are linked by the same document(s) (co-citation of an inbound link)
                common_incoming_links = self.incoming_links.get(doc_a_path, set()).intersection(self.incoming_links.get(doc_b_path, set()))
                if len(common_incoming_links) >= 1: # Threshold can be adjusted
                    common_sources_titles = [self.documents_metadata.get(p, {}).get("title", p.name) for p in common_incoming_links]
                    display_sources = common_sources_titles[:3]
                    if len(common_sources_titles) > 3:
                        display_sources.append("...")
                    reason = f"Both documents are linked from common source(s): {', '.join(display_sources)}."
                    suggestions.append({
                        "type": "shared_incoming_link",
                        "doc1_path": str(doc_a_path), "doc1_title": doc_a_meta.get("title", doc_a_path.name),
                        "doc2_path": str(doc_b_path), "doc2_title": doc_b_meta.get("title", doc_b_path.name),
                        "shared_sources": [str(p) for p in common_incoming_links],
                        "reason": reason
                    })
                    suggested_pairs.add(pair_identifier)
                    continue

        return suggestions

    def get_graph_data(self) -> dict:
        """
        Returns a serializable representation of the graph (nodes and edges).
        """
        nodes = []
        for path, meta in self.documents_metadata.items():
            if "error" not in meta:
                 nodes.append({"id": str(path), "title": meta.get("title", path.name)})

        return {
            "nodes": nodes,
            "edges": [
                {"source": str(source_doc), "target": str(target_doc)}
                for source_doc, linked_docs in self.graph.items()
                for target_doc in linked_docs
                if source_doc in self.documents_metadata and "error" not in self.documents_metadata[source_doc] and \
                   target_doc in self.documents_metadata and "error" not in self.documents_metadata[target_doc]
            ],
        }

if __name__ == '__main__':
    print("Running basic DocumentationGraphAnalyzer example...")
    # Create a dummy doc structure in a temporary directory
    # Using Path.cwd() to ensure it's created where the script is, or use a fixed temp path
    base_test_dir = Path.cwd() / "markitecture_test_docs"
    example_docs_path = base_test_dir / "project_root"
    example_docs_path.mkdir(parents=True, exist_ok=True)

    # Create some content
    (example_docs_path / "index.md").write_text(
        "# Welcome\nMain page linking to [Feature A](features/feature_a.md) and [About Us](about/info.md).\n"
        "Also, a link to [Installation Guide](guides/installation.md)."
    )

    features_path = example_docs_path / "features"
    features_path.mkdir(exist_ok=True)
    (features_path / "feature_a.md").write_text(
        "## Feature A\nDetails about A. Links to [Main Page](../index.md) and [Feature B](./feature_b.md).\n"
        "Consider reading the [Installation Guide](../guides/installation.md)."
    )
    (features_path / "feature_b.md").write_text(
        "### Feature B\nInfo on B. Also see [Advanced B Details](advanced/feature_b_details.mdx).\n"
        "Related to [Feature A](./feature_a.md)."
    ) # feature_a and feature_b are now directly linked.

    advanced_path = features_path / "advanced"
    advanced_path.mkdir(exist_ok=True)
    (advanced_path / "feature_b_details.mdx").write_text("# Advanced B\nVery advanced stuff. No outgoing internal links.")

    about_path = example_docs_path / "about"
    about_path.mkdir(exist_ok=True)
    (about_path / "info.md").write_text(
        "# About Us\nThis page is about us. Check the [Main Page](../index.md) or an [External Site](http://example.com).\n"
        "Learn about our [Team Structure](team/structure.md)." # New link
    )
    (about_path / "history.md").write_text("# Our History\nCompany history. See also [About Us](./info.md).") # In same dir as info.md

    team_path = example_docs_path / "team" # Sibling to 'about', under 'root'
    team_path.mkdir(exist_ok=True)
    (team_path / "structure.md").write_text("# Team Structure\nHow our team is organized.") # Linked by about/info.md
    (team_path / "values.md").write_text("# Team Values\nOur core values.") # In same dir as structure.md, but not linked.

    guides_path = example_docs_path / "guides"
    guides_path.mkdir(exist_ok=True)
    (guides_path / "installation.md").write_text("# Installation Guide\nHow to install.") # Linked by index & feature_a
    (guides_path / "usage.md").write_text("# Usage Guide\nHow to use the product.") # Not linked by installation.md

    # An orphaned file (no incoming links from others in this set)
    (example_docs_path / "legal.md").write_text("# Legal Stuff\nImportant legal information.")

    # A file linking to Feature A, creating a shared incoming link situation for Feature A and Index (via Feature A)
    (example_docs_path / "contributing.md").write_text("# Contributing\nHow to contribute. Link to [Feature A](features/feature_a.md).")

    print(f"Analyzing documentation in: {example_docs_path.relative_to(Path.cwd())}")
    analyzer = DocumentationGraphAnalyzer(root_path=str(example_docs_path))

    # Build graph with all files found in root_path
    analyzer.build_graph()

    analysis_results = analyzer.analyze_knowledge_flow()

    print("\n--- Analysis Results ---")
    print(f"  Total documents processed: {analysis_results['total_documents_processed']}")
    print(f"  Documents with errors: {analysis_results['documents_with_errors']}")

    print("\n  Orphaned documents (no incoming links from within the set):")
    for doc_path_str in analysis_results['orphaned_documents']:
        doc_path = Path(doc_path_str)
        print(f"    - {analyzer.documents_metadata.get(doc_path, {}).get('title', doc_path.name)} ({doc_path.relative_to(example_docs_path)})")

    print("\n  Hub documents (most outgoing links):")
    for hub_info in analysis_results['hub_documents'][:5]: # Top 5
        doc_path = Path(hub_info['doc'])
        print(f"    - {hub_info['title']} ({doc_path.relative_to(example_docs_path)}) - Count: {hub_info['count']}")

    print("\n  Authority documents (most incoming links):")
    for auth_info in analysis_results['authority_documents'][:5]: # Top 5
        doc_path = Path(auth_info['doc'])
        print(f"    - {auth_info['title']} ({doc_path.relative_to(example_docs_path)}) - Count: {auth_info['count']}")

    print("\n  Missing Bridge Content Suggestions:")
    if analysis_results['missing_bridge_suggestions']:
        for i, suggestion in enumerate(analysis_results['missing_bridge_suggestions']):
            doc1_path = Path(suggestion['doc1_path'])
            doc2_path = Path(suggestion['doc2_path'])
            print(f"    Suggestion {i+1} (Type: {suggestion['type']}):")
            print(f"      Doc 1: '{suggestion['doc1_title']}' ({doc1_path.relative_to(example_docs_path)})")
            print(f"      Doc 2: '{suggestion['doc2_title']}' ({doc2_path.relative_to(example_docs_path)})")
            print(f"      Reason: {suggestion['reason']}")
    else:
        print("    No specific bridge content suggestions found.")

    print("\n  Document Link Stats:")
    for doc_str, stats in analysis_results['document_link_stats'].items():
        doc_path = Path(doc_str)
        if "error" in stats:
            print(f"  - {stats['title']} ({doc_path.relative_to(example_docs_path)}): Error - {stats['error']}")
        else:
            print(f"  - {stats['title']} ({doc_path.relative_to(example_docs_path)}): Out({stats['outgoing_links_count']}) In({stats['incoming_links_count']})")
            # To see specific links:
            # if stats['outgoing_links_to']:
            #     print(f"      Links to: {[Path(p).name for p in stats['outgoing_links_to']]}")

    # print("\nGraph Data (for visualization):")
    # graph_viz_data = analyzer.get_graph_data()
    # print(f"Nodes: {len(graph_viz_data['nodes'])}, Edges: {len(graph_viz_data['edges'])}")

    # It's good practice to offer cleanup, but for testing, manual inspection is often better.
    print(f"\nNote: Example directory '{example_docs_path}' and its parent '{base_test_dir}' were created.")
    print(f"To remove them, run: import shutil; shutil.rmtree('{base_test_dir}')")

    # Test case: what if root_path does not exist?
    analyzer_bad_root = DocumentationGraphAnalyzer(root_path="./non_existent_docs_root")
    analyzer_bad_root.build_graph() # Should handle gracefully
    results_bad_root = analyzer_bad_root.analyze_knowledge_flow()
    print("\n--- Analysis with non-existent root ---")
    print(f"  Total documents processed: {results_bad_root['total_documents_processed']}") # Expected 0
    assert results_bad_root['total_documents_processed'] == 0

    # Test case: root_path exists but is empty
    empty_dir = base_test_dir / "empty_project_root"
    empty_dir.mkdir(exist_ok=True)
    analyzer_empty_root = DocumentationGraphAnalyzer(root_path=str(empty_dir))
    analyzer_empty_root.build_graph()
    results_empty_root = analyzer_empty_root.analyze_knowledge_flow()
    print("\n--- Analysis with empty root directory ---")
    print(f"  Total documents processed: {results_empty_root['total_documents_processed']}") # Expected 0
    assert results_empty_root['total_documents_processed'] == 0

    # Clean up the test directories after run
    # import shutil
    # shutil.rmtree(base_test_dir)
    # print(f"\nCleaned up test directory: {base_test_dir}")
