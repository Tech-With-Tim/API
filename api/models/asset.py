from postDB import Model, Column, types
import asyncpg
import io


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
        :param :class:`io.BytesIO` data:            The binary data (the file itself)

    """
    id = Column(types.Serial, unique=True)
    name = Column(types.String(length=100), unique=True)
    url_path = Column(types.String, primary_key=True)
    mimetype = Column(types.String)
    type = Column(types.String)
    data = Column(types.Binary)

    @classmethod
    async def fetch(cls, name: str = None, url_path: str = None) -> Optional["Asset"]:
        """
        Fetch Asset based on any of the provided arguments.
        If `None` is given it will not be acquainted for in the query.

        :param name:        Asset name
        :param url_path:    Asset url path
        :return:            Optional[Asset]
        """

        if name is None and url_path is None:
            raise RuntimeWarning("Both name and url_path cannot be None.")

        args = []
        query = "SELECT * FROM assets"
        if name is not None:
            query += " WHERE name = $1"
            args.append(name)
            if url_path is not None:
                query += " AND url_path = $2"
                args.append(url_path)
        else:
            if url_path is not None:
                query += " WHERE url_path = $1"
                args.append(url_path)

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
