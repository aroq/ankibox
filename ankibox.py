import re
import os
import urllib
from pathlib import Path
from shutil import copyfile
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option("--input-dir", default="", help="Input directory.")
@click.option("--output-dir", default="", help="Output directory")
@click.option("--name", default="output", help="Name")
@click.option("--anki", is_flag=True)
def many_to_one(input_dir, output_dir, name, anki):
    """Process markdown to anki ready markdown."""
    input_dir = Path(os.getcwd(), input_dir)
    click.echo(f"Input dir: {input_dir}")
    click.echo(f"Output dir: {output_dir}")

    files = list(input_dir.glob("*.md"))
    # print('[%s]' % ', '.join(map(str, result)))
    output_file = Path(os.path.join(output_dir, f"{name}.md"))
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w') as outfile:
        count = len(files)
        i = 0
        for fname in files:
            i += 1
            with open(fname) as infile:
                input_stream = infile.read()
                lines = input_stream.split('\n', 1)

                images = re.findall(r'!\[.*\]\((.+)\)', lines[1])
                for image in images:
                    source_image = urllib.parse.unquote(image)
                    click.echo(f"Image: {source_image}")
                    source_image_file_path = Path(os.path.join(input_dir, source_image))
                    click.echo(f"Image file: {source_image_file_path}")
                    if source_image_file_path.is_file():
                        target_image = Path(os.path.join("images", f"{name}", slugify(source_image)))
                        target_image_file_path = Path(os.path.join(output_dir, target_image))
                        click.echo(f"Image: {image} exists")
                        os.makedirs(os.path.dirname(target_image_file_path), exist_ok=True)
                        copyfile(source_image_file_path, target_image_file_path)
                        lines[1] = lines[1].replace(image, str(target_image))

                if anki:
                    outfile.write("%% " + lines[0])
                    outfile.write("\n\n")
                    outfile.write("%%")
                    outfile.write("\n\n")
                    outfile.write(lines[1])
                else:
                    outfile.write(lines[0])
                    outfile.write("\n\n")
                    outfile.write(lines[1])

                if i < count:
                    outfile.write("\n")
                    outfile.write("---\n\n")
                    

@cli.command()
@click.option("--input-file", default="", help="Input file")
def anki(input_file):
    """Process markdown to anki ready markdown."""

    input_file = Path(os.getcwd(), input_file)
    name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = Path(os.getcwd(), f"{name}-anki.md")

    with open(output_file, 'w') as outfile:
        with open(input_file) as infile:
            input_stream = infile.read()
            headers = re.sub(r'^(#\s.*)\n', r'%% \1\n\n%%\n', input_stream, 0, re.MULTILINE)
            outfile.write(headers)


def slugify(value):
    value = str(re.sub(r'[^\w\s\/\.-]', '', value).strip().lower())
    value = str(re.sub(r'[-\s\/]+', '-', value))

    return value

if __name__ == '__main__':
    cli()
