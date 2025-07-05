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
    guest_name: str = "Name"
    guest_phone: Optional[str] = "Phone number"
    check_in: date
    check_out: date
    people_count: int = 1
    beds: int = 1
    origin_platform_id: int = 1
    department_id: int = 1
    payment_status: PaymentStatus = None

    down_payment_ars: Optional[float] = 0 # Nuevo campo para la seña
    amount_usd: Optional[float] = 0 # Total cobrado en Dolares
    amount_ars: Optional[float] = 0 # Total cobrado en Pesos
    amount_due: Optional[float] = 0 # Lo que adeuda pagar si pagó una seña
    
    #Estos datos no se modifican en la creación
    total_revenue_ars: Optional[float] = 0 # Total de ganancias en ARS Netas
    is_blocked_on_other_platforms: bool = False # Pregunta si las fechas estan bloqueados en las otras Plataformas


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

    amount_usd: Optional[float] = None # Total cobrado en Dolares
    amount_ars: Optional[float] = None # Total cobrado en Pesos
    down_payment_ars: Optional[float] = None # Nuevo campo para la seña
    amount_due: Optional[float] = None # Lo que adeuda pagar si pagó una seña
    total_revenue_ars: Optional[float] = None # Total de ganancias en ARS Netas

    payment_status: Optional[PaymentStatus] = None
    is_blocked_on_other_platforms: Optional[bool] = None
    department_id: Optional[int] = None


# Esquema de respuesta
class ReservationResponse(ReservationBase):
    id: int

    class Config:
        from_attributes = True