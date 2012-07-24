# A suggestion to make it easier for developers to build the development
# environment is to use a combination of virtualenv, virtualenvwrapper and a
# requirements.txt file. This ensures that everybody uses similar versions of
# software.
#
# Here is how to get started.
#
#     $ pip install virtualenv
#     $ pip install virtualenvwrapper
#
# Edit .bashrc and append:
#
#     export WORKON_HOME=$HOME/.virtualenvs
#     source /usr/local/bin/virtualenvwrapper.sh
#
# On Mac, the path to virtualenvwrapper.sh is:
# /usr/local/share/python/virtualenvwrapper.sh.
#
# Afterwards it is easy to build and activate the development environment:
#
#     $ mkvirtualenv -r requirements.txt -p /usr/bin/python2.6 adslabs 
#     $ workon adslabs
