from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='${project_name}',
    version='0.1.0',

    description='${project_description}',
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='${project_github_url}',
    licence='MIT',

    author='${author_name}',
    author_email='${author_email}',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='${project_tags}',

    packages=find_packages(),
    install_requires=[
        'click~=7.0',
    ],

    project_urls={
        'Source': '${project_github_url}',
    },

    entry_points={
        'console_scripts': [
            '${project_name}=${project_name}.cli:cli'
        ],
    },
)
