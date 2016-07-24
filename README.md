# Installation

1. Clone this repo and navigate to it
```
git clone https://github.com/lilorox/pysynodl
```

2. Set up a virtualenv (install python-virtualenv or python3-virtualenv, depending on your OS or just pip install virtualenv)
```
[[ ! -d ~/.virtualenvs ]] && mkdir ~/.virtualenvs
virtualenv -p /usr/bin/python3 ~/.virtualenvs/pysynodl
```

3. Enter the virtualenv and install dependencies
```
cd pysnodl
workon pysynodl
pip install -r requirements.txt
```

4. Run the application
```
./pysynodl.py --help
```
