from typing import List
import typer
from pathlib import Path


def main(api_doc_file: Path, cli_doc_file: Path, readme_file: Path):
    open_line = "<!-- AUTO_DOCZ_START -->"
    close_line = "<!-- AUTO_DOCZ_END -->"
    found_open = False
    found_close = False
    before_lines: List[str] = []
    after_lines: List[str] = []
    line: str
    for line in readme_file.read_text().split("\n"):
        if not found_open:
            before_lines.append(line)
            if line.strip() == open_line:
                found_open = True
        elif not found_close:
            if line.strip() == close_line:
                found_close = True
                after_lines.append(line)
        else:
            after_lines.append(line)

    api_docs = api_doc_file.read_text().split("\n")
    cli_docs = cli_doc_file.read_text().split("\n")
    output = "\n".join(before_lines + api_docs + cli_docs + after_lines)
    readme_file.write_text(output)
    typer.echo("Updated API/CLI docs in readme!")


if __name__ == "__main__":
    typer.run(main)
