from postDB import Model, Column, types


class Log(Model):
    """
    Database Attributes:
        Attributes stored in the `logs` table.

        :param int id:      The SERIAL ID of the Log.
        :param str type:    The type of log this is - ping|general|command.
        :param dict data:   The data connected to this log.
    """

    id = Column(types.Serial)
    type = Column(types.String)
    data = Column(types.JSON)

    @classmethod
    async def fetch(cls, id: int):
        query = """
        SELECT * FROM {}
        WHERE id = $1
        """.format(cls.tablename)
        
        record = await cls.pool.fetchrow(query, id)
        if record is None:
            return None

        return cls(**record)
