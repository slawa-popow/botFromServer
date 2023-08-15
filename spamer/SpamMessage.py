class SpamMessage:

    def __init__(self, message: str="", id=None) -> None:
        self._message = message
        self._id = id

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def message(self) -> str:
        return self._message
    
    @message.setter
    def message(self, value: str) -> None:
        self._message = str(value)

    def __str__(self) -> str:
        return self.message