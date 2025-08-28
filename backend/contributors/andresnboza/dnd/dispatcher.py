from handler.fetch_monster_handler import FetchMonsterHandler
from handler.fetch_monster_list_handler import FetchMonsterListHandler

class Dispatcher:
    def __init__(self):
        self.handlers = {
            "fetch_monster": FetchMonsterHandler(),
            "fetch_monster_list": FetchMonsterListHandler(),
        }

    def dispatch(self, call_type, request):
        handler = self.handlers.get(call_type)
        if handler:
            return handler.handle(request)
        else:
            return {"error": f"No handler for call type: {call_type}"}