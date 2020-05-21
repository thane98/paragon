from model.conversation.source_position import SourcePosition


class TranspilerError(Exception):
    def __init__(self, source_position: SourcePosition, error_message: str):
        super().__init__(error_message)
        self.source_position = source_position
        self.error_message = error_message

    def __str__(self):
        return "Error at line %d, index %d: %s" % (
            self.source_position.line_number, self.source_position.character, self.error_message)
