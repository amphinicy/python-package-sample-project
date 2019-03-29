from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='sample',
    version='1.0.0',

    description='A sample project on how to make a python package',
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='https://github.com/amphinicy/python-package-sample-project',
    licence='MIT',

    author='Ivan Arar',
    author_email='ivan.arar@amphinicy.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='sample, python, package',

    packages=find_packages(),
    package_data={'': ['cli.py.template',
                       'test.py.template',
                       'setup.py.template',
                       'requirements.txt.template',
                       'travis.yml.template',
                       'travis_pypi.yml.template']},
    install_requires=[
        'click~=7.0',
        'GitPython~=2.1.11',
        'python-slugify~=3.0.0',
    ],

    project_urls={
        'Source': 'https://github.com/amphinicy/python-package-sample-project',
    },

    entry_points={
        'console_scripts': [
            'sample=sample.cli:cli'
        ],
    },
)
