from invoke import Collection, Program
from ctypestest import ctypestest

namespace = Collection(ctypestest)
program = Program(version='0.1.0', namespace=namespace)
