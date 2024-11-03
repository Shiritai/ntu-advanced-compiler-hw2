from . import value, const, compute, control, trivial, ssa

for t in (value, const, compute, control, trivial, ssa):
    t.register_type()
