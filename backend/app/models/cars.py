from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Numeric, Integer, CheckConstraint
from decimal import Decimal
from app.database import Base


class CarsOrm(Base):
    __tablename__ = "cars"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    brand: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
    )
    
    def __repr__(self):
        return f"<Car {self.brand} {self.name}>"