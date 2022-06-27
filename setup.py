from setuptools import setup

setup(
    name='OpenAI Bot',
    version='1.0',
    long_description=__doc__,
    packages=['openaibot'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)