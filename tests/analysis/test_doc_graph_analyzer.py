import unittest
from pathlib import Path
import shutil
from collections import defaultdict

from markitecture.analysis.doc_graph_analyzer import DocumentationGraphAnalyzer


class TestDocumentationGraphAnalyzer(unittest.TestCase):
    def setUp(self):
        self.base_test_dir = Path.cwd() / "temp_test_doc_analyzer_docs"
        self.root_docs_path = self.base_test_dir / "project_root"
        self.root_docs_path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.base_test_dir.exists():
            shutil.rmtree(self.base_test_dir)

    def _create_file(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _get_abs_path(self, relative_path_str: str) -> Path:
        return (self.root_docs_path / relative_path_str).resolve()

    def test_initialization(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        self.assertEqual(analyzer.root_path, self.root_docs_path.resolve())
        self.assertIsInstance(analyzer.graph, defaultdict)
        self.assertIsInstance(analyzer.incoming_links, defaultdict)
        self.assertIsInstance(analyzer.documents_metadata, dict)

    def test_normalize_path_internal_existing(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        self._create_file(self.root_docs_path / "doc.md", "content")

        norm_path = analyzer._normalize_path("doc.md", self.root_docs_path)
        self.assertEqual(norm_path, self._get_abs_path("doc.md"))

        subdir = self.root_docs_path / "sub"
        self._create_file(subdir / "subdoc.md", "content")
        norm_path_sub = analyzer._normalize_path("../doc.md", subdir)
        self.assertEqual(norm_path_sub, self._get_abs_path("doc.md"))

    def test_normalize_path_variations(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        self._create_file(self.root_docs_path / "file.md", "Test")
        self._create_file(self.root_docs_path / "file.mdx", "Test")

        self.assertEqual(
            analyzer._normalize_path("file.md", self.root_docs_path),
            self._get_abs_path("file.md"),
        )
        self.assertEqual(
            analyzer._normalize_path("file.mdx", self.root_docs_path),
            self._get_abs_path("file.mdx"),
        )
        self._create_file(self.root_docs_path / "file.txt", "Test")
        self.assertIsNone(analyzer._normalize_path("file.txt", self.root_docs_path))
        self.assertIsNone(
            analyzer._normalize_path("nonexistent.md", self.root_docs_path)
        )
        self.assertIsNone(
            analyzer._normalize_path("http://example.com/doc.md", self.root_docs_path)
        )
        self.assertIsNone(
            analyzer._normalize_path("https://example.com", self.root_docs_path)
        )
        self.assertIsNone(analyzer._normalize_path("#section", self.root_docs_path))
        self.assertIsNone(
            analyzer._normalize_path("mailto:test@example.com", self.root_docs_path)
        )
        self.assertIsNone(
            analyzer._normalize_path(
                str(self.base_test_dir / "outside_root.md"), self.root_docs_path
            )
        )

    def test_extract_document_details_simple(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        doc_path = self.root_docs_path / "doc1.md"
        self._create_file(
            doc_path,
            "# Title One\nLink to [doc2](doc2.md). And [external](http://example.com).",
        )

        analyzer._extract_document_details(doc_path)
        meta = analyzer.documents_metadata[doc_path]

        self.assertEqual(meta["title"], "Title One")
        self.assertIn("doc2.md", meta["raw_links"])
        self.assertIn("http://example.com", meta["raw_links"])
        self.assertEqual(len(meta["raw_links"]), 2)
        self.assertEqual(meta["concepts"], [])

    def test_extract_document_details_setext_title(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        doc_path = self.root_docs_path / "setext.md"
        self._create_file(doc_path, "Setext Title\n===\nContent here.")
        analyzer._extract_document_details(doc_path)
        self.assertEqual(analyzer.documents_metadata[doc_path]["title"], "Setext Title")

    def test_extract_document_details_no_title(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        doc_path = self.root_docs_path / "no_title.md"
        self._create_file(doc_path, "Just content.")
        analyzer._extract_document_details(doc_path)
        self.assertEqual(
            analyzer.documents_metadata[doc_path]["title"], "no_title.md"
        )

    def test_build_graph_simple_list(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        doc1_path_str = str(self.root_docs_path / "doc1.md")
        doc2_path_str = str(self.root_docs_path / "doc2.md")
        doc1_path = Path(doc1_path_str)
        doc2_path = Path(doc2_path_str)

        self._create_file(doc1_path, "# Doc 1\nLinks to [doc2](doc2.md).")
        self._create_file(doc2_path, "# Doc 2\nLinks to [doc1](doc1.md).")

        analyzer.build_graph([doc1_path_str, doc2_path_str])

        self.assertIn(doc1_path, analyzer.graph)
        self.assertIn(doc2_path, analyzer.graph[doc1_path])
        self.assertIn(doc1_path, analyzer.graph[doc2_path])

        self.assertIn(doc2_path, analyzer.incoming_links)
        self.assertIn(doc1_path, analyzer.incoming_links[doc2_path])
        self.assertIn(doc2_path, analyzer.incoming_links[doc1_path])

        self.assertEqual(analyzer.documents_metadata[doc1_path]["title"], "Doc 1")

    def test_build_graph_scan_directory(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        doc1_path = self.root_docs_path / "doc1.md"
        subdir_path = self.root_docs_path / "subdir"
        doc2_path = subdir_path / "doc2.mdx"

        self._create_file(doc1_path, "# Doc 1\nLinks to [doc2](./subdir/doc2.mdx).")
        self._create_file(doc2_path, "# Doc 2\nLinks to [doc1](../doc1.md).")
        self._create_file(self.root_docs_path / "other.txt", "ignore this")

        analyzer.build_graph()

        self.assertIn(doc1_path, analyzer.graph)
        self.assertIn(doc2_path, analyzer.graph[doc1_path])
        self.assertIn(doc1_path, analyzer.graph[doc2_path])
        self.assertNotIn(self.root_docs_path / "other.txt", analyzer.graph)
        self.assertEqual(len(analyzer.graph), 2)

    def test_build_graph_link_to_non_processed_file(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        doc1_path = self._get_abs_path("doc1.md")
        self._create_file(doc1_path, "Link to [non-processed](doc2.md)")
        self._create_file(self._get_abs_path("doc2.md"), "I exist but am not processed.")

        analyzer.build_graph([str(doc1_path)])
        self.assertIn(doc1_path, analyzer.graph)
        self.assertEqual(len(analyzer.graph[doc1_path]), 0)

    def test_build_graph_empty_and_errors(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))

        analyzer.build_graph([])
        self.assertEqual(len(analyzer.graph), 0)
        self.assertEqual(len(analyzer.documents_metadata), 0)

        analyzer.build_graph([str(self.root_docs_path / "ghost.md")])
        self.assertEqual(len(analyzer.graph), 0)

        empty_subdir = self.root_docs_path / "empty_dir"
        empty_subdir.mkdir()
        analyzer_empty_scan = DocumentationGraphAnalyzer(root_path=str(empty_subdir))
        analyzer_empty_scan.build_graph()
        self.assertEqual(len(analyzer_empty_scan.graph), 0)

    def test_analyze_knowledge_flow_full_analysis(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        d1 = self._get_abs_path("d1.md")
        d2 = self._get_abs_path("d2.md")
        d3 = self._get_abs_path("sub/d3.md")
        d4 = self._get_abs_path("sub/d4.md")
        d5 = self._get_abs_path("d5.md")

        self._create_file(d1, "# D1\n[d2](d2.md)\n[d5](d5.md)")
        self._create_file(d2, "# D2\n[d1](d1.md)")
        self._create_file(d3, "# D3\nContent for D3.")
        self._create_file(d4, "# D4\nContent for D4, also in sub.")
        self._create_file(d5, "# D5\n[d1](d1.md)\n[d2](d2.md)")

        analyzer.build_graph()
        results = analyzer.analyze_knowledge_flow()

        self.assertEqual(results["total_documents_processed"], 5)

        self.assertIn(str(d3), results["orphaned_documents"])
        self.assertIn(str(d4), results["orphaned_documents"])
        self.assertEqual(len(results["orphaned_documents"]), 2)

        hub_docs_paths = {h["doc"] for h in results["hub_documents"]}
        self.assertIn(str(d1), hub_docs_paths)
        self.assertIn(str(d5), hub_docs_paths)

        auth_docs_paths = {a["doc"] for a in results["authority_documents"]}
        self.assertIn(str(d1), auth_docs_paths)
        self.assertIn(str(d2), auth_docs_paths)

        self.assertEqual(
            results["document_link_stats"][str(d1)]["outgoing_links_count"], 2
        )
        self.assertEqual(
            results["document_link_stats"][str(d1)]["incoming_links_count"], 2
        )

        found_d3_d4_suggestion = False
        for sugg in results["missing_bridge_suggestions"]:
            if sugg["type"] == "common_directory":
                pair = {sugg["doc1_path"], sugg["doc2_path"]}
                if {str(d3), str(d4)} == pair:
                    found_d3_d4_suggestion = True
                    break
        self.assertTrue(
            found_d3_d4_suggestion,
            "Expected common_directory suggestion for d3 and d4",
        )

        for sugg in results["missing_bridge_suggestions"]:
            pair = {sugg["doc1_path"], sugg["doc2_path"]}
            self.assertNotEqual(
                pair, {str(d1), str(d2)}, "d1 and d2 are linked, should not be suggested."
            )

    def test_analyze_knowledge_flow_empty_graph(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        for item in self.root_docs_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        analyzer.build_graph()
        results = analyzer.analyze_knowledge_flow()

        self.assertEqual(results["total_documents_processed"], 0)
        self.assertEqual(len(results["orphaned_documents"]), 0)
        self.assertEqual(len(results["hub_documents"]), 0)
        self.assertEqual(len(results["authority_documents"]), 0)
        self.assertEqual(len(results["missing_bridge_suggestions"]), 0)

    def test_get_graph_data(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        d1_path = self._get_abs_path("doc1.md")
        d2_path = self._get_abs_path("doc2.md")
        self._create_file(d1_path, "# Doc 1\n[link](doc2.md)")
        self._create_file(d2_path, "# Doc 2")

        analyzer.build_graph([str(d1_path), str(d2_path)])
        graph_data = analyzer.get_graph_data()

        self.assertEqual(len(graph_data["nodes"]), 2)
        node_ids = {n["id"] for n in graph_data["nodes"]}
        self.assertIn(str(d1_path), node_ids)
        self.assertIn(str(d2_path), node_ids)

        self.assertEqual(len(graph_data["edges"]), 1)
        edge = graph_data["edges"][0]
        self.assertEqual(edge["source"], str(d1_path))
        self.assertEqual(edge["target"], str(d2_path))

    def test_bridge_content_shared_outgoing_and_incoming(self):
        analyzer = DocumentationGraphAnalyzer(root_path=str(self.root_docs_path))
        idx_path = self._get_abs_path("index.md")
        feat_a_path = self._get_abs_path("feat_a.md")
        feat_b_path = self._get_abs_path("feat_b.md")
        common_target_path = self._get_abs_path("common_target.md")
        common_source_path = self._get_abs_path("common_source.md")

        self._create_file(
            idx_path, "# Index\nLinks to [Feat A](feat_a.md) and [Feat B](feat_b.md)."
        )
        self._create_file(
            feat_a_path, "# Feat A\nLinks to [Common Target](common_target.md)."
        )
        self._create_file(
            feat_b_path, "# Feat B\nLinks to [Common Target](common_target.md)."
        )
        self._create_file(common_target_path, "# Common Target")
        self._create_file(
            common_source_path,
            "# Common Source\nLinks to [Feat A](feat_a.md) and [Feat B](feat_b.md).",
        )

        analyzer.build_graph()
        results = analyzer.analyze_knowledge_flow()
        suggestions = results["missing_bridge_suggestions"]

        sugg_shared_outgoing = None
        for s in suggestions:
            pair = {s["doc1_path"], s["doc2_path"]}
            if pair == {
                str(feat_a_path),
                str(feat_b_path),
            } and s["type"] == "shared_outgoing_link":
                sugg_shared_outgoing = s
                break
        self.assertIsNotNone(
            sugg_shared_outgoing,
            "Expected 'shared_outgoing_link' suggestion for feat_a and feat_b.",
        )
        if sugg_shared_outgoing:
            self.assertIn(
                str(common_target_path), sugg_shared_outgoing["shared_targets"]
            )

        self._create_file(feat_b_path, "# Feat B\nNo link to common_target now.")
        analyzer.build_graph()
        results_rebuilt = analyzer.analyze_knowledge_flow()
        suggestions_rebuilt = results_rebuilt["missing_bridge_suggestions"]

        sugg_shared_incoming = None
        for s in suggestions_rebuilt:
            pair = {s["doc1_path"], s["doc2_path"]}
            if pair == {
                str(feat_a_path),
                str(feat_b_path),
            } and s["type"] == "shared_incoming_link":
                sugg_shared_incoming = s
                break
        self.assertIsNotNone(
            sugg_shared_incoming,
            "Expected 'shared_incoming_link' for feat_a, feat_b after removing shared_outgoing.",
        )
        if sugg_shared_incoming:
            self.assertTrue(
                str(idx_path) in sugg_shared_incoming["shared_sources"]
                or str(common_source_path) in sugg_shared_incoming["shared_sources"]
            )


if __name__ == "__main__":
    unittest.main()
