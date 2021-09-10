"""Build static HTML site from directory of HTML templates and plain files."""
import pathlib
import json
import os
from distutils.dir_util import copy_tree
import sys
import jinja2
import click
# from click.types import Paths


@click.command()
@click.option('-o', '--output', help='Output directory.', type=click.Path())
@click.option('-v', '--verbose', help='Print more output.', is_flag=True)
@click.argument('INPUT_DIR', type=click.Path())
def render(output, verbose, input_dir):
    """Templated static website generator."""
    # click.echo(click.format_filename(input_dir))
    is_dir = os.path.isdir(input_dir)
    if not is_dir: #catches input dir error
        print("Input directory doesn't exist\n")
        sys.exit(1)
    json_file_path = pathlib.Path(input_dir+'/config.json')
    try:
        with open(json_file_path) as config:
            try: #json error
                config = json.load(config)
            except ValueError:
                print("Error opening config file\n")
                sys.exit(1)
            try: #get the template environment
                template_env = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(str(input_dir)),
                        autoescape=jinja2.select_autoescape(['html', 'xml']),
                )
            except jinja2.TemplateError: #throw template errors
                print("Error with setting up the template enviornment\n")
                sys.exit(1)
            input_dir = pathlib.Path(input_dir)  # convert str to Path object
            output_dir = input_dir/"html"
            if output: # sets output dir based on output arg
                output_dir = pathlib.Path(output)
            is_dir = os.path.isdir(output_dir)
            if is_dir: #throws error if output dir already exists
                print("Output directory already exists\n")
                sys.exit(1)
            os.makedirs(output_dir) #creates output directory
            if os.path.isdir(input_dir/"static"): #copies css if needed
                copy_tree(str(input_dir/"static"),str(output_dir))
                if verbose:
                    print("Copied %s -> %s" %(str(input_dir/"static"),output_dir))
            for data in config:
                try:
                    template = template_env.get_template('templates/'+data["template"])
                except jinja2.TemplateError:
                    print("Error with opening the template file\n")
                    sys.exit(1)
                url = data['url'].lstrip("/")  # remove leading slash
                output_path = output_dir/url
                is_dir = os.path.isdir(output_path)
                if not is_dir:
                    os.makedirs(output_path) #creates output path
                output_file = output_path/"index.html"
                try:
                    with open(output_file,"w") as finished_template: #writes template
                        for i in data["context"]:
                            finished_template.write(template.render({i:data['context'][i]}))
                        if verbose:
                            print("Rendered %s -> %s" %(data["template"],output_path))
                except FileNotFoundError:
                    print("Error opening file to write")
                    sys.exit(1)
    except FileNotFoundError:
        print("Json file doesn't exist")
        sys.exit(1)
    # print(output_path)
    # with open(os.path.join(output_path,"index.html"), "w") as file:
    #     toFile = template.render(words=data['context']['words'])
    #     file.write(toFile)
    # p = pathlib.Path(input_dir)
    # config = load(p)


def main():
    """Top level command line interface."""
    # print("Hello world!")
    render()


if __name__ == "__main__":
    main()
