#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
build_conda_recipes_index

Generate an HTML page listing package.name and package.version from meta.yaml files

Requirements:

* PyYAML::

  pip install pyyaml
  conda install pyyaml

"""

import cgi
import collections
import codecs
import datetime
import fnmatch
import logging
import os

import yaml

log = logging.getLogger(__name__)


def list_meta_yamls(repopath, followlinks=True):
    for root, dirs, files in os.walk(repopath, followlinks=followlinks):
        for name in files:
            if fnmatch.fnmatch(name, 'meta.yaml'):
                yield os.path.join(root, name)


def urljoin(a, b):
    return a + '/' + b  # XXX


def urlencode(x):
    return x  # XXX


def build_conda_recipes_index(fileobj, repopath, meta_yamls,
                              skip_parse_exceptions=False):
    """mainfunc

    Arguments:
         fileobj (fileobj): fileobj to .write to
         repopath (str): path to the conda-recipes repository

    Returns:
        fileobj: fileobj passed in
    Raises:
        Exception: ...
    """
    current_git_rev = "..."
    build_date = datetime.datetime.now().isoformat()
    f = fileobj
    f.write("<!DOCTYPE html>\n")
    f.write("<html><head><title>conda-recipes %s</title></head>\n" % build_date)
    f.write("<body>\n")
    f.write("<h1>conda-recipes</h1>\n")
    f.write("<span>{build_date}</span>\n".format(build_date=build_date))
    f.write("<span>{git_rev}</span>\n".format(git_rev=current_git_rev))
    f.write("<table><tr><th>package</th><th>version</th><th></th></tr>\n")

    errs = collections.OrderedDict()

    for meta_yaml_path in meta_yamls:
        with codecs.open(meta_yaml_path, encoding='utf8') as yamlfile:
            log.debug("read %r", meta_yaml_path)
            try:
                meta_yaml = yaml.load(yamlfile)
            except yaml.parser.ParserError as e:
                log.exception(e)
                errs.setdefault(meta_yaml_path, [])
                errs[meta_yaml_path].append(e)
                if skip_parse_exceptions:
                    pass
        package = meta_yaml.get('package', {})
        if not package:
            name = ''
            version = ''
            comment = "Could not read 'package:' from %r" % meta_yaml_path
        else:
            name = unicode(package.get('name'))
            version = unicode(package.get('version'))
            comment = ''
        f.write((
            '<tr><td><a href="{url}">{name}<a></td><td>{version}</td>'
            '<td>{comment}</td></tr>\n')
            .format(
                url=urljoin(
                    'https://github.com/conda/conda-recipes/blob/master',
                    urlencode(meta_yaml_path)),  # XXX
                name=cgi.escape(name),
                version=cgi.escape(version),
                comment=cgi.escape(comment) if comment else ""))
    f.write("</table></body></html>\n")


import unittest


class Test_build_conda_recipes_index(unittest.TestCase):

    def setUp(self):
        pass

    def test_list_meta_yamls(self):
        repopath = os.path.dirname(__file__)
        output = list_meta_yamls(repopath)
        self.assertTrue(hasattr(output, '__iter__'))
        output = list(output)
        self.assertTrue(len(output))
        for x in output:
            self.assertTrue(x.endswith(os.path.sep + 'meta.yaml'))

    def test_build_conda_recipes_index(self):
        repopath = os.path.dirname(__file__)
        meta_yamls = list_meta_yamls(repopath)
        with codecs.open('index.html', 'w', encoding='utf8') as f:
            build_conda_recipes_index(f, repopath, meta_yamls)

    def tearDown(self):
        pass


def main(argv=None):
    """
    Main function

    Keyword Arguments:
        argv (list): commandline arguments (e.g. sys.argv[1:])
    Returns:
        int:
    """
    import logging
    import optparse

    prs = optparse.OptionParser(usage="%prog : args")

    prs.add_option('-v', '--verbose',
                   dest='verbose',
                   action='store_true',)
    prs.add_option('-q', '--quiet',
                   dest='quiet',
                   action='store_true',)
    prs.add_option('-t', '--test',
                   dest='run_tests',
                   action='store_true',)

    loglevel = logging.INFO
    (opts, args) = prs.parse_args(args=argv)
    if opts.verbose:
        loglevel = logging.DEBUG
    elif opts.quiet:
        loglevel = logging.ERROR
    logging.basicConfig(level=loglevel)
    argv = list(argv) if argv else []
    log.debug('argv: %r', argv)
    log.debug('opts: %r', opts)
    log.debug('args: %r', args)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        return unittest.main()

    EX_OK = 0
    output = build_conda_recipes_index()
    return EX_OK


if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv[1:]))
