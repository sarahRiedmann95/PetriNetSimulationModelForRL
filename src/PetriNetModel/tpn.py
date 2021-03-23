"""
>>> from src.PetriNetModel import tpn
>>> nets = snakes.plugins.load(tpn, 'snakes.nets', 'nets')
>>> from nets import *
>>> n = PetriNet('timed')
>>> n.add_place(Place('p', ['dot']))
>>> n.add_transition(Transition('t', min_time=1.0, max_time=2.0))
>>> t = n.transition('t')
>>> n.add_input('p', 't', Value('dot'))
>>> n.reset()
>>> n.time(0.5)
0.5
>>> t.time, t.enabled(Substitution())
(0.5, False)
>>> n.time(1.0)
0.5
>>> t.time, t.enabled(Substitution())
(1.0, True)
>>> n.time(1.0)
1.0
>>> t.time, t.enabled(Substitution())
(2.0, True)
>>> n.time(1.0)
0.0
"""

import snakes.plugins

from snakes import ConstraintError

@snakes.plugins.plugin("snakes.nets")
def extend (module) :
    class Transition (module.Transition) :
        def __init__ (self, name, guard=None, **args) :
            self.time = None
            self.min_time = args.pop("min_time", 0.0)
            self.max_time = args.pop("max_time", None)
            module.Transition.__init__(self, name, guard, **args)
        def enabled (self, binding, **args) :
            if args.pop("untimed", False) :
                return module.Transition.enabled(self, binding)
            elif self.time is None :
                return False
            elif self.max_time is None :
                return (self.min_time <= self.time) and module.Transition.enabled(self, binding)
            else :
                return (self.min_time <= self.time <= self.max_time) and module.Transition.enabled(self, binding)
    class Place (module.Place) :
        def __init__ (self, name, tokens=[], check=None, **args) :
            self.post = {}
            self.pre = {}
            module.Place.__init__(self, name, tokens, check, **args)
        def reset (self, tokens) :
            module.Place.reset(self, tokens)
            for name in self.post :
                trans = self.net.transition(name)
                if len(trans.modes()) > 0 :
                    trans.time = 0.0
                else :
                    trans.time = None
        def empty (self) :
            module.Place.empty(self)
            for name in self.post :
                self.net.transition(name).time = None
        def _post_enabled (self) :
            return dict((name, self.net.transition(name).time is not None)
                        for name in self.post)
        def add (self, tokens) :
            enabled = self._post_enabled()
            module.Place.add(self, tokens)
            for name in self.post :
                if not enabled[name] :
                    trans = self.net.transition(name)
                    if len(trans.modes()) > 0 :
                        trans.time = 0.0
        def remove (self, tokens) :
            enabled = self._post_enabled()
            module.Place.remove(self, tokens)
            for name in self.post :
                if enabled[name] :
                    trans = self.net.transition(name)
                    if len(trans.modes()) == 0 :
                        trans.time = None
    class PetriNet (module.PetriNet) :
        def reset (self) :
            self.set_marking(self.get_marking())
        def step (self) :
            step = None
            for trans in self.transition() :
                if trans.time is None :
                    continue
                if trans.time < trans.min_time :
                    if step is None :
                        step = trans.min_time - trans.time
                    else :
                        step = min(step, trans.min_time - trans.time)
                elif trans.max_time is None :
                    pass
                elif trans.time <= trans.max_time :
                    if step is None :
                        step = trans.max_time - trans.time
                    else :
                        step = min(step, trans.max_time - trans.time)
            return step
        def time (self, step=None) :
                if step is None :
                    step = self.step()
                else :
                    # bug fix of initial code
                    step_temp = self.step()
                    if step_temp is None:
                        pass
                    else:
                        step = min(step_temp, step)
                if step is None :
                    return None
                for trans in self.transition() :
                    if trans.time is not None :
                        trans.time += step
                return step
    return Transition, Place, PetriNet
