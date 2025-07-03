from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import ReservationCost, Reservation
from app.schemas.reservation_cost_schema import ReservationCostCreate, ReservationCostResponse, ReservationCostUpdate

router = APIRouter(prefix="/reservation-costs", tags=["Reservation Costs"])


# Crear un nuevo costo asociado a una reserva
@router.post("/", response_model=ReservationCostResponse)
def create_cost(cost: ReservationCostCreate, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).get(cost.reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    new_cost = ReservationCost(**cost.dict())
    db.add(new_cost)
    db.commit()
    db.refresh(new_cost)
    return new_cost


# Listar todos los costos
@router.get("/", response_model=List[ReservationCostResponse])
def list_costs(db: Session = Depends(get_db)):
    return db.query(ReservationCost).all()


# Listar costos por ID de reserva
@router.get("/by-reservation/{reservation_id}", response_model=List[ReservationCostResponse])
def list_costs_by_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return db.query(ReservationCost).filter(ReservationCost.reservation_id == reservation_id).all()


# Obtener un costo específico por ID
@router.get("/{cost_id}", response_model=ReservationCostResponse)
def get_cost(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(ReservationCost).get(cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="Costo no encontrado.")
    return cost


# Actualizar un costo existente
@router.put("/{cost_id}", response_model=ReservationCostResponse)
def update_cost(cost_id: int, data: ReservationCostUpdate, db: Session = Depends(get_db)):
    cost = db.query(ReservationCost).get(cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="Costo no encontrado.")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(cost, field, value)

    db.commit()
    db.refresh(cost)
    return cost


# Eliminar un costo
@router.delete("/{cost_id}")
def delete_cost(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(ReservationCost).get(cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="Costo no encontrado.")
    db.delete(cost)
    db.commit()
    return {"ok": True}
