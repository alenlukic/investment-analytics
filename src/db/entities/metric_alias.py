from sqlalchemy import Column, Integer, Sequence

from src.db import Base, metadata


class MetricAlias(Base):
    __tablename__ = 'stock_metric_alias'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, Sequence('stock_metric_alias_seq', metadata=metadata), index=True, unique=True,
                primary_key=True)

    def __eq__(self, other):
        return self.id == other.id and self.__class__.__name__ == other.__class__.__name__

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.id))
