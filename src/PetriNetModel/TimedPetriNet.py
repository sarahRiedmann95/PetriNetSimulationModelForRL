from src.PetriNetModel import tpn
import snakes.plugins

snakes.plugins.load(tpn, "snakes.nets", "snk")
from snk import *
from snakes.nets import MultiSet, Marking


class TimedPetriNet:
    hidden_place_name_extension = "_place_hidden"
    hidden_trans_name_extension = "_trans_hidden"

    def __init__(self, net_name):
        self.clock = 0.0
        self.net_name = net_name

        self.hidden_transitions = []
        self.hidden_places = []

        self.net = PetriNet(net_name)
        self.init_condition = Marking()
        self.previous_marking = self.init_condition
        self.reset()

    def reset(self):
        self.clock = 0
        self.net.reset()
        self.set_net_marking(self.init_condition)

    def time_step(self):
        self.clock += self.net.time(0.1)
        return self.clock

    def fast_time_step(self):
        stp = self.net.step()
        if stp is None:
            self.clock += self.net.time(0.1)
        else:
            self.clock += self.net.time()
        return self.clock

    def fire_transition(self, trans_name):
        modes = self.net.transition(trans_name).modes()

        if modes != [] and self.net.transition(trans_name).enabled(modes[0]):
            self.previous_marking = self.get_net_marking()
            self.net.transition(trans_name).fire(modes[0])
            return True
        else:
            return False

    def fire_hidden_transitions(self):
        """
        hidden transitions are used to implement timed transitions...
        :return: None
        """
        for hidden_transition in self.hidden_transitions:
            self.fire_transition(hidden_transition)

    def create_timed_transition(self, input_places_names, output_places_names, trans_name, time, trans_guard=None):
        """
        :param input_places_names:  List of input place names of the transition; Could be a tuple to define
                                    ArcExpressions
        :param output_places_names: List of output place names of the transition;
                                   Could be a tuple to define ArcExpressions, in that case order is important
        :param trans_name: name of the timedTransition, also used to name hidden place & trans
        :param time: How long the transition takes
        :param trans_guard: transition guard as defined by snakes toolbox, e.g. a logical expression such as x>4
        :return: none, modifies self
        """

        # Visible transition
        if trans_guard is None:
            self.net.add_transition(Transition(trans_name, min_time=0, max_time=None))
        else:
            self.net.add_transition(Transition(trans_name, guard=trans_guard, min_time=0, max_time=None))

        # Hidden nodes
        self.net.add_place(Place(trans_name + self.hidden_place_name_extension))
        self.net.add_transition(Transition(trans_name + self.hidden_trans_name_extension, min_time=time, max_time=time))
        self.hidden_transitions.append(trans_name + self.hidden_trans_name_extension)
        self.hidden_places.append(trans_name + self.hidden_place_name_extension)

        arc_expression = []
        for input_place_name in input_places_names:
            if type(input_place_name) == tuple:
                self.net.add_input(input_place_name[0], trans_name, input_place_name[1])
                arc_expression.append(input_place_name[1])
            else:
                self.net.add_input(input_place_name, trans_name, Variable('var'))
                arc_expression.append(Variable('var'))

        for output_place_name in output_places_names:
            if type(output_place_name) == tuple:
                self.net.add_output(output_place_name[0], trans_name + self.hidden_trans_name_extension,
                                    output_place_name[1])
            else:
                self.net.add_output(output_place_name, trans_name + self.hidden_trans_name_extension, Variable('var'))

        self.net.add_output(trans_name + self.hidden_place_name_extension, trans_name, MultiArc(arc_expression))
        self.net.add_input(trans_name + self.hidden_place_name_extension, trans_name + self.hidden_trans_name_extension,
                           MultiArc(arc_expression))

    def is_timed_transition_active(self, transition_name):
        if self.get_place_tokens(transition_name + self.hidden_place_name_extension) == []:
            return False
        else:
            return True

    def is_marking_part_of_current_marking(self, marking):
        current_marking = self.get_net_marking()
        for key in marking:
            if current_marking.get(key) is not None:
                if marking.get(key) == current_marking.get(key):
                    continue
                else:
                    return False
            else:
                return False
        return True

    def has_place_changed(self, place_name):
        current_marking = self.get_net_marking()
        if current_marking[place_name] != self.previous_marking[place_name]:
            return True
        else:
            return False

    def has_net_changed(self):
        current_marking = self.get_net_marking()
        if current_marking != self.previous_marking:
            return True
        else:
            return False

    def set_place_tokens(self, place_name, tokens):
        if type(tokens) == MultiSet:
            temp_marking = self.get_net_marking()
            temp_marking[place_name] = tokens
            self.set_net_marking(temp_marking)
        elif type(tokens) == list:
            temp_marking = self.get_net_marking()
            temp_marking[place_name] = MultiSet(tokens)
            self.set_net_marking(temp_marking)

    def get_place_tokens(self, place_name):
        return self.net.place(place_name).tokens

    def set_init_marking(self, new_marking):
        if type(new_marking) == Marking:
            self.init_condition = new_marking
        elif type(new_marking) == dict:
            self.init_condition = Marking(new_marking)

    def set_net_marking(self, new_marking):
        self.previous_marking = self.get_net_marking()

        if type(new_marking) == Marking:
            self.net.set_marking(new_marking)
        elif type(new_marking) == dict:
            self.net.set_marking(Marking(new_marking))

    def get_net_marking(self):
        return self.net.get_marking()
