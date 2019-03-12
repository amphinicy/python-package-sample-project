import click
from io import StringIO
from typing import AnyStr
from contextlib import redirect_stdout


def the_zen_of_python() -> None:
    """The Zen of Python, by Tim Peters."""

    with StringIO() as buf, redirect_stdout(buf):

        # By making this import statement, the Zen of
        # Python is being printed in standard output.
        # Let's catch it and apply some coloring and
        # styling stuff on it.
        import this

        output = buf.getvalue()

    blank = align_middle()
    color_kwargs = {'fg': 'white', 'bg': 'blue'}

    click.clear()
    click.secho(blank, **color_kwargs)
    click.secho(blank, **color_kwargs)

    for i, line in enumerate(output.split('\n')):
        if i == 0:
            line = line.upper()
        click.secho(align_middle(line), **color_kwargs)

    click.secho(blank, **color_kwargs)


def align_middle(text: AnyStr = '',
                 space: AnyStr = ' ') -> AnyStr:
    """Add left and right spaces for text to
    be in the middle of the terminal screen."""

    # get the screen width
    screen_width = click.get_terminal_size()[0]

    # calculate spaces on both side of the text to
    # populate the rest of the screen with spaces
    spaces = int((screen_width - len(text)) / 2) * space

    # add one more space character at the right end
    # if it is not the same width as terminal screen
    postfix = space * (screen_width -
                       (len(spaces)*2 + len(text)))

    return f'{spaces}{text}{spaces}{postfix}'
