from setuptools import find_packages, setup

setup(
    name='ai_tool_lib',
    packages=find_packages(include=['src/ai_tool_lib']),
    version='0.0.1',
    description='Library for creating AI chat bot that uses tools to perform tasks and answer questions. ',
    author='Nathan Ogden',
    license='MIT',
    install_requires=['pydantic', 'openai']
)