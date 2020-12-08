from postDB import Model, Column, types


class ModLog(Model):
    """
    Database Attributes:
        Attributes stored in the `` table.

        :param int id:                                  The SERIAL ID of the Log.
        :param str type:                                The type of modlog this is - ban, kick, mute.
        :param :class:`datetime.datetime` expires_at:   The time this token expires.
        :param int timer_id:                            The Optional timer connected to this modlog.
        :param dict data:                               The data connected to this log.
    """
    id = Column(types.Serial, primary_key=True)
    type = Column(types.String(length=16))
    created_at = Column(types.DateTime)
    timer_id = Column(
        types.ForeignKey("timers", "id"),
    )
    data = Column(types.JSON)
