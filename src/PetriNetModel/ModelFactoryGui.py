import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

from enum import Enum


class Position(Enum):
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4


class SimulationSpeed(Enum):
    SLOW = 100
    FAST = 1


class Colours(Enum):
    LIGHT_BLUE = '#03a9fc'
    DARK_BLUE = '#0241b8'
    LIGHT_GREEN = '#0bdb15'
    GREEN = 'green'
    DARK_GREEN = '#017a11'
    RED = '#fa0f2e'
    GREY = 'grey'
    LIGHT_GREY = '#b8b8b8'
    VERY_LIGHT_GREY = '#e6e6e6'


def get_value_between_coordinates(x1, x2, factor=1 / 2):
    return x1 + (x2 - x1) * factor


class Popup(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.wm_title("Info")

        master_x = master.winfo_rootx()
        master_y = master.winfo_rooty()

        popup_x = master_x + 500
        popup_y = master_y + 350

        self.geometry(f'+{popup_x}+{popup_y}')

        lbl = ttk.Label(self, text="This Button is used with the Q-Learning implementation.\nIf you are interested in "
                                   "the complete version contact:\n\nsriedmann.its-m2019@fh-salzburg.ac.at or\n"
                                   "jharb.its-m2019@fh-salzburg.ac.at")
        lbl.pack(side="top", fill="x", pady=20, padx=20)

        btn = ttk.Button(self, text="OK", command=self.destroy)
        btn.pack()

        self.transient(master)
        self.grab_set()
        master.wait_window(self)


class Gui(Frame):
    # used outside of this class
    speed = SimulationSpeed.SLOW
    perform_q_learning = False
    reset = False
    save_q = False
    save_stats = False

    # UI
    window_height = 750
    window_width = 1200

    canvas_width = window_width - 40
    canvas_height = window_height - 100

    circle_radius = 25
    rect_width, rect_height = 8, 40

    def popup(self):
        Popup(self)

    def __init__(self, model_factory, root):
        super().__init__()

        self.model_factory = model_factory

        # place names ---------------------------------------------------------
        self.place_name_entry_transport = "Transport"
        self.place_name_entry_lower_goods = "Lower goods"
        self.place_name_entry_upper_goods = "Upper goods"
        self.place_name_assembled_goods = "Assembled goods"

        self.place_name_rt_entry = "RT Entry"
        self.place_name_rt_ready = "RT ready"
        self.place_name_rt_exit = "RT Exit"
        self.place_name_rt_storage = "RT Storage"

        self.place_name_assembly_station = "Assembly station"
        self.place_name_rivets = "Rivets"
        self.place_name_exit = "Exit"

        self.place_name_storage = "Storage"

        # trans names ---------------------------------------------------------
        self.trans_name_assemble_goods = "Assemble goods"
        self.trans_name_goods_to_rt = "Goods to RT"

        self.trans_name_rt_entry_to_rt_storage = "RT Entry to RT Storage"
        self.trans_name_rt_entry_to_rt_exit = "RT Entry to RT Exit"
        self.trans_name_rt_exit_to_rt_storage = "RT Exit to RT Storage"
        self.trans_name_rt_storage_to_rt_exit = "RT Storage to RT Exit"

        self.trans_name_product_to_storage = "Product to Storage"

        self.trans_name_assembly_to_rt_exit = "Assembly to RT Exit"
        self.trans_name_rt_exit_to_assembly = "RT Exit to Assembly"
        self.trans_name_install_rivets = "Install rivets"
        self.trans_name_product_to_exit = "Product to Exit"

        # rotaryTable ---------------------------------------------------------
        self.net_rt_entry_name = model_factory.net_place_rt_entry
        self.net_rt_exit_name = model_factory.net_place_rt_exit
        self.net_rt_storage_name = model_factory.net_place_rt_storage
        self.net_rt_resource_name = model_factory.net_place_rt_resource

        self.net_rt_storage_to_exit_name = model_factory.net_trans_storage_to_exit
        self.net_rt_exit_to_storage_name = model_factory.net_trans_exit_to_storage
        self.net_rt_entry_to_exit = model_factory.net_trans_entry_to_exit
        self.net_rt_entry_to_storage_name = model_factory.net_trans_entry_to_storage

        # entry --------------------------------------------------------------
        self.net_assembled_goods_name = model_factory.net_place_assembled_goods
        self.net_transport_name = model_factory.net_place_transport
        self.net_upper_goods_name = model_factory.net_place_goods_upper
        self.net_lower_goods_name = model_factory.net_place_goods_lower

        self.net_entry_to_rt_name = model_factory.net_trans_entry_to_rotary_table
        self.net_prepare_goods_name = model_factory.net_trans_prepare_goods

        # exit ---------------------------------------------------------------
        self.net_assembly_station_name = model_factory.net_place_assembly_station
        self.net_rivets_name = model_factory.net_place_rivets
        self.net_exit_name = model_factory.net_place_exit

        self.net_assemble_name = model_factory.net_trans_assemble
        self.net_rt_to_exit_name = model_factory.net_trans_rotary_table_to_exit
        self.net_exit_to_rt_name = model_factory.net_trans_exit_to_rotary_table
        self.net_to_exit_name = model_factory.net_trans_to_exit

        # storage -------------------------------------------------------------
        self.net_rt_to_storage_name = model_factory.net_trans_rotary_table_to_storage
        self.net_storage_name = model_factory.net_place_storage

        self.exit_correct_counter = 0
        self.exit_incorrect_counter = 0
        self.storage_correct_counter = 0
        self.storage_incorrect_counter = 0

        self.style = Style()
        self.position_rotary_table(rt_exit_x=460, rt_exit_y=210, rt_width=300, rt_height=200)
        self.position_entry(rect_entry_to_rt_x=610, rect_entry_to_rt_y=495, entry_width=380, entry_height=200)
        self.position_exit(assembly_x=260, assembly_y=210, exit_width=380, exit_height=165)
        self.position_storage(storage_x=990, storage_y=210, storage_width=120, storage_height=100)
        self.init_ui()

        root.geometry(str(self.window_width) + "x" + str(self.window_height))
        root.configure(background='white')
        root.resizable(0, 0)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_loop(self):
        self.update_clock()

        self.colour_transitions()
        self.colour_places()
        self.update_displayed_tokens()

    # UI Init functions ------------------------------------------------------------------------------------------------

    def init_ui(self):
        self.master.title("Model factory")

        frame = tk.Frame(self, relief=RAISED, borderwidth=1, bg='white')
        frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)

        self.create_buttons()

        self.canvas = tk.Canvas(frame, width=self.canvas_width, height=self.canvas_height, bg='white',
                                highlightthickness=0)
        self.canvas.pack(side=LEFT, padx=20, pady=10)

        self.create_places()
        self.create_transitions()
        self.create_arcs()
        self.create_labels()
        self.create_tokens()
        self.create_text_fields()

    def position_rotary_table(self, rt_exit_x, rt_exit_y, rt_width, rt_height):
        self.circ_rt_exit_x = rt_exit_x
        self.circ_rt_exit_y = rt_exit_y

        self.circ_rt_storage_x = rt_exit_x + rt_width
        self.circ_rt_storage_y = self.circ_rt_exit_y

        self.circ_rt_entry_x = get_value_between_coordinates(self.circ_rt_exit_x, self.circ_rt_storage_x)
        self.circ_rt_entry_y = rt_exit_y + rt_height

        self.circ_rt_resource_x = self.circ_rt_entry_x
        self.circ_rt_resource_y = get_value_between_coordinates(self.circ_rt_exit_y,
                                                                self.circ_rt_entry_y,
                                                                factor=3 / 8)

        self.rect_storage_to_exit_x = get_value_between_coordinates(self.circ_rt_exit_x, self.circ_rt_storage_x)
        self.rect_storage_to_exit_y = self.circ_rt_storage_y - (rt_height / 3)

        self.rect_exit_to_storage_x = get_value_between_coordinates(self.circ_rt_exit_x, self.circ_rt_storage_x)
        self.rect_exit_to_storage_y = self.circ_rt_storage_y

        self.rect_entry_to_exit_x = get_value_between_coordinates(self.circ_rt_exit_x, self.circ_rt_entry_x,
                                                                  factor=1 / 4)
        self.rect_entry_to_exit_y = get_value_between_coordinates(self.circ_rt_exit_y, self.circ_rt_entry_y,
                                                                  factor=2 / 3)

        self.rect_entry_to_storage_x = get_value_between_coordinates(self.circ_rt_storage_x, self.circ_rt_entry_x,
                                                                     factor=1 / 4)
        self.rect_entry_to_storage_y = get_value_between_coordinates(self.circ_rt_storage_y, self.circ_rt_entry_y,
                                                                     factor=2 / 3)

    def position_entry(self, rect_entry_to_rt_x, rect_entry_to_rt_y, entry_width, entry_height):
        self.rect_entry_to_rt_x = rect_entry_to_rt_x
        self.rect_entry_to_rt_y = rect_entry_to_rt_y

        self.circ_entry_assembled_goods_x = self.rect_entry_to_rt_x + entry_width / 3
        self.circ_entry_assembled_goods_y = rect_entry_to_rt_y

        self.rect_prepare_goods_x = self.circ_entry_assembled_goods_x + entry_width / 3
        self.rect_prepare_goods_y = self.circ_entry_assembled_goods_y

        self.circ_entry_goods_lower_x = self.rect_prepare_goods_x + entry_width / 3
        self.circ_entry_goods_lower_y = self.rect_prepare_goods_y

        self.circ_entry_goods_upper_x = self.circ_entry_goods_lower_x
        self.circ_entry_goods_upper_y = self.circ_entry_goods_lower_y + entry_height / 2

        self.circ_entry_transport_x = self.circ_entry_goods_lower_x
        self.circ_entry_transport_y = self.circ_entry_goods_lower_y - entry_height / 2

    def position_exit(self, assembly_x, assembly_y, exit_width, exit_height):
        self.circ_assembly_station_x = assembly_x
        self.circ_assembly_station_y = assembly_y

        self.circ_exit_x = self.circ_assembly_station_x - exit_width / 4 * 2
        self.circ_exit_y = self.circ_assembly_station_y

        self.circ_rivets_x = self.circ_assembly_station_x
        self.circ_rivets_y = self.circ_assembly_station_y - exit_height / 2 * 2

        self.rect_rt_to_exit_x = self.circ_assembly_station_x + exit_width / 4 * 1
        self.rect_rt_to_exit_y = self.circ_assembly_station_y - exit_height / 2 * 1

        self.rect_exit_to_rt_x = self.circ_assembly_station_x + exit_width / 4 * 1
        self.rect_exit_to_rt_y = self.circ_assembly_station_y

        self.rect_assemble_x = self.circ_assembly_station_x
        self.rect_assemble_y = self.circ_assembly_station_y - exit_height / 2 * 1

        self.rect_to_exit_x = self.circ_assembly_station_x - exit_width / 4 * 1
        self.rect_to_exit_y = self.circ_assembly_station_y

    def position_storage(self, storage_x, storage_y, storage_width, storage_height):
        self.circ_storage_x = storage_x
        self.circ_storage_y = storage_y

        self.rect_rt_to_storage_x = storage_x - storage_width / 1
        self.rect_rt_to_storage_y = storage_y

    def create_buttons(self):
        transition_button_width = 0
        button_padding_x = 1
        button_padding_y = 5

        top_frame = Frame()
        top_frame.pack(fill=BOTH)

        bottom_frame = Frame()
        bottom_frame.pack(fill=BOTH)

        close_button = Button(bottom_frame, text="Close", command=self.on_closing)
        close_button.pack(side=RIGHT, padx=button_padding_x, pady=button_padding_y)

        assemble_goods_button = Button(top_frame, text=self.trans_name_assemble_goods,
                                       command=self.on_prepare_goods_button,
                                       width=transition_button_width)
        assemble_goods_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        goods_to_rt_button = Button(top_frame, text=self.trans_name_goods_to_rt, command=self.on_entry_to_rt_button,
                                    width=transition_button_width)
        goods_to_rt_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        rt_entry_to_rt_exit_button = Button(top_frame, text=self.trans_name_rt_entry_to_rt_exit,
                                            command=self.on_rt_entry_to_exit_button,
                                            width=transition_button_width)
        rt_entry_to_rt_exit_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        rt_entry_to_rt_storage_button = Button(top_frame, text=self.trans_name_rt_entry_to_rt_storage,
                                               command=self.on_rt_entry_to_storage_button,
                                               width=transition_button_width)
        rt_entry_to_rt_storage_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        rt_storage_to_rt_exit_button = Button(top_frame, text=self.trans_name_rt_storage_to_rt_exit,
                                              command=self.on_rt_storage_to_exit_button,
                                              width=transition_button_width)
        rt_storage_to_rt_exit_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        rt_exit_to_rt_storage_button = Button(bottom_frame, text=self.trans_name_rt_exit_to_rt_storage,
                                              command=self.on_rt_exit_to_storage_button,
                                              width=transition_button_width)
        rt_exit_to_rt_storage_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        rt_exit_to_assembly_button = Button(bottom_frame, text=self.trans_name_rt_exit_to_assembly,
                                            command=self.on_rt_to_exit_button,
                                            width=transition_button_width)
        rt_exit_to_assembly_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        assembly_to_rt_exit_button = Button(bottom_frame, text=self.trans_name_assembly_to_rt_exit,
                                            command=self.on_exit_to_rt_button,
                                            width=transition_button_width)
        assembly_to_rt_exit_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        install_rivets_button = Button(bottom_frame, text=self.trans_name_install_rivets,
                                       command=self.on_assemble_button,
                                       width=transition_button_width)
        install_rivets_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        product_to_exit_button = Button(bottom_frame, text=self.trans_name_product_to_exit,
                                        command=self.on_to_exit_button,
                                        width=transition_button_width)
        product_to_exit_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        product_to_storage_button = Button(bottom_frame, text=self.trans_name_product_to_storage,
                                           command=self.on_rt_to_storage_button,
                                           width=transition_button_width)
        product_to_storage_button.pack(side=LEFT, padx=button_padding_x, pady=button_padding_y)

        save_stats_button = Button(bottom_frame, text="Save Stats", command=self.on_save_stats_button)
        save_stats_button.pack(side=RIGHT, padx=button_padding_x, pady=button_padding_y)

        save_q_button = Button(bottom_frame, text="Save Q", command=self.on_save_q_button)
        save_q_button.pack(side=RIGHT, padx=button_padding_x, pady=button_padding_y)

        reset_button = Button(top_frame, text="RESET", command=self.on_reset_button)
        reset_button.pack(side=RIGHT, padx=button_padding_x, pady=button_padding_y)

        self.speed_button = Button(top_frame, text="Faster", command=self.on_speed_button)
        self.speed_button.pack(side=RIGHT, padx=button_padding_x, pady=button_padding_y)

        self.run_button = Button(top_frame, text="RUN", command=self.on_run_button)
        self.run_button.pack(side=RIGHT, padx=button_padding_x, pady=button_padding_y)

    def create_places(self):
        self.place_rt_exit = self.create_circle(self.circ_rt_exit_x, self.circ_rt_exit_y, self.circle_radius)
        self.place_rt_storage = self.create_circle(self.circ_rt_storage_x, self.circ_rt_storage_y, self.circle_radius)
        self.place_rt_ressource = self.create_circle(self.circ_rt_resource_x, self.circ_rt_resource_y,
                                                     self.circle_radius)
        self.place_rt_entry = self.create_circle(self.circ_rt_entry_x, self.circ_rt_entry_y, self.circle_radius)

        self.place_entry_assembled_goods = self.create_circle(self.circ_entry_assembled_goods_x,
                                                              self.circ_entry_assembled_goods_y, self.circle_radius)
        self.place_entry_lower_goods = self.create_circle(self.circ_entry_goods_lower_x, self.circ_entry_goods_lower_y,
                                                          self.circle_radius)
        self.place_entry_upper_goods = self.create_circle(self.circ_entry_goods_upper_x, self.circ_entry_goods_upper_y,
                                                          self.circle_radius)
        self.place_entry_transport = self.create_circle(self.circ_entry_transport_x, self.circ_entry_transport_y,
                                                        self.circle_radius)

        self.place_assembly_station = self.create_circle(self.circ_assembly_station_x, self.circ_assembly_station_y,
                                                         self.circle_radius)
        self.place_rivets = self.create_circle(self.circ_rivets_x, self.circ_rivets_y, self.circle_radius)
        self.place_exit = self.create_circle(self.circ_exit_x, self.circ_exit_y, self.circle_radius)

        self.place_storage = self.create_circle(self.circ_storage_x, self.circ_storage_y, self.circle_radius)

        self.circle_place_dict = {self.net_rt_exit_name: self.place_rt_exit,
                                  self.net_rt_storage_name: self.place_rt_storage,
                                  self.net_rt_resource_name: self.place_rt_ressource,
                                  self.net_rt_entry_name: self.place_rt_entry,
                                  self.net_assembled_goods_name: self.place_entry_assembled_goods,
                                  self.net_lower_goods_name: self.place_entry_lower_goods,
                                  self.net_upper_goods_name: self.place_entry_upper_goods,
                                  self.net_transport_name: self.place_entry_transport,
                                  self.net_assembly_station_name: self.place_assembly_station,
                                  self.net_rivets_name: self.place_rivets,
                                  self.net_exit_name: self.place_exit,
                                  self.net_storage_name: self.place_storage}

    def create_transitions(self):
        self.storage_to_exit = self.create_rectangle(self.rect_storage_to_exit_x, self.rect_storage_to_exit_y,
                                                     self.rect_width,
                                                     self.rect_height)
        self.exit_to_storage = self.create_rectangle(self.rect_exit_to_storage_x, self.rect_exit_to_storage_y,
                                                     self.rect_width,
                                                     self.rect_height)
        self.entry_to_exit = self.create_rectangle(self.rect_entry_to_exit_x, self.rect_entry_to_exit_y,
                                                   self.rect_width,
                                                   self.rect_height)
        self.entry_to_storage = self.create_rectangle(self.rect_entry_to_storage_x, self.rect_entry_to_storage_y,
                                                      self.rect_width,
                                                      self.rect_height)

        # entry
        self.entry_to_rt = self.create_rectangle(self.rect_entry_to_rt_x, self.rect_entry_to_rt_y,
                                                 self.rect_width,
                                                 self.rect_height)

        self.prepare_goods = self.create_rectangle(self.rect_prepare_goods_x, self.rect_prepare_goods_y,
                                                   self.rect_width,
                                                   self.rect_height)

        # exit
        self.assemble = self.create_rectangle(self.rect_assemble_x, self.rect_assemble_y, self.rect_width,
                                              self.rect_height)

        self.rt_to_exit = self.create_rectangle(self.rect_rt_to_exit_x, self.rect_rt_to_exit_y, self.rect_width,
                                                self.rect_height)

        self.exit_to_rt = self.create_rectangle(self.rect_exit_to_rt_x, self.rect_exit_to_rt_y, self.rect_width,
                                                self.rect_height)

        self.to_exit = self.create_rectangle(self.rect_to_exit_x, self.rect_to_exit_y, self.rect_width, self.rect_height)

        # storage
        self.rt_to_storage = self.create_rectangle(self.rect_rt_to_storage_x, self.rect_rt_to_storage_y, self.rect_width,
                                                   self.rect_height)

        self.rect_trans_dict = {self.net_rt_storage_to_exit_name: self.storage_to_exit,
                                self.net_rt_exit_to_storage_name: self.exit_to_storage,
                                self.net_rt_entry_to_exit: self.entry_to_exit,
                                self.net_rt_entry_to_storage_name: self.entry_to_storage,
                                self.net_entry_to_rt_name: self.entry_to_rt,
                                self.net_prepare_goods_name: self.prepare_goods,
                                self.net_assemble_name: self.assemble,
                                self.net_rt_to_exit_name: self.rt_to_exit,
                                self.net_exit_to_rt_name: self.exit_to_rt,
                                self.net_to_exit_name: self.to_exit,
                                self.net_rt_to_storage_name: self.rt_to_storage}

    def create_arcs(self):
        # RotaryTable Arcs
        self.create_arc_between_place_and_trans(self.circ_rt_exit_x, self.circ_rt_exit_y,
                                                self.rect_storage_to_exit_x, self.rect_storage_to_exit_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_rt_storage_x, self.circ_rt_storage_y,
                                                self.rect_storage_to_exit_x, self.rect_storage_to_exit_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_rt_exit_x, self.circ_rt_exit_y,
                                                self.rect_exit_to_storage_x, self.rect_exit_to_storage_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_rt_storage_x, self.circ_rt_storage_y,
                                                self.rect_exit_to_storage_x, self.rect_exit_to_storage_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_rt_entry_x, self.circ_rt_entry_y,
                                                self.rect_entry_to_exit_x, self.rect_entry_to_exit_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_rt_exit_x, self.circ_rt_exit_y,
                                                self.rect_entry_to_exit_x, self.rect_entry_to_exit_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_rt_entry_x, self.circ_rt_entry_y,
                                                self.rect_entry_to_storage_x, self.rect_entry_to_storage_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_rt_storage_x, self.circ_rt_storage_y,
                                                self.rect_entry_to_storage_x, self.rect_entry_to_storage_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_rt_resource_x, self.circ_rt_resource_y,
                                                self.rect_exit_to_storage_x, self.rect_exit_to_storage_y,
                                                arrow=tk.BOTH)
        self.create_arc_between_place_and_trans(self.circ_rt_resource_x, self.circ_rt_resource_y,
                                                self.rect_entry_to_exit_x, self.rect_entry_to_exit_y,
                                                arrow=tk.BOTH)
        self.create_arc_between_place_and_trans(self.circ_rt_resource_x, self.circ_rt_resource_y,
                                                self.rect_entry_to_storage_x, self.rect_entry_to_storage_y,
                                                arrow=tk.BOTH)
        self.create_curvy_arc_between_place_and_trans(self.circ_rt_resource_x, self.circ_rt_resource_y,
                                                      self.rect_storage_to_exit_x, self.rect_storage_to_exit_y,
                                                      arrow=tk.BOTH, curviness=80, curvy_dir=Position.LEFT)

        # Entry Arcs
        self.create_arc_between_place_and_trans(self.circ_rt_entry_x, self.circ_rt_entry_y,
                                                self.rect_entry_to_rt_x, self.rect_entry_to_rt_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_entry_assembled_goods_x, self.circ_entry_assembled_goods_y,
                                                self.rect_entry_to_rt_x, self.rect_entry_to_rt_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_entry_assembled_goods_x, self.circ_entry_assembled_goods_y,
                                                self.rect_prepare_goods_x, self.rect_prepare_goods_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_entry_transport_x, self.circ_entry_transport_y,
                                                self.rect_prepare_goods_x, self.rect_prepare_goods_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_entry_goods_upper_x, self.circ_entry_goods_upper_y,
                                                self.rect_prepare_goods_x, self.rect_prepare_goods_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_entry_goods_lower_x, self.circ_entry_goods_lower_y,
                                                self.rect_prepare_goods_x, self.rect_prepare_goods_y,
                                                arrow=tk.LAST)

        # Exit arcs
        self.create_arc_between_place_and_trans(self.circ_rt_exit_x, self.circ_rt_exit_y,
                                                self.rect_rt_to_exit_x, self.rect_rt_to_exit_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_rt_exit_x, self.circ_rt_exit_y,
                                                self.rect_exit_to_rt_x, self.rect_exit_to_rt_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_assembly_station_x, self.circ_assembly_station_y,
                                                self.rect_rt_to_exit_x, self.rect_rt_to_exit_y,
                                                arrow=tk.FIRST)
        self.create_arc_between_place_and_trans(self.circ_assembly_station_x, self.circ_assembly_station_y,
                                                self.rect_exit_to_rt_x, self.rect_exit_to_rt_y,
                                                arrow=tk.LAST)

        self.create_arc_between_place_and_trans(self.circ_assembly_station_x, self.circ_assembly_station_y,
                                                self.rect_assemble_x, self.rect_assemble_y,
                                                arrow=tk.BOTH)
        self.create_arc_between_place_and_trans(self.circ_rivets_x, self.circ_rivets_y,
                                                self.rect_assemble_x, self.rect_assemble_y,
                                                arrow=tk.LAST)

        self.create_arc_between_place_and_trans(self.circ_assembly_station_x, self.circ_assembly_station_y,
                                                self.rect_to_exit_x, self.rect_to_exit_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_exit_x, self.circ_exit_y,
                                                self.rect_to_exit_x, self.rect_to_exit_y,
                                                arrow=tk.FIRST)

        # storage arcs
        self.create_arc_between_place_and_trans(self.circ_rt_storage_x, self.circ_rt_storage_y,
                                                self.rect_rt_to_storage_x, self.rect_rt_to_storage_y,
                                                arrow=tk.LAST)
        self.create_arc_between_place_and_trans(self.circ_storage_x, self.circ_storage_y,
                                                self.rect_rt_to_storage_x, self.rect_rt_to_storage_y,
                                                arrow=tk.FIRST)

    def create_labels(self):
        # RT Labels
        self.create_place_label(self.circ_rt_exit_x, self.circ_rt_exit_y, position=Position.BOTTOM,
                                text=self.place_name_rt_exit)
        self.create_place_label(self.circ_rt_storage_x, self.circ_rt_storage_y, position=Position.BOTTOM,
                                text=self.place_name_rt_storage)
        self.create_place_label(self.circ_rt_entry_x, self.circ_rt_entry_y, position=Position.TOP,
                                text=self.place_name_rt_entry)
        self.create_place_label(self.circ_rt_resource_x, self.circ_rt_resource_y, position=Position.BOTTOM,
                                text=self.place_name_rt_ready)

        self.create_trans_label(self.rect_storage_to_exit_x, self.rect_storage_to_exit_y, Position.TOP,
                                text=self.trans_name_rt_storage_to_rt_exit)
        self.create_trans_label(self.rect_exit_to_storage_x, self.rect_exit_to_storage_y, Position.TOP,
                                text=self.trans_name_rt_exit_to_rt_storage)
        self.create_trans_label(self.rect_entry_to_exit_x, self.rect_entry_to_exit_y, Position.BOTTOM,
                                text=self.trans_name_rt_entry_to_rt_exit)
        self.create_trans_label(self.rect_entry_to_storage_x, self.rect_entry_to_storage_y, Position.BOTTOM,
                                text=self.trans_name_rt_entry_to_rt_storage)

        # Entry Labels
        self.create_place_label(self.circ_entry_assembled_goods_x, self.circ_entry_assembled_goods_y,
                                position=Position.BOTTOM, text=self.place_name_assembled_goods)
        self.create_place_label(self.circ_entry_transport_x, self.circ_entry_transport_y, position=Position.TOP,
                                text=self.place_name_entry_transport)
        self.create_place_label(self.circ_entry_goods_upper_x, self.circ_entry_goods_upper_y, position=Position.TOP,
                                text=self.place_name_entry_upper_goods)
        self.create_place_label(self.circ_entry_goods_lower_x, self.circ_entry_goods_lower_y, position=Position.TOP,
                                text=self.place_name_entry_lower_goods)

        self.create_trans_label(self.rect_prepare_goods_x, self.rect_prepare_goods_y, Position.TOP,
                                text=self.trans_name_assemble_goods)
        self.create_trans_label(self.rect_entry_to_rt_x, self.rect_entry_to_rt_y, Position.TOP,
                                text=self.trans_name_goods_to_rt)

        # Exit Labels
        self.create_place_label(self.circ_assembly_station_x, self.circ_assembly_station_y, position=Position.BOTTOM,
                                text=self.place_name_assembly_station)
        self.create_place_label(self.circ_rivets_x, self.circ_rivets_y, position=Position.TOP,
                                text=self.place_name_rivets)
        self.create_place_label(self.circ_exit_x, self.circ_exit_y, position=Position.TOP,
                                text=self.place_name_exit)

        self.create_trans_label(self.rect_rt_to_exit_x, self.rect_rt_to_exit_y, Position.TOP,
                                text=self.trans_name_rt_exit_to_assembly)
        self.create_trans_label(self.rect_exit_to_rt_x, self.rect_exit_to_rt_y, Position.TOP,
                                text=self.trans_name_assembly_to_rt_exit)
        self.create_trans_label(self.rect_assemble_x, self.rect_assemble_y, Position.BOTTOM,
                                text=self.trans_name_install_rivets)
        self.create_trans_label(self.rect_to_exit_x, self.rect_to_exit_y, Position.TOP,
                                text=self.trans_name_product_to_exit)

        # storage Labels
        self.create_place_label(self.circ_storage_x, self.circ_storage_y, position=Position.TOP,
                                text=self.place_name_storage)
        self.create_trans_label(self.rect_rt_to_storage_x, self.rect_rt_to_storage_y, Position.TOP,
                                text=self.trans_name_product_to_storage)

    def create_tokens(self):
        # RT Tokens
        self.rt_exit_tokens_id = self.canvas.create_text(self.circ_rt_exit_x, self.circ_rt_exit_y,
                                                         text=str(
                                                           self.model_factory.get_place_tokens(self.net_rt_exit_name)))
        self.rt_storage_tokens_id = self.canvas.create_text(self.circ_rt_storage_x, self.circ_rt_storage_y
                                                            , text=str(self.model_factory.get_place_tokens
                                                                     (self.net_rt_storage_name)))
        self.rotary_table_ressource_tokens_id = self.canvas.create_text(self.circ_rt_resource_x, self.circ_rt_resource_y,
                                                                        text=str(self.model_factory.get_place_tokens(
                                                                         self.net_rt_resource_name)))
        self.rt_entry_tokens_id = self.canvas.create_text(self.circ_rt_entry_x, self.circ_rt_entry_y,
                                                          text=str(
                                                            self.model_factory.get_place_tokens(
                                                                self.net_rt_entry_name)))

        # Entry Tokens
        self.assembled_goods_tokens_id = self.canvas.create_text(self.circ_entry_assembled_goods_x,
                                                                 self.circ_entry_assembled_goods_y,
                                                                 text=str(self.model_factory.get_place_tokens
                                                                        (self.net_assembled_goods_name)))
        self.transport_tokens_id = self.canvas.create_text(self.circ_entry_transport_x, self.circ_entry_transport_y,
                                                           text=str(self.model_factory.get_place_tokens(
                                                              self.net_transport_name)))
        self.upper_goods_tokens_id = self.canvas.create_text(self.circ_entry_goods_upper_x, self.circ_entry_goods_upper_y,
                                                             text=str(self.model_factory.get_place_tokens(
                                                               self.net_upper_goods_name)))
        self.lower_goods_tokens_id = self.canvas.create_text(self.circ_entry_goods_lower_x, self.circ_entry_goods_lower_y,
                                                             text=str(self.model_factory.get_place_tokens(
                                                               self.net_lower_goods_name)))

        # Exit Tokens
        self.assembly_station_tokens_id = self.canvas.create_text(self.circ_assembly_station_x,
                                                                  self.circ_assembly_station_y,
                                                                  text=str(self.model_factory.get_place_tokens(
                                                                    self.net_assembly_station_name)))
        self.rivet_tokens_id = self.canvas.create_text(self.circ_rivets_x, self.circ_rivets_y,
                                                       text=str(self.model_factory.get_place_tokens(
                                                          self.net_rivets_name)))
        self.exit_tokens_id = self.canvas.create_text(self.circ_exit_x, self.circ_exit_y,
                                                      text=str(self.model_factory.get_place_tokens(
                                                         self.net_exit_name)))

        # Storage Tokens
        self.storage_tokens_id = self.canvas.create_text(self.circ_storage_x, self.circ_storage_y,
                                                         text=str(self.model_factory.get_place_tokens(
                                                            self.net_storage_name)))

    def create_text_fields(self):
        self.clock_id = self.canvas.create_text(self.canvas_width - 50, 10, text="Clock: " + str(0.0))

    def create_circle(self, x, y, r):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1, outline='black')

    def create_rectangle(self, x, y, width, height):  # center coordinates, radius
        x0 = x - width / 2
        y0 = y - height / 2
        x1 = x0 + width
        y1 = y0 + height
        return self.canvas.create_rectangle(x0, y0, x1, y1)

    def create_arc_between_place_and_trans(self, place_x, place_y, trans_x, trans_y, arrow=tk.LAST):
        if abs(place_x - trans_x) > abs(place_y - trans_y):
            if place_x > trans_x:
                self.canvas.create_line(place_x - self.circle_radius,
                                        place_y,
                                        trans_x + self.rect_width / 2,
                                        trans_y, arrow=arrow)
            elif place_x < trans_x:
                self.canvas.create_line(place_x + self.circle_radius,
                                        place_y,
                                        trans_x - self.rect_width / 2,
                                        trans_y, arrow=arrow)
        else:
            if place_y > trans_y:
                self.canvas.create_line(place_x,
                                        place_y - self.circle_radius,
                                        trans_x,
                                        trans_y + self.rect_height / 2, arrow=arrow)
            else:
                self.canvas.create_line(place_x,
                                        place_y + self.circle_radius,
                                        trans_x,
                                        trans_y - self.rect_height / 2, arrow=arrow)

    def create_curvy_arc_between_place_and_trans(self, place_x, place_y, trans_x, trans_y, arrow=tk.LAST,
                                                 curvy_dir=Position.LEFT, curviness=60):
        """
        :param curvy_dir:  direction of curvature, if set to Position.LEFT will curve left or up depending on position
            of place and transition, if set to Position.RIGHT will curve right or down
        :param curviness: factor as percent value defining the curviness with respect to the arc length
        :return: none, modifies self
        """
        factor = curviness / 100

        # horizontal arcs
        if abs(place_x - trans_x) > abs(place_y - trans_y):
            if place_x > trans_x:
                halfway_x = ((place_x - self.circle_radius) + (trans_x + self.rect_width / 2)) / 2
                halfway_y = (place_y + trans_y) / 2
                if curvy_dir == Position.LEFT:
                    self.canvas.create_line(place_x - self.circle_radius, place_y,
                                            halfway_x + (place_y - halfway_y) * factor,
                                            halfway_y - (place_x - halfway_x) * factor,
                                            trans_x + self.rect_width / 2, trans_y,
                                            arrow=arrow, smooth="true")
                else:
                    self.canvas.create_line(place_x - self.circle_radius, place_y,
                                            halfway_x - (place_y - halfway_y) * factor,
                                            halfway_y + (place_x - halfway_x) * factor,
                                            trans_x + self.rect_width / 2, trans_y,
                                            arrow=arrow, smooth="true")

            elif place_x < trans_x:
                halfway_x = ((place_x + self.circle_radius) + (trans_x - self.rect_width / 2)) / 2
                halfway_y = (place_y + trans_y) / 2
                if curvy_dir == Position.LEFT:
                    self.canvas.create_line(place_x + self.circle_radius, place_y,
                                            halfway_x - (place_y - halfway_y) * factor,
                                            halfway_y + (place_x - halfway_x) * factor,
                                            trans_x - self.rect_width / 2, trans_y,
                                            arrow=arrow, smooth="true")
                else:
                    self.canvas.create_line(place_x + self.circle_radius, place_y,
                                            halfway_x + (place_y - halfway_y) * factor,
                                            halfway_y - (place_x - halfway_x) * factor,
                                            trans_x - self.rect_width / 2, trans_y,
                                            arrow=arrow, smooth="true")
        # vertical arcs
        else:
            if place_y > trans_y:
                halfway_x = (place_x + trans_x) / 2
                halfway_y = ((place_y - self.circle_radius) + (trans_y + self.rect_height / 2)) / 2
                if curvy_dir == Position.LEFT:
                    self.canvas.create_line(place_x, place_y - self.circle_radius,
                                            halfway_x - (place_y - halfway_y) * factor,
                                            halfway_y - (place_x - halfway_x) * factor,
                                            trans_x, trans_y + self.rect_height / 2,
                                            arrow=arrow, smooth="true")
                else:
                    self.canvas.create_line(place_x, place_y - self.circle_radius,
                                            halfway_x + (place_y - halfway_y) * factor,
                                            halfway_y + (place_x - halfway_x) * factor,
                                            trans_x, trans_y + self.rect_height / 2,
                                            arrow=arrow, smooth="true")
            else:
                halfway_x = (place_x + trans_x) / 2
                halfway_y = ((place_y + self.circle_radius) + (trans_y - self.rect_height / 2)) / 2
                if curvy_dir == Position.LEFT:
                    self.canvas.create_line(place_x, place_y + self.circle_radius,
                                            halfway_x + (place_y - halfway_y) * factor,
                                            halfway_y - (place_x - halfway_x) * factor,
                                            trans_x, trans_y - self.rect_height / 2,
                                            arrow=arrow, smooth="true")
                else:
                    self.canvas.create_line(place_x, place_y + self.circle_radius,
                                            halfway_x - (place_y - halfway_y) * factor,
                                            halfway_y + (place_x - halfway_x) * factor,
                                            trans_x, trans_y - self.rect_height / 2,
                                            arrow=arrow, smooth="true")

    def create_place_label(self, circ_x, circ_y, position, text):
        x = circ_x
        y = circ_y
        padding = 10
        if position == Position.TOP:
            y = circ_y - self.circle_radius - padding
        elif position == Position.BOTTOM:
            y = circ_y + self.circle_radius + padding
        elif position == Position.RIGHT:
            x = circ_x + self.circle_radius + padding
        elif position == Position.LEFT:
            x = circ_x - self.circle_radius - padding
        self.canvas.create_text(x, y, text=text)

    def create_trans_label(self, rect_x, rect_y, position, text):
        x = rect_x
        y = rect_y
        padding = 12
        if position == Position.TOP:
            y = rect_y - self.rect_height / 2 - padding
        elif position == Position.BOTTOM:
            y = rect_y + self.rect_height / 2 + padding
        elif position == Position.RIGHT:
            x = rect_x + self.rect_width / 2 + padding
        elif position == Position.LEFT:
            x = rect_x - self.rect_width / 2 - padding
        self.canvas.create_text(x, y, text=text)

    # Update functions -------------------------------------------------------------------------------------------------

    def colour_transitions(self):
        for trans in self.model_factory.get_transitions():
            if self.model_factory.is_timed_transition_active(trans):
                self.canvas.itemconfig(self.rect_trans_dict[trans], fill=Colours.GREEN.value)
            else:
                self.canvas.itemconfig(self.rect_trans_dict[trans], fill=Colours.GREY.value)

    def colour_places(self):
        for place in self.model_factory.places:
            if self.model_factory.is_collision_detected_on_place(place):
                self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.RED.value)
            else:
                if self.model_factory.is_not_observed_place(place):
                    self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.VERY_LIGHT_GREY.value)
                elif not self.model_factory.is_storage_place(place) \
                        and not self.model_factory.is_resource_place(place) \
                        and len(self.model_factory.get_place_tokens(place).items()) > 0:
                    token = self.model_factory.get_place_tokens(place).items()[0]
                    if token == 1:
                        self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.LIGHT_BLUE.value)
                    elif token == 2:
                        self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.LIGHT_GREEN.value)
                    elif token == 3:
                        self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.DARK_BLUE.value)
                    elif token == 4:
                        self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.DARK_GREEN.value)
                else:
                    self.canvas.itemconfig(self.circle_place_dict[place], fill=Colours.VERY_LIGHT_GREY.value)

    def update_displayed_tokens(self):
        # RT Tokens
        self.canvas.itemconfig(self.rt_exit_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_rt_exit_name)))
        self.canvas.itemconfig(self.rt_storage_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_rt_storage_name)))
        self.canvas.itemconfig(self.rotary_table_ressource_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_rt_resource_name)))
        self.canvas.itemconfig(self.rt_entry_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_rt_entry_name)))

        # Entry Tokens
        self.canvas.itemconfig(self.assembled_goods_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_assembled_goods_name)))
        self.canvas.itemconfig(self.transport_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_transport_name)))
        self.canvas.itemconfig(self.upper_goods_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_upper_goods_name)))
        self.canvas.itemconfig(self.lower_goods_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_lower_goods_name)))

        # Exit Tokens
        self.canvas.itemconfig(self.assembly_station_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_assembly_station_name)))
        self.canvas.itemconfig(self.rivet_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_rivets_name)))
        self.canvas.itemconfig(self.exit_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_exit_name)))

        # Storage Tokens
        self.canvas.itemconfig(self.storage_tokens_id,
                               text=str(self.model_factory.get_place_tokens(self.net_storage_name)))

    def update_clock(self):
        self.canvas.itemconfig(self.clock_id,
                               text="Clock: " + str(round(self.model_factory.clock, 1)))

    # Button functions -------------------------------------------------------------------------------------------------

    def on_rt_storage_to_exit_button(self):
        self.model_factory.fire_transition(self.net_rt_storage_to_exit_name)
        self.update_displayed_tokens()

    def on_rt_exit_to_storage_button(self):
        self.model_factory.fire_transition(self.net_rt_exit_to_storage_name)
        self.update_displayed_tokens()

    def on_rt_entry_to_exit_button(self):
        self.model_factory.fire_transition(self.net_rt_entry_to_exit)
        self.update_displayed_tokens()

    def on_rt_entry_to_storage_button(self):
        self.model_factory.fire_transition(self.net_rt_entry_to_storage_name)
        self.update_displayed_tokens()

    def on_entry_to_rt_button(self):
        self.model_factory.fire_transition(self.net_entry_to_rt_name)
        self.update_displayed_tokens()

    def on_prepare_goods_button(self):
        self.model_factory.fire_transition(self.net_prepare_goods_name)
        self.update_displayed_tokens()

    def on_rt_to_exit_button(self):
        self.model_factory.fire_transition(self.net_rt_to_exit_name)
        self.update_displayed_tokens()

    def on_exit_to_rt_button(self):
        self.model_factory.fire_transition(self.net_exit_to_rt_name)
        self.update_displayed_tokens()

    def on_assemble_button(self):
        self.model_factory.fire_transition(self.net_assemble_name)
        self.update_displayed_tokens()

    def on_to_exit_button(self):
        self.model_factory.fire_transition(self.net_to_exit_name)
        self.update_displayed_tokens()

    def on_rt_to_storage_button(self):
        self.model_factory.fire_transition(self.net_rt_to_storage_name)
        self.update_displayed_tokens()

    def on_run_button(self):
        self.perform_q_learning = True

    def on_save_q_button(self):
        self.save_q = True

    def on_save_stats_button(self):
        self.save_stats = True

    def on_reset_button(self):
        self.reset = True

    def on_speed_button(self):
        if self.speed == SimulationSpeed.SLOW:
            self.speed = SimulationSpeed.FAST
            self.speed_button.config(text="Slower")
        elif self.speed == SimulationSpeed.FAST:
            self.speed = SimulationSpeed.SLOW
            self.speed_button.config(text="Faster")

    def on_closing(self):
        self.master.destroy()
