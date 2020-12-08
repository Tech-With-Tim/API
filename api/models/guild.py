from postDB import Model, Column, types


import utils


class Guild(Model):
    """

    Database Attributes:
        Attributes stored in the `guilds` table.

        :param int id:                          The Guild ID.
        :param str name:                        The Guild name.
        :param int muted_role_id:               Muted role ID.
        :param int log_channel_id:              Log channel ID.
        :param int verification_channel_id:     Verification channel
    """

    id = Column(types.Integer(big=True), primary_key=True)
    name = Column(types.String(length=100))

    muted_role_id = Column(types.Integer(big=True), nullable=True)
    log_channel_id = Column(types.Integer(big=True), nullable=True)
    verification_channel_id = Column(types.Integer(big=True), nullable=True)

    @property
    def created_at(self):
        return utils.snowflake_time(self.id)

    async def create(self) -> bool:
        """
        Post a new Guild instance.

        Returns a bool informing you if a new User object was inserted or not.
        """
        query = """
        INSERT INTO users (id, name, muted_role_id, log_channel_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT DO NOTHING;
        """

        con = await self.ensure_con()

        response = await con.execute(
            query,
            self.id,
            self.name,
            self.muted_role_id,
            self.log_channel_id
        )

        return response.split()[-1] == "1"

    async def update(self, **new_kwargs):
        verified = {}

        for arg in ("name", "muted_role_id", "log_channel_id"):
            try:
                value = new_kwargs[arg]
            except KeyError:
                continue

            column: Column = getattr(self, arg)

            check = column.column_type.python
            if value is None and not column.nullable:
                raise TypeError('Cannot pass None to non-nullable column %s.' % column.name)
            elif not check or not isinstance(value, check):
                fmt = 'column {0.name} expected {1.__name__}, received {2.__class__.__name__}'
                raise TypeError(fmt.format(column, check, value))

            verified[arg] = value
            setattr(self, arg, value)

        query = """UPDATE guilds SET name = $1, muted_role_id = $2, log_channel_id = $3"""
        con = await self.ensure_con()
        return await con.execute(query, self.name, self.muted_role_id, self.log_channel_id)
