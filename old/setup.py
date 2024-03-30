import setuptools
import os

with open("README.md", "r", encoding='utf-8') as fh:
  long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'socketman', 'version.py')) as f:
    exec(f.read(), about)

setuptools.setup(
  name="socketman",
  version=about['__version__'],
  python_requires=">=3.6",
  author="zlols",
  author_email="zlols@foxmail.com",
  description="Send arbitrary Python objects via websockets",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/zlolss/SocketMan.py.git",
  py_modules=['socketman'],
  install_requires=[
        'websockets'
    ],
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3 :: Only",
  "License :: OSI Approved :: MIT License",
  #"Operating System :: OS Independent",
  ],
)
