#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015-2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import os.path
import subprocess

import yaml

def get_dependencies(role):
    names = []
    meta = os.path.join('roles/', role, 'meta', 'main.yml')
    if os.path.isfile(meta):
        with open(meta) as stream:
            data = yaml.load(stream)

            if data is None:
                return names

            if 'dependencies' in data:
                dependencies = data['dependencies']

                if dependencies is None:
                    return names

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

    return names


def main():
    options = _parse_args()

    tree = {}

    os.chdir(options.dir)

    for role in os.listdir('roles'):
        tree[os.path.basename(role)] = get_dependencies(role)

    output = []

    output.append('digraph {')

    for role, dependencies in tree.items():
        for dependency in dependencies:
            output.append('"{}" -> "{}"'.format(role, dependency))

    output.append( '}')

    print('\n'.join(output))


    with open('role-dependencies.dot', 'w') as stream:
        for line in output:
            stream.write(line)

    subprocess.check_call(['dot', '-Tpdf', '-o', 'role-dependencies.pdf', 'role-dependencies.dot'])
    subprocess.check_call(['dot', '-Tsvg', '-o', 'role-dependencies.svg', 'role-dependencies.dot'])

                        

def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('dir')
    options = parser.parse_args()

    return options

if __name__ == '__main__':
    main()
