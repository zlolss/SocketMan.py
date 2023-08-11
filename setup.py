import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
  long_description = fh.read()

setuptools.setup(
  name="socketman",
  version="0.1.4",
  python_requires=">=3.6",
  author="zloss",
  author_email="zlols@foxmail.com",
  description="websocket client or server, easy to use.",
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