from app.repositories.comments import CommentsRepository


class MongoManager:

    def __init__(self):
        self.comments = CommentsRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass 