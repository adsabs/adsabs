We have agreed that all documentation is inside the source code.
We don't know yet which engine to use, there were two options
 - Sphinx (the most popular, used by Python website, Flask itself):
   http://sphinx.pocoo.org/
 - Invenio uses Epydoc: http://epydoc.sourceforge.net/

Sphinx is a very neat option and Epydoc seems to be a dead project. Sphinx uses
reStructuredText as its markup language where Epydoc uses Epytext. Epydoc also
supports reStructuredText so a suggestion is to start documenting with
reStructuredText and implement the documentation generator at a later notice.

This folder should contain automatically generated documentation.

Plus perhaps what doesn't fit inside the source code, ie. outline
of the modules, links to important docs...

