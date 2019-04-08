import os
import git
import sys
import click
import shutil
from os import PathLike
from string import Template
from slugify import slugify
from collections import namedtuple
from typing import Callable, AnyStr


SETUP = 'setup.py'
SETUP_TEMPLATE = 'setup.py.template'

CLI = 'cli.py'
CLI_TEMPLATE = 'cli.py.template'

TEST = 'test_{}.py'
TEST_TEMPLATE = 'test.py.template'

REQUIREMENTS = 'requirements.txt'
REQUIREMENTS_TEMPLATE = 'requirements.txt.template'

TRAVIS = '.travis.yml'
TRAVIS_TEMPLATE = 'travis.yml.template'
TRAVIS_PYPI_TEMPLATE = 'travis_pypi.yml.template'

GITLAB_CI = '.gitlab-ci.yml'
GITLAB_CI_TEMPLATE = 'gitlab-ci.yml.template'

PROJECT_INIT = '__init__.py'


Step = namedtuple('Step', 'fn index rollback validator divider_up divider_down')


def register_step(index: bool,
                  rollback: AnyStr = None,
                  validator: AnyStr = None,
                  divider_up: Callable = lambda: None,
                  divider_down: Callable = lambda: None) \
        -> Callable:
    """Method decorator for registering steps."""

    def fnc(fn):
        fn._decor_data = Step(**{
            'fn': fn,
            'index': index,
            'rollback': rollback,
            'validator': validator,
            'divider_up': divider_up,
            'divider_down': divider_down
        })
        return fn

    return fnc


def collect_steps(cls):
    """Collect steps defined in methods."""

    cls.steps = list()
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if hasattr(attr, '_decor_data'):
            cls.steps.append(attr._decor_data)

    cls.steps = sorted(cls.steps, key=lambda s: s.index)

    return cls


@collect_steps
class NewProject:
    """Creating skeleton for your new python package project ..."""

    steps = list()

    def __init__(self, destination_path: PathLike):
        self._destination_path = destination_path

        self._project_name = None
        self._project_description = None
        self._project_git_repo = None
        self._project_git_url = None
        self._author_name = None
        self._author_email = None
        self._project_tags = None

        self._use_travis = False
        self._use_pypi = False
        self._pypi_username = None

        self._use_gitlab_ci = False

        self._project_root_path = None
        self._sample_lib_root_path = None
        self._project_app_dir = None

    @register_step(index=0, divider_up=lambda: click.echo(),
                   divider_down=lambda: click.echo())
    def _prompt(self) -> None:
        """Collecting data from user ..."""

        self._project_name = slugify(click.prompt('Enter project name')).replace('-', '_')
        self._project_description = click.prompt('Enter project description')
        self._project_git_repo = click.prompt('Enter project GitHub url (ssh)')
        self._project_git_url = click.prompt('Enter project GitHub url (https)')
        self._author_name = click.prompt('Enter project author name')
        self._author_email = click.prompt('Enter project author e-mail')
        self._project_tags = click.prompt('Enter project project tags')

        click.echo()

        self._use_travis = click.confirm('Do you want to use Travis CI?')
        if self._use_travis:
            self._use_pypi = click.confirm('Do you want to upload your project to pypi.org?')
            self._pypi_username = click.prompt('Enter your pypi.org username')

        self._use_gitlab_ci = click.confirm('Do you want to use Gitlab CI?')

    @register_step(index=1, divider_down=lambda: click.echo())
    def _clone_git_repo(self) -> None:
        """Cloning the repo from GitHub ..."""

        git.Git(self._destination_path).clone(self._project_git_repo)

        self._project_root_path = os.path.join(
            self._destination_path,
            self._project_git_repo.split('/')[-1].split('.git')[0]
        )

        self._sample_lib_root_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__))
        )

    @register_step(index=2, rollback='_remove_git_repo')
    def _create_setup_py(self) -> None:
        """Creating setup.py ..."""

        with open(os.path.join(self._sample_lib_root_path, SETUP_TEMPLATE)) as f:
            t = Template(f.read())
            setup_template = t.substitute(project_name=self._project_name,
                                          project_description=self._project_description,
                                          author_name=self._author_name,
                                          author_email=self._author_email,
                                          project_tags=self._project_tags,
                                          project_github_url=self._project_git_url)

        with open(os.path.join(self._project_root_path, SETUP), 'w') as f:
            f.write(setup_template)

    @register_step(index=3, rollback='_remove_git_repo')
    def _create_requirements_txt(self) -> None:
        """Creating requirements.txt ..."""

        with open(os.path.join(self._sample_lib_root_path, REQUIREMENTS_TEMPLATE)) as f:
            requirements_template = f.read()

        with open(os.path.join(self._project_root_path, REQUIREMENTS), 'w') as f:
            f.write(requirements_template)

    @register_step(index=4, validator='_use_travis', rollback='_remove_git_repo')
    def _create_travis_yml(self) -> None:
        """Creating .travis.yml ..."""

        with open(os.path.join(self._sample_lib_root_path, TRAVIS_TEMPLATE)) as f:
            travis_template = f.read()

        with open(os.path.join(self._project_root_path, TRAVIS), 'w') as f:
            if self._use_pypi:
                with open(os.path.join(self._sample_lib_root_path,
                                       TRAVIS_PYPI_TEMPLATE)) as fi:
                    t = Template(fi.read())
                    travis_pypi_template = t.substitute(
                        pypi_username=self._pypi_username,
                        pypi_encripted_password='_enter_password_here_'
                    )

                    click.echo()
                    click.secho('To enter encrypted pypi.org password in '
                                '.travis.yml do the following:', fg='green')
                    click.secho('- install ruby', fg='green')
                    click.echo(click.style('- install Travis CLI: ', fg='green') +
                               'gem install travis -v 1.8.9 --no-rdoc --no-ri')
                    click.echo(click.style('- go to git repo root and type: ', fg='green') +
                               'travis encrypt your-password-here --add deploy.password')
                    click.echo()
            else:
                travis_pypi_template = ''

            f.write(f'{travis_template}\n{travis_pypi_template}')

    @register_step(index=5, validator='_use_gitlab_ci', rollback='_remove_git_repo')
    def _create_gitlab_ci_yml(self) -> None:
        """Creating .gitlab-ci.yml ..."""

        with open(os.path.join(self._sample_lib_root_path, GITLAB_CI_TEMPLATE)) as f:
            t = Template(f.read())
            gitlab_ci_template = t.safe_substitute(project_name=self._project_name)

        with open(os.path.join(self._project_root_path, GITLAB_CI), 'w') as f:
            f.write(gitlab_ci_template)

    @register_step(index=6, rollback='_remove_git_repo')
    def _create_app_dir(self) -> None:
        """Creating python package app dir ..."""

        self._project_app_dir = os.path.join(self._project_root_path, self._project_name)
        os.makedirs(self._project_app_dir)

    @register_step(index=7, rollback='_remove_git_repo')
    def _create_init(self) -> None:
        """Creating __init__.py ..."""

        with open(os.path.join(self._project_app_dir, PROJECT_INIT), 'w') as f:
            f.write('')

    @register_step(index=8, rollback='_remove_git_repo')
    def _create_cli(self) -> None:
        """Creating cli.py ..."""

        with open(os.path.join(self._sample_lib_root_path, CLI_TEMPLATE)) as f:
            t = Template(f.read())
            setup_template = t.substitute(project_description=self._project_description)

        with open(os.path.join(self._project_app_dir, CLI), 'w') as f:
            f.write(setup_template)

    @register_step(index=9, rollback='_remove_git_repo')
    def _create_tests(self) -> None:
        """Creating tests ..."""

        with open(os.path.join(self._sample_lib_root_path, TEST_TEMPLATE)) as f:
            t = Template(f.read())
            pnc = ''.join([f'{s[0].upper()}{s[1:]}'
                           for s in self._project_name.split('_')])
            test_template = t.substitute(project_name_class=pnc,
                                         project_name_test=self._project_name)

        tests_dir = os.path.join(os.path.dirname(self._project_app_dir), 'tests')
        os.makedirs(tests_dir)

        with open(os.path.join(tests_dir, TEST.format(self._project_name)), 'w') as f:
            f.write(test_template)

    @register_step(index=10, rollback='_remove_git_repo',
                   divider_down=lambda: click.echo())
    def _create_virtual_environment(self) -> None:
        """Creating virtual environment ..."""

        venv_path = os.path.join(self._project_root_path, '.venv')
        os.system(f'python3 -m venv {venv_path}')
        pip_path = os.path.join(self._project_root_path, '.venv', 'bin', 'pip')

        click.echo()
        os.system(f'{pip_path} install -U pip setuptools')
        os.system(f'{pip_path} install -e {self._project_root_path}')

        click.echo()
        os.system(f'{pip_path} list')

        click.echo()
        click.secho('To activate new project virtual environment type:', fg='green')

        venv_activate_path = os.path.join(venv_path, 'bin', 'activate')
        click.secho(f'. {venv_activate_path}', fg='green')

    def _remove_git_repo(self) -> None:
        """Deleting git repository ..."""

        shutil.rmtree(self._project_root_path)

    def run(self) -> None:
        """Run all steps."""

        click.clear()
        click.echo()
        click.secho(NewProject.__doc__, fg='green')

        for step in self.steps:
            if step.validator:
                if not getattr(self, step.validator):
                    continue

            step.divider_up()
            click.echo(step.fn.__doc__)

            try:
                step.fn(self)
            except Exception as e:
                click.echo()
                click.secho(f'An error occurred: {str(e)}.', fg='red')

                if step.rollback:
                    click.secho('Reverting!', fg='red')
                    getattr(self, step.rollback)()

                click.echo()

                sys.exit()

            step.divider_down()
