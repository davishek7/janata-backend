from beanie.odm.queries.find import FindMany


async def paginate(
    query: FindMany,
    page: int,
    size: int,
):
    total = await query.count()

    items = await query.skip((page - 1) * size).limit(size).to_list()

    return items, total
