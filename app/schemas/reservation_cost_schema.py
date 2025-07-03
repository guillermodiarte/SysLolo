from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReservationCostBase(BaseModel):
    category: str  # Ej: "limpieza", "canasta de bienvenida"
    description: Optional[str] = None
    amount: float
    date: date
    reservation_id: int
    department_id: Optional[int] = None


class ReservationCostCreate(ReservationCostBase):
    pass


class ReservationCostUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None # type: ignore
    department_id: Optional[int] = None


class ReservationCostResponse(ReservationCostBase):
    id: int

    class Config:
        from_attributes = True
