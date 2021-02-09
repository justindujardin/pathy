import re
from pathlib import Path
from typing import List

import typer


def extract_code_snippets(lines: List[str]) -> List[str]:
    inside_codeblock = False
    blocks = []
    current_block: List[str] = []
    while len(lines) > 0:
        line = lines.pop(0)
        if not inside_codeblock:
            inside_codeblock = re.match(r"```(p|P)ython$", line.strip())
        else:
            end_block = re.match(r"```", line.strip())
            if end_block:
                blocks.append("\n".join(current_block))
                current_block = []
                inside_codeblock = False
            else:
                current_block.append(line)

    return blocks


def exec_snippet(text: str):
    try:
        exec(text)
    except BaseException as identifier:
        typer.echo(f"TEST Failed! == ERROR: {identifier}")
        typer.echo("SNIPPET")
        typer.echo(text)
        typer.Exit(1)
        raise identifier


def main(readme_file: Path):
    readme_lines = readme_file.read_text().split("\n")
    snippets = extract_code_snippets(readme_lines)
    for snip in snippets:
        exec_snippet(snip)
    typer.echo("All snippets in readme executed without error!")


if __name__ == "__main__":
    typer.run(main)
