from sqlalchemy import select
from models import odkeyo_Monster, odkeyo_MonsterDetail
from clients import odkeyo_DnDClient


class odkeyo_MonsterProxyService:

    def __init__(self, client: odkeyo_DnDClient):
        self.client = client

    def list_monsters(self, session):
        existing = session.scalars(select(odkeyo_Monster)).all()
        if existing:
            return [{"index": m.index, "name": m.name} for m in existing]

        data = self.client.list_monsters()
        results = data.get("results", [])
        for item in results:
            idx = item.get("index"); name = item.get("name")
            if not idx or not name:
                continue
            if session.get(odkeyo_Monster, idx) is None:
                session.add(odkeyo_Monster(index=idx, name=name))
        session.flush()
        return [{"index": i.get("index"), "name": i.get("name")}
                for i in results if i.get("index") and i.get("name")]
    
    def get_monster(self, session, index: str):
        m = session.get(odkeyo_Monster, index)
        if m and m.detail:
            payload = dict(m.detail.data)
            payload["index"] = m.index
            payload["name"]  = m.name 
            return payload

        data = self.client.get_monster_by_index(index)
        name = data.get("name") or index

        if m is None:
            m = odkeyo_Monster(index=index, name=name)
            session.add(m)
            session.flush()

        d = session.get(odkeyo_MonsterDetail, index)
        if d is None:
            session.add(odkeyo_MonsterDetail(monster_index=index, data=data))
        else:
            d.data = data

        m.name = name
        session.flush()
        return data
