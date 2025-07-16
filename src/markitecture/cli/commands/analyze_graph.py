from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from markitecture.analysis.doc_graph_analyzer import DocumentationGraphAnalyzer
from markitecture.utils.printer import RichPrinter # Assuming printer is accessible

# Initialize printer globally or pass as dependency if preferred by project style
_printer = RichPrinter()

class AnalyzeGraphCommand(BaseModel):
    """
    Analyzes the structure and relationships within a documentation set.
    Provides insights into orphaned pages, content hubs, authorities,
    and suggests potential missing links between related documents.
    """
    input_dir: Path = Field(
        ...,  # Ellipsis means it's a required argument
        description="The root directory of the documentation to analyze.",
        json_schema_extra=dict(commands=[['-i', '--input']]), # Example, actual CLI flags need to be set up in MarkitectureApp
    )
    # Add other potential options later, e.g., output_file, verbosity

    def cli_cmd(self) -> None:
        """
        Executes the documentation graph analysis.
        """
        if not self.input_dir.exists() or not self.input_dir.is_dir():
            _printer.print_error(f"Input directory does not exist or is not a directory: {self.input_dir}")
            return

        _printer.print_info(f"Analyzing documentation graph for directory: {self.input_dir.resolve()}")

        try:
            analyzer = DocumentationGraphAnalyzer(root_path=str(self.input_dir))
            # build_graph will be called by analyze_knowledge_flow if graph is not built
            # analyzer.build_graph() # Or call explicitly if preferred
            results = analyzer.analyze_knowledge_flow()
        except Exception as e:
            _printer.print_error(f"An error occurred during graph analysis: {e}")
            # Consider re-raising if it's critical and not handled by the global exception handler in app.py
            return

        # --- Display Results ---
        _printer.print_title("Documentation Graph Analysis Results")

        # Summary
        summary_data = {
            "Total Documents Processed": str(results["total_documents_processed"]),
            "Documents with Read Errors": str(results["documents_with_errors"]),
            "Orphaned Documents Found": str(len(results["orphaned_documents"])),
            "Hub Documents Found": str(len(results["hub_documents"])),
            "Authority Documents Found": str(len(results["authority_documents"])),
            "Bridge Content Suggestions": str(len(results["missing_bridge_suggestions"])),
        }
        _printer.print_key_value_table("Analysis Summary", summary_data)

        # Orphaned Documents
        if results["orphaned_documents"]:
            orphaned_rows = []
            for doc_path_str in results["orphaned_documents"]:
                doc_path = Path(doc_path_str)
                title = results["document_link_stats"].get(doc_path_str, {}).get("title", doc_path.name)
                try:
                    relative_path = doc_path.relative_to(self.input_dir.resolve())
                except ValueError:
                    relative_path = doc_path # Should not happen if paths are correct
                orphaned_rows.append([title, str(relative_path)])
            _printer.print_table("Orphaned Documents (No Incoming Links)", ["Title", "Path"], orphaned_rows)
        else:
            _printer.print_info("No orphaned documents found.")

        # Hub Documents
        if results["hub_documents"]:
            hub_rows = []
            # Sort by count descending, take top N if list is too long
            for hub_info in sorted(results["hub_documents"], key=lambda x: x["count"], reverse=True)[:10]:
                doc_path = Path(hub_info["doc"])
                try:
                    relative_path = doc_path.relative_to(self.input_dir.resolve())
                except ValueError:
                    relative_path = doc_path
                hub_rows.append([hub_info["title"], str(relative_path), str(hub_info["count"])])
            _printer.print_table("Hub Documents (Most Outgoing Links - Top 10)", ["Title", "Path", "Outgoing Links"], hub_rows)
        else:
            _printer.print_info("No significant hub documents found.")

        # Authority Documents
        if results["authority_documents"]:
            auth_rows = []
            # Sort by count descending, take top N
            for auth_info in sorted(results["authority_documents"], key=lambda x: x["count"], reverse=True)[:10]:
                doc_path = Path(auth_info["doc"])
                try:
                    relative_path = doc_path.relative_to(self.input_dir.resolve())
                except ValueError:
                    relative_path = doc_path
                auth_rows.append([auth_info["title"], str(relative_path), str(auth_info["count"])])
            _printer.print_table("Authority Documents (Most Incoming Links - Top 10)", ["Title", "Path", "Incoming Links"], auth_rows)
        else:
            _printer.print_info("No significant authority documents found.")

        # Missing Bridge Suggestions
        if results["missing_bridge_suggestions"]:
            _printer.print_info("\n[header]Missing Bridge Content Suggestions:[/header]") # Custom header for this section
            for i, sugg in enumerate(results["missing_bridge_suggestions"]):
                doc1_path = Path(sugg["doc1_path"])
                doc2_path = Path(sugg["doc2_path"])
                try:
                    rel_doc1 = doc1_path.relative_to(self.input_dir.resolve())
                    rel_doc2 = doc2_path.relative_to(self.input_dir.resolve())
                except ValueError:
                    rel_doc1 = doc1_path
                    rel_doc2 = doc2_path

                _printer.console.print(f"\n[info]Suggestion {i+1} (Type: {sugg['type']}):[/info]")
                _printer.console.print(f"  [key]Document 1:[/key] '{sugg['doc1_title']}' ({rel_doc1})")
                _printer.console.print(f"  [key]Document 2:[/key] '{sugg['doc2_title']}' ({rel_doc2})")
                _printer.console.print(f"  [key]Reason:[/key] {sugg['reason']}")
            _printer.console.print() # Extra space after suggestions
        else:
            _printer.print_info("No specific bridge content suggestions found.")

        _printer.print_success("Documentation graph analysis complete.")

# Example of how it might be invoked if this file were runnable (for testing)
# if __name__ == "__main__":
#     # This is for standalone testing of the command structure,
#     # actual CLI invocation goes through app.py
#
#     # Create a dummy test environment
#     current_dir = Path.cwd()
#     dummy_root = current_dir / "temp_cli_test_docs"
#     dummy_root.mkdir(exist_ok=True)
#
#     (dummy_root / "index.md").write_text("# Index\nLinks to [page1](page1.md).")
#     (dummy_root / "page1.md").write_text("# Page 1\nLinks to [page2](sub/page2.md).")
#     sub_dir = dummy_root / "sub"
#     sub_dir.mkdir(exist_ok=True)
#     (sub_dir / "page2.md").write_text("# Page 2\nNo links.")
#     (sub_dir / "page3.md").write_text("# Page 3\nOrphan in sub.") # Orphan, but also common dir with page2
#
#     command_settings = {
#         "input_dir": str(dummy_root)
#     }
#     command = AnalyzeGraphCommand(**command_settings)
#     command.cli_cmd()
#
#     # Clean up
#     import shutil
#     shutil.rmtree(dummy_root)
