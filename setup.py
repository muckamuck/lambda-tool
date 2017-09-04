from setuptools import setup
setup(
    name="LambdaTool",
    version="0.0.0",
    packages=['lambdatool'],
    description='Python Lambda utility',
    author='Chuck Muckamuck',
    author_email='Chuck.Muckamuck@gmail.com',
    install_requires=[
        "boto3>=1.4.3",
        "Click>=6.7",
        "PyYAML>=3.12",
        "pymongo>=3.4.0"
    ],
    entry_points="""
        [console_scripts]
        lambdatool=lambdatool.command:cli
    """
)
