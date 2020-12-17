from setuptools import setup
import os


def find_data(starting_dir, the_dir):
    original_cwd = os.getcwd()
    tree = []
    try:
        os.chdir(starting_dir)
        for folder, subs, files in os.walk(the_dir):
            for file in files:
                tree.append('{}/{}'.format(folder, file))
    except Exception:
        pass

    os.chdir(original_cwd)
    return tree


setup(
    name='LambdaTool',
    version='0.8.7',
    packages=['lambdatool'],
    description='Python Lambda utility',
    author='Chuck Muckamuck',
    author_email='Chuck.Muckamuck@gmail.com',
    include_package_data=True,
    package_data={'lambdatool': find_data('lambdatool', 'template')},
    install_requires=[
        'boto3>=1.4.3',
        'GitPython>=2.1.7',
        'Click>=6.7',
        'PyYAML>=3.12',
        'pymongo>=3.4.0',
        'stackility>=0.3',
        'Mako>=1.0.6'
    ],
    entry_points="""
        [console_scripts]
        lambdatool=lambdatool.command:cli
    """
)
