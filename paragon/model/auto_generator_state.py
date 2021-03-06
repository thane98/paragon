import dataclasses


@dataclasses.dataclass
class AutoGeneratorState:
    main_state: object
    game_state: object
    generator: object
    type_metadata: dict
    field_metadata: dict
    typename: str
    labeled_widgets: dict = dataclasses.field(default_factory=dict)
