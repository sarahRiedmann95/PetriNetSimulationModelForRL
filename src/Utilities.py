def handle_run_button(gui):
    if gui.perform_q_learning:
        gui.popup()
        gui.perform_q_learning = False


def handle_reset_button(gui, net):
    if gui.reset:
        net.reset()
        gui.reset = False


def handle_save_q_button(gui):
    if gui.save_q:
        gui.popup()
        gui.save_q = False


def handle_save_stats_button(gui):
    if gui.save_stats:
        gui.popup()
        gui.save_stats = False


def handle_simulation_speed(gui, net):
    net.time_step()
    gui.update_loop()
