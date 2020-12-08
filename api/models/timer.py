from postDB import Model, Column, types


class Timer(Model):
    """
    Database Attributes:
        Attributes stored in the `badges` table.

        :param int id:                                  The SERIAL ID of this Timer.
        :param dict data:                               The connected data to the Timer.
        :param str event:                               The kind of timer this is. reminder|tempban|tempmute
        :param :class:`datetime.datetime` expires_at:   When the timer expires.
        :param :class:`datetime.datetime` created_at:   When the timer was created.
    """
    id = Column(types.Serial)
    data = Column(types.JSON)
    event = Column(types.String)
    expires_at = Column(types.DateTime)
    created_at = Column(types.DateTime)
