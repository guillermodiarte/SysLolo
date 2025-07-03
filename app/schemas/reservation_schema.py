from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum


# Estado del pago
class PaymentStatus(str, Enum):
    complete = "complete"
    deposit = "deposit"
    pending = "pending"


# Base del esquema de reserva
class ReservationBase(BaseModel):
    guest_name: str
    guest_phone: Optional[str]
    check_in: date
    check_out: date
    people_count: int
    beds: int
    origin_platform_id: Optional[int] = None
    
    amount_usd: Optional[float] = None
    amount_ars: Optional[float] = None # Sigue siendo opcional en la entrada
    
    total_revenue_ars: Optional[float] = None # Renombrado
    down_payment_ars: Optional[float] = None # Nuevo campo para la seña
    
    amount_due: Optional[float] = None # Seguirá siendo calculado automáticamente
    payment_status: PaymentStatus = PaymentStatus.pending
    is_blocked_on_other_platforms: bool = False
    department_id: int


# Esquema para creación
class ReservationCreate(ReservationBase):
    pass


# Esquema para actualización (todos los campos opcionales)
class ReservationUpdate(BaseModel):
    guest_name: Optional[str] = None
    guest_phone: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    people_count: Optional[int] = None
    beds: Optional[int] = None
    origin_platform_id: Optional[int] = None
    amount_usd: Optional[float] = None
    amount_ars: Optional[float] = None
    
    total_revenue_ars: Optional[float] = None # Total de ganancias en ARS Netas
    down_payment_ars: Optional[float] = None # Nuevo campo para la seña

    amount_due: Optional[float] = None
    payment_status: Optional[PaymentStatus] = None
    is_blocked_on_other_platforms: Optional[bool] = None
    department_id: Optional[int] = None


# Esquema de respuesta
class ReservationResponse(ReservationBase):
    id: int

    class Config:
        from_attributes = True