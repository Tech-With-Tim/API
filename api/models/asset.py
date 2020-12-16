from postDB import Model, Column, types
import asyncpg


from typing import Optional


class Asset(Model):
    """
    Asset class used in the CDN and Badge class.

    Database Attributes:
        Attributes stored in the `guilds` table.

        :param int id:              The asset ID.
        :param str name:            The asset name to be displayed on web-dashboard.
        :param str url_path:        The CDN path this Asset should be mapped to
        :param str mimetype:
        :param str type:            The type of asset this is; Badge|Avatar|Image
        :param bytes data:           The binary data (the file itself)

    """
    id = Column(types.Serial, unique=True)
    name = Column(types.String(length=100), unique=True)
    url_path = Column(types.String, primary_key=True)
    mimetype = Column(types.String)
    type = Column(types.String)
    data = Column(types.Binary)

    @classmethod
    async def fetch(cls, **kwargs) -> Optional["Asset"]:
        """
        Fetch Asset based on any of the provided arguments.
        If `None` is given it will not be acquainted for in the query.

        :param int id:          Asset ID
        :param str name:        Asset name
        :param str url_path:    Asset url path
        :return:                Optional[Asset]
        """
        args, i = [], 1
        query = "SELECT * FROM {}".format(cls.__tablename__)

        for key in ("id", "name", "url_path"):
            value = kwargs.get(key)
            if value is None:
                continue

            query += f" {'WHERE' if i==1 else 'AND'} {key} = ${i}"
            args.append(value)

        record = await cls.pool.fetchrow(query, *args)
        if record is None:
            return None

        return cls(**record)

    async def create(self) -> bool:
        """
        Create the current instance, if not already created.
        Returns boolean describing if it was created or not.
        """
        query = """
        INSERT INTO assets (name, url_path, mimetype, type, data)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """
        try:
            record = await self.pool.fetchrow(query, self.name, self.url_path,
                                              self.mimetype, self.type, self.data.read())
        except asyncpg.UniqueViolationError:
            return False

        self.id = record["id"]
        return True

    async def save(self) -> bool:
        """
        Update the current instance with new attributes of the class.
        Returns boolean describing if updating was successful.
        """

        query = """
        UPDATE assets SET
            name = $2,
            url_path = $3,
            mimetype = $4,
            type = $5,
            data = $6
        WHERE id = $1
        """

        try:
            await self.pool.execute(query, self.id, self.name, self.url_path,
                                    self.mimetype, self.type, self.data)
        except asyncpg.UniqueViolationError:
            return False

        return True

    @classmethod
    async def delete(cls, asset_id: int) -> str:
        """
        Returns boolean describing if an asset was deleted or not.
        """
        return await cls.pool.execute("DELETE FROM assets WHERE id = $1", asset_id)
