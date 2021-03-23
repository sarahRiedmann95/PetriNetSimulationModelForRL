import tkinter as tk

from src.PetriNetModel.ModelFactory import ModelFactory
from src.PetriNetModel.ModelFactoryGui import Gui

from src.Utilities import handle_reset_button, \
    handle_simulation_speed, handle_save_q_button, handle_save_stats_button, handle_run_button


def main():
    root = tk.Tk()
    model_factory = ModelFactory()

    gui = Gui(model_factory, root)

    def clock():
        handle_reset_button(gui, model_factory)

        handle_run_button(gui)
        handle_save_q_button(gui)
        handle_save_stats_button(gui)

        handle_simulation_speed(gui, model_factory)
        model_factory.fire_hidden_transitions()

        root.after(gui.speed.value, clock)

    clock()
    root.mainloop()


if __name__ == '__main__':
    main()
