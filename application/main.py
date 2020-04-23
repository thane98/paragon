import logging
logging.basicConfig(handlers=[logging.FileHandler('paragon.log', 'w', 'utf-8')], level=logging.DEBUG)
import sys
from PySide2.QtWidgets import QApplication
from core.state_machine import StateMachine
from services.service_locator import locator
from states.create_project_state import CreateProjectState
from states.find_project_state import FindProjectState
from states.init_state import InitState
from states.loading_state import LoadingState
from states.main_state import MainState
from states.transitions.create_project_to_loading import CreateProjectToLoadingTransition
from states.transitions.find_project_to_loading import FindProjectToLoadingTransition

logging.info("Paragon version: Alpha 11")
logging.info("Starting application...")
application = QApplication(sys.argv)
state_machine = StateMachine()
locator.register_static("StateMachine", state_machine)
state_machine.add_state(InitState())
state_machine.add_state(FindProjectState())
state_machine.add_state(CreateProjectState())
state_machine.add_state(LoadingState())
state_machine.add_state(MainState())
state_machine.add_transition(CreateProjectToLoadingTransition("CreateProject", "Loading"))
state_machine.add_transition(FindProjectToLoadingTransition("FindProject", "Loading"))
state_machine.transition("Init")
sys.exit(application.exec_())
