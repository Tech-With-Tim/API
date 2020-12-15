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
