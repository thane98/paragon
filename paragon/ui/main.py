import faulthandler
import logging
import sys

from paragon.model.configuration import Configuration
from paragon.ui.states.ui_main_state import UIMainState

faulthandler.enable(all_threads=True)

logging.basicConfig(
    handlers=[
        logging.FileHandler("paragon.log", "w", "utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
logging.info("Paragon Beta 1")

try:
    from PySide6.QtWidgets import QApplication
    from paragon.model.main_state import MainState
    from paragon.ui.states.find_project_state import FindProjectState
    from paragon.ui.states.init_state import InitState
    from paragon.ui.states.select_project_state import SelectProjectState
    from paragon.ui.states.load_state import LoadState
    from paragon.ui.states.state_machine import StateMachine
except:
    logging.exception("Failed to import a core module.")
    exit(1)

try:
    app = QApplication(sys.argv)

    config = Configuration.load("paragon.json")

    state_machine = StateMachine()
    state_machine.add_state(InitState())
    state_machine.add_state(FindProjectState())
    state_machine.add_state(SelectProjectState())
    state_machine.add_state(LoadState())
    state_machine.add_state(UIMainState())

    main_state = MainState(app=app, config=config, sm=state_machine)
    main_state.sm.transition("Init", main_state=main_state)

    app.exec()

    main_state.config.save("paragon.json")
except:
    logging.exception("Encountered a fatal error during startup or closing.")
    exit(1)

logging.info("Application exited.")
