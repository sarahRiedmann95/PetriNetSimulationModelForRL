from random import randint

from src.PetriNetModel import tpn
import snakes.plugins
from src.PetriNetModel.TimedPetriNet import TimedPetriNet
from snakes.nets import MultiSet
import numpy as np

snakes.plugins.load(tpn, "snakes.nets", "snk")
from snk import *


class ModelFactory(TimedPetriNet):
    def __init__(self, net_name="ModelFactory"):
        self.net_name = net_name
        super(ModelFactory, self).__init__(self.net_name)

        self.num_tokens = 3

        self.transitions = []
        self.places = []

        # Rotary table places and transitions
        self.net_place_rt_entry = "RT_Entry"
        self.net_place_rt_exit = "RT_Exit"
        self.net_place_rt_storage = "RT_Storage"
        self.net_place_rt_resource = "RT_Resource"

        self.net_trans_storage_to_exit = "StorageToExit"
        self.net_trans_exit_to_storage = "ExitToStorage"
        self.net_trans_entry_to_exit = "EntryToExit"
        self.net_trans_entry_to_storage = "EntryToStorage"

        # Entry places and transition
        self.net_place_transport = "Transport"
        self.net_place_goods_lower = "GoodsLower"
        self.net_place_goods_upper = "GoodsUpper"
        self.net_place_assembled_goods = "AssembledGoods"

        self.net_trans_prepare_goods = "PrepareGoods"

        # Exit places and transitions
        self.net_place_assembly_station = "AssemblyStation"
        self.net_place_rivets = "Rivets"
        self.net_place_exit = "Exit"

        self.net_trans_assemble = "Assemble"
        self.net_trans_to_exit = "ToExit"

        # Storage place
        self.net_place_storage = "Storage"

        # transitions connecting factory components
        self.net_trans_entry_to_rotary_table = "EntryToRotaryTable"
        self.net_trans_rotary_table_to_exit = "RotaryTableToExit"
        self.net_trans_exit_to_rotary_table = "ExitToRotaryTable"
        self.net_trans_rotary_table_to_storage = "ToStorage"

        self.not_observed_places = [self.net_place_goods_upper, self.net_place_transport, self.net_place_rivets,
                                    self.net_place_exit, self.net_place_storage]

        self.storage_places = [self.net_place_goods_upper, self.net_place_goods_lower, self.net_place_transport,
                               self.net_place_rivets]

        self.resource_places = [self.net_place_rt_resource]

        self.init_model_factory()
        self.init_condition = self.create_init_marking()
        self.reset()

    def init_model_factory(self):
        self.create_rotary_table()
        self.create_entry()
        self.create_exit()
        self.create_storage()

        self.connect_entry_to_rotary_table()
        self.connect_rotary_table_to_exit()
        self.connect_rotary_table_to_storage()

    def create_init_marking(self):
        list_init_tokens = np.resize([1, 2, 1, 2], self.num_tokens)
        mark = {self.net_place_rt_resource: MultiSet(1),
                self.net_place_goods_lower: MultiSet(list_init_tokens),
                self.net_place_goods_upper: MultiSet([1 for _ in range(self.num_tokens)]),
                self.net_place_transport: MultiSet([1 for _ in range(self.num_tokens)]),
                self.net_place_rivets: MultiSet([1 for _ in range(self.num_tokens)])}
        return mark

    def create_rotary_table(self):
        self.places.extend([self.net_place_rt_resource,
                            self.net_place_rt_entry,
                            self.net_place_rt_storage,
                            self.net_place_rt_exit])

        self.transitions.extend([self.net_trans_storage_to_exit,
                                 self.net_trans_exit_to_storage,
                                 self.net_trans_entry_to_exit,
                                 self.net_trans_entry_to_storage])

        self.net.add_place(Place(self.net_place_rt_resource))
        self.net.add_place(Place(self.net_place_rt_entry))
        self.net.add_place(Place(self.net_place_rt_storage))
        self.net.add_place(Place(self.net_place_rt_exit))

        # -----------------------------------------------------------------------------------------------------------------
        self.create_timed_transition(trans_name=self.net_trans_entry_to_exit,
                                     input_places_names=[self.net_place_rt_resource,
                                                         (self.net_place_rt_entry, Variable('a'))],
                                     output_places_names=[self.net_place_rt_resource,
                                                          (self.net_place_rt_exit, Variable('a'))],
                                     time=2)

        # -----------------------------------------------------------------------------------------------------------------
        self.create_timed_transition(trans_name=self.net_trans_entry_to_storage,
                                     input_places_names=[self.net_place_rt_resource,
                                                         (self.net_place_rt_entry, Variable('a'))],
                                     output_places_names=[self.net_place_rt_resource,
                                                          (self.net_place_rt_storage, Variable('a'))],
                                     time=2)

        # -----------------------------------------------------------------------------------------------------------------
        self.create_timed_transition(trans_name=self.net_trans_exit_to_storage,
                                     input_places_names=[self.net_place_rt_resource,
                                                         (self.net_place_rt_exit, Variable('a'))],
                                     output_places_names=[self.net_place_rt_resource,
                                                          (self.net_place_rt_storage, Variable('a'))],
                                     time=2)

        # -----------------------------------------------------------------------------------------------------------------
        self.create_timed_transition(trans_name=self.net_trans_storage_to_exit,
                                     input_places_names=[self.net_place_rt_resource,
                                                         (self.net_place_rt_storage, Variable('a'))],
                                     output_places_names=[self.net_place_rt_resource,
                                                          (self.net_place_rt_exit, Variable('a'))],
                                     time=2)

    def create_entry(self):
        self.places.extend([self.net_place_transport,
                            self.net_place_goods_lower,
                            self.net_place_goods_upper,
                            self.net_place_assembled_goods])

        self.transitions.extend([self.net_trans_prepare_goods])

        self.net.add_place(Place(self.net_place_transport))
        self.net.add_place(Place(self.net_place_goods_lower))
        self.net.add_place(Place(self.net_place_goods_upper))
        self.net.add_place(Place(self.net_place_assembled_goods))

        self.create_timed_transition(trans_name=self.net_trans_prepare_goods,
                                     input_places_names=[(self.net_place_goods_lower, Variable('b')),
                                                         (self.net_place_transport, Variable('a')),
                                                         (self.net_place_goods_upper, Variable('c'))],
                                     output_places_names=[(self.net_place_assembled_goods, Variable('b'))],
                                     time=2)

    def create_exit(self):
        self.places.extend([self.net_place_assembly_station,
                            self.net_place_rivets,
                            self.net_place_exit])

        self.transitions.extend([self.net_trans_assemble,
                                 self.net_trans_to_exit])

        self.net.add_place(Place(self.net_place_assembly_station))
        self.net.add_place(Place(self.net_place_rivets))
        self.net.add_place(Place(self.net_place_exit))

        self.create_timed_transition(trans_name=self.net_trans_assemble,
                                     input_places_names=[(self.net_place_assembly_station, Variable('a')),
                                                         (self.net_place_rivets, Variable('b'))],
                                     output_places_names=[(self.net_place_assembly_station, Expression('a+2'))],
                                     time=4,
                                     trans_guard=Expression('a<=2'))
        self.create_timed_transition(trans_name=self.net_trans_to_exit,
                                     input_places_names=[(self.net_place_assembly_station, Variable('a'))],
                                     output_places_names=[(self.net_place_exit, Variable('a'))],
                                     time=2)

    def create_storage(self):
        self.places.append(self.net_place_storage)

        self.net.add_place(Place(self.net_place_storage))

    def connect_entry_to_rotary_table(self):
        self.transitions.append(self.net_trans_entry_to_rotary_table)

        self.create_timed_transition(trans_name=self.net_trans_entry_to_rotary_table,
                                     input_places_names=[(self.net_place_assembled_goods, Variable('a'))],
                                     output_places_names=[(self.net_place_rt_entry, Variable('a'))],
                                     time=2)

    def connect_rotary_table_to_exit(self):
        self.transitions.extend([self.net_trans_rotary_table_to_exit,
                                 self.net_trans_exit_to_rotary_table])

        self.create_timed_transition(trans_name=self.net_trans_rotary_table_to_exit,
                                     input_places_names=[(self.net_place_rt_exit, Variable('a'))],
                                     output_places_names=[(self.net_place_assembly_station, Variable('a'))],
                                     time=2)
        self.create_timed_transition(trans_name=self.net_trans_exit_to_rotary_table,
                                     input_places_names=[(self.net_place_assembly_station, Variable('a'))],
                                     output_places_names=[(self.net_place_rt_exit, Variable('a'))],
                                     time=2)

    def connect_rotary_table_to_storage(self):
        self.transitions.append(self.net_trans_rotary_table_to_storage)

        self.create_timed_transition(trans_name=self.net_trans_rotary_table_to_storage,
                                     input_places_names=[(self.net_place_rt_storage, Variable('a'))],
                                     output_places_names=[(self.net_place_storage, Variable('a'))],
                                     time=2)

    def get_transitions(self):
        return self.transitions

    def get_active_transitions(self):
        active_trans = []
        for transition in self.transitions:
            if self.is_timed_transition_active(transition):
                active_trans.append(transition)
        return active_trans

    def is_any_timed_transition_active(self):
        for transition in self.transitions:
            if self.is_timed_transition_active(transition):
                return True
        return False

    def is_any_action_possible(self):
        for transition in self.transitions:
            modes = self.net.transition(transition).modes()
            if modes != []:
                return True

        if self.is_any_timed_transition_active():
            return True
        else:
            return False

    def get_total_token_count(self):
        all_places = self.places + self.hidden_places
        token_count = 0
        for place in all_places:
            token_count += len(self.get_place_tokens(place))
        return token_count

    def remove_token_from_place(self, place, token):
        self.get_place_tokens(place).remove(token)

    def collision_detected(self):
        for place in self.places:
            if self.is_collision_detected_on_place(place):
                return True
        return False

    def is_collision_detected_on_place(self, place):
        if self.is_storage_place(place) or len(self.get_place_tokens(place)) <= 1:
            return False
        else:
            return True

    def is_resource_place(self, place):
        if place in self.resource_places:
            return True
        else:
            return False

    def is_storage_place(self, place):
        if place in self.storage_places:
            return True
        else:
            return False

    def is_not_observed_place(self, place):
        if place in self.not_observed_places:
            return True
        else:
            return False
