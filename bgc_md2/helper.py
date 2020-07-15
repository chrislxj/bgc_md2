from . import models
from IPython.display import Math
from IPython.display import display
from bgc_md2.models.helpers import computable_mvars
from bgc_md2.models.helpers import get_single_mvar_value
from bgc_md2.resolve.mvars import CompartmentalMatrix
from pathlib import Path
from sympy import latex
import ipywidgets as widgets
import nbformat as nbf
import pkgutil


def list_models():
    exclude_path = Path('./exclude-models.txt')
    if exclude_path.exists():
        exclude_lines = set(line.strip() for line in open(exclude_path))
        exclude_models = set(name for name in exclude_lines
                             if name and not name.startswith('#'))
    else:
        exclude_models = set()
    sub_mod_pkgs= [tup[1] for tup in pkgutil.iter_modules(models.__path__)
                   if tup[2] and tup[1] not in exclude_models]
    return sub_mod_pkgs


def list_models_md():
    names = list_models()
    links = ["[{name}](/tmp/{name})".format(name=name) for name in names]
    return "".join(links)


def funcmakerInsertLink(grid,i,j,name):
    def insert_link(b):
        # called for side effect on grid object
        tmpDirPath= Path("./tmp") # has to be relative for jupyter to open the file on click (so the exact location depends on where the notebook server was started)
        tmpDirPath.mkdir(exist_ok=True)   
        suffix=".ipynb"
        nbPath=tmpDirPath.joinpath(name+suffix)
        createSingleModelNb(name,nbPath)
        grid[i,j]=widgets.HTML(
            value="""
            <a href="{path}" target="_blank">{text}</a>
            """.format(
                    path = nbPath.as_posix(),
                    text = name+suffix
                )
        )

    return insert_link

def createSingleModelNb(modelName,ReportFilePath):
    # this will be specific to the model and depend on the 
    # available information
    nb = nbf.v4.new_notebook()
    text = """\
    # My first automatic Jupyter Notebook
    This is an auto-generated notebook."""
    code = """\
    %pylab inline
    hist(normal(size=2000), bins=50);"""

    nb['cells'] = [nbf.v4.new_markdown_cell(text),
               nbf.v4.new_code_cell(code) ]
    nbf.write(nb,ReportFilePath)


#################################################################################
def funcmakerInsertLinkInToBox(grid,name):
    def insert_link(b):
        # called for side effect on grid object
        tmpDirPath= Path("./tmp") # has to be relative for jupyter to open the file on click (so the exact location depends on where the notebook server was started)
        tmpDirPath.mkdir(exist_ok=True)   
        suffix=".ipynb"
        nbPath=tmpDirPath.joinpath(name+suffix)
        createSingleModelNb(name,nbPath)
        old_chs=grid.children
        new_chs=( 
            widgets.HTML(
                value="""
                <a href="{path}" target="_blank">{text}</a>
                """.format(
                        path = nbPath.as_posix(),
                        text = name+suffix
                    )
             )
        ,) 
        # we change the children tuple
        grid.children=old_chs + new_chs

    return insert_link

def modelVBox(modelName):
    
    mvs=computable_mvars(modelName)
    res=get_single_mvar_value(CompartmentalMatrix,modelName)
    def output(var):
        res=get_single_mvar_value(var,modelName)
        out = widgets.Output()
        with out:
            display(var.__name__+"=")
            display(Math(latex(res)))
            # The latex could be filtered to display subscripts better
            #display(res)
        return out

    box= widgets.VBox(
        [
            widgets.HTML(value="""
                <h1>{name}</h1>
                This model specific overview page depends on the available 
                properties
                """.format(name=modelName)
            )
            ,
            widgets.HTML(
                "computable_mvars( perhaps as links to the docs or some graph ui ...)"
                +"<ol>\n"
                +"\n".join(["<li> "+var.__name__+" </li>" for var in mvs])
                +"</ol>\n"
            )
        ]
        +
        [ output(var) for var in mvs ]
    )
    b =  widgets.Button(
                    layout=widgets.Layout(width='auto', height='auto'),
                    description="Create notebook \n from template"
                    )
    b.on_click(funcmakerInsertLinkInToBox(box,modelName))
    box.children=box.children+(b,)
    return box 

#################################################################################
def funcmakerInsertLinkInRow(grid,names,i):
    def insert_link(b):
        # called for side effect on g
        tmpDirPath= Path("./tmp") #has to be relative for jupyter to open the file
        tmpDirPath.mkdir(exist_ok=True)   
        suffix=".ipynb"
        nbPath=tmpDirPath.joinpath(names[i]+suffix)
        createSingleModelNb(names[i],nbPath)
        grid[i,9]=widgets.HTML(
            value="""
            <a href="{path}" target="_blank">{text}</a>
            """.format(
                    path = nbPath.as_posix(),
                    text = names[i]+suffix
                )
        )

    return insert_link
def modelListGridBox():
    names = list_models()
    buttons=list()
    nrows = len(names)
    grid = widgets.GridspecLayout(nrows, 10)
    for i in range(nrows):
        mn=names[i]
        grid[i, 0] = widgets.Text(
                layout=widgets.Layout(width='auto', height='auto'),
                value = names[i]
        )
        res=get_single_mvar_value(CompartmentalMatrix,mn)
        out = widgets.Output()
        with out:
            display(res)
        grid[i,1:7] =out

        b =  widgets.Button(
                        layout=widgets.Layout(width='auto', height='auto'),
                        description="Create notebook \n from template"
                    )
        b.on_click(funcmakerInsertLinkInRow(grid,names,i))
        grid[i, 8] = b
    return grid
