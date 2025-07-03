from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Enum, Boolean
from sqlalchemy.orm import relationship
from .base import Base
import enum

# Roles de usuario
class UserRole(str, enum.Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.viewer)


# Departamentos
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    direction = Column(String, nullable=False)

    reservations = relationship("Reservation", back_populates="department")
    inventory_items = relationship("InventoryItem", back_populates="department")


# Inventario
class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)

    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="inventory_items")


# Plataformas de reserva
class BookingPlatform(Base):
    __tablename__ = "booking_platforms"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=True)
    icon = Column(String, nullable=True) # URL o ruta del icono


# Estados de pago
class PaymentStatus(str, enum.Enum):
    complete = "complete"
    deposit = "deposit"
    pending = "pending"


# Reservas
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, nullable=False)
    guest_phone = Column(String, nullable=True)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    people_count = Column(Integer, nullable=False)
    beds = Column(Integer, nullable=False)
    origin_platform_id = Column(Integer, ForeignKey("booking_platforms.id"), nullable=True)
    amount_usd = Column(Float, nullable=True)
    amount_ars = Column(Float, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    total_revenue_ars = Column(Float, nullable=True) # Total de ganancias en ARS Netas
    down_payment_ars = Column(Float, nullable=True) # En caso de que pague una seña
    amount_due = Column(Float, nullable=True)
    is_blocked_on_other_platforms = Column(Boolean, default=False)

    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="reservations")
    platform = relationship("BookingPlatform")
    costs = relationship("ReservationCost", back_populates="reservation")


# Costos de la reserva
class ReservationCost(Base):
    __tablename__ = "reservation_costs"

    id = Column(Integer, primary_key=True)
    category = Column(String) # ej., "canasta de bienvenida", "limpieza", "lavandería"
    description = Column(String)
    amount = Column(Float)
    date = Column(Date)

    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    reservation = relationship("Reservation", back_populates="costs")


# Lista negra
class BlacklistEntry(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True)
    guest_name = Column(String)
    guest_phone = Column(String)
    reason = Column(String)
    date_added = Column(Date)