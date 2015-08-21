#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

import argparse
import os.path

import yaml

def main():
    options = _parse_args()

    tree = {}

    for role in options.role:
        meta = os.path.join(role, 'meta', 'main.yml')
        if os.path.isfile(meta):
            with open(meta) as stream:
                data = yaml.load(stream)

                if data is None:
                    continue

                if 'dependencies' in data:
                    dependencies = data['dependencies']

                    names = []

                    for dependency in dependencies:
                        name = dependency

                        try:
                            name = list(dependency.keys())[0]
                        except TypeError:
                            pass
                        except AttributeError:
                            pass

                        try:
                            name = dependency['role']
                        except TypeError:
                            pass
                        except KeyError:
                            pass

                        names.append(name)

                    tree[os.path.basename(role)] = names

    output = []

    output.append('digraph {')

    for role, dependencies in tree.items():
        for dependency in dependencies:
            output.append('"{}" -> "{}"'.format(role, dependency))

    output.append( '}')

    print('\n'.join(output))



                        

def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('role', nargs='+')
    options = parser.parse_args()

    return options

if __name__ == '__main__':
    main()
