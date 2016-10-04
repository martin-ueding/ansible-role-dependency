#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015-2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import glob
import os.path
import subprocess

import yaml

def get_from_multiple(dependency):
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

    return name


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
                names.append(get_from_multiple(dependency))

    return names


def get_used_roles(playbook):
    with open(playbook) as stream:
        data = yaml.load(stream)

    names = []
    for task in data:
        if not 'roles' in task:
            continue

        for role in task['roles']:
            names.append(get_from_multiple(role))

    print(names)
    return names


def main():
    options = _parse_args()

    pwd = os.getcwd()

    tree = {}
    tree2 = {}

    os.chdir(options.dir)

    for role in os.listdir('roles'):
        tree[os.path.basename(role)] = get_dependencies(role)

    for playbook in glob.glob('*.yml'):
        base, ext = os.path.splitext(playbook)
        tree2[base] = get_used_roles(playbook)

    output = []

    output.append('''
                  digraph {
                  rankdir=LR
                  ''')

    for role, dependencies in tree.items():
        for dependency in dependencies:
            output.append('"{}" -> "{}"'.format(role, dependency))

    for playbook, dependencies in tree2.items():
        output.append('"{}" [shape=rectangle]'.format(playbook))
        for dependency in dependencies:
            output.append('"{}" -> "{}"'.format(playbook, dependency))

    output.append( '}')

    print('\n'.join(output))

    os.chdir(pwd)

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
