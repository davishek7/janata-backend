from pymongo.asynchronous.client_session import AsyncClientSession
from beanie.operators import Inc
from app.models import Counter


class CounterService:
    async def get_next_counter(self, key: str, session: AsyncClientSession) -> int:
        counter = await Counter.find_one(Counter.key == key, session=session)

        if not counter:
            counter = Counter(key=key, value=1)
            await counter.insert(session=session)
            return 1

        counter.value += 1
        await counter.save(session=session)

        return counter.value
