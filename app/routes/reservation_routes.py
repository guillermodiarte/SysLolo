from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.schemas.reservation_schema import ReservationCreate, ReservationResponse, ReservationUpdate
from app.models.models import Reservation, ReservationCost, BookingPlatform
from app.database import get_db


router = APIRouter(prefix="/reservations", tags=["Reservas"])

# Tasa de cambio actual (por el momento, luego se podría integrar una API)
USD_TO_ARS_RATE = 1200


# Verifica si hay superposición de fechas para el mismo departamento
def check_overlapping_reservation(db: Session, check_in: date, check_out: date, department_id: int, reservation_id: Optional[int] = None):
    query = db.query(Reservation).filter(
        Reservation.department_id == department_id,
        Reservation.check_out > check_in,
        Reservation.check_in < check_out
    )

    if reservation_id:
        query = query.filter(Reservation.id != reservation_id)

    if query.first():
        raise HTTPException(status_code=400, detail="Ya existe una reserva para esas fechas en este departamento.")


# Crear una nueva reserva
@router.post("/", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    # Validación de superposición de fechas
    check_overlapping_reservation(db, reservation.check_in, reservation.check_out, reservation.department_id)

    reservation_data = reservation.model_dump()

    # Validar origin_platform_id si se proporciona
    if reservation_data.get("origin_platform_id") is not None:
        platform_id = reservation_data["origin_platform_id"]
        # Asegurarse de que el ID no sea 0 si no se maneja en la DB
        if platform_id == 0:
            raise HTTPException(status_code=400, detail="El 'origin_platform_id' no puede ser 0. Use 'null' para reservas directas.")
        
        # Verificar que el platform_id exista en la tabla BookingPlatform
        existing_platform = db.query(BookingPlatform).filter(BookingPlatform.id == platform_id).first()
        if not existing_platform:
            raise HTTPException(status_code=400, detail=f"El 'origin_platform_id' {platform_id} no existe en la base de datos de plataformas de reserva.")
    
    # Lógica de cálculo de amount_ars
    # Aseguramos que amount_ars siempre tenga un valor antes de ser guardado
    if reservation_data.get("amount_usd") is not None:
        # Si se proporciona amount_usd, calculamos amount_ars
        reservation_data["amount_ars"] = reservation_data["amount_usd"] * USD_TO_ARS_RATE
    elif reservation_data.get("amount_ars") is None:
        # Si no se proporciona amount_usd y amount_ars tampoco, levantamos un error
        # Porque amount_ars es nullable=False en el modelo de la DB
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos 'amount_usd' o 'amount_ars'. 'amount_ars' no puede ser nulo.")
    
    # Si amount_ars fue provided directamente y no amount_usd, ya está en reservation_data


    # Cálculo del total_revenue_ars
    # Si total_revenue_ars no se proporciona, asumimos que es igual a amount_ars
    if reservation_data.get("total_revenue_ars") is None:
        # Usamos el valor final de amount_ars (calculado o proporcionado)
        reservation_data["total_revenue_ars"] = reservation_data.get("amount_ars")

    # Cálculo del monto restante (amount_due)
    amount_due = None
    # Solo calculamos amount_due si hay un total_revenue_ars
    if reservation_data.get("total_revenue_ars") is not None:
        if reservation_data.get("down_payment_ars") is not None:
            if reservation_data["down_payment_ars"] > reservation_data["total_revenue_ars"]:
                raise HTTPException(status_code=400, detail="El valor de la seña no puede ser mayor que el total de ganancias.")
            amount_due = reservation_data["total_revenue_ars"] - reservation_data["down_payment_ars"]
        else:
            # Si no hay seña pero sí total_revenue_ars, el monto adeudado es el total_revenue_ars
            amount_due = reservation_data["total_revenue_ars"]
    
    reservation_data["amount_due"] = amount_due

    # Crear objeto reserva
    new_reservation = Reservation(**reservation_data)

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation


# Listar todas las reservas
@router.get("/", response_model=List[ReservationResponse])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()


# Obtener una reserva por ID
@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    return reservation


# Actualizar una reserva
@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(reservation_id: int, data: ReservationUpdate, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    updated_data = data.model_dump(exclude_unset=True) 

    # Validar origin_platform_id si se proporciona en la actualización
    if "origin_platform_id" in updated_data and updated_data["origin_platform_id"] is not None:
        platform_id = updated_data["origin_platform_id"]
        if platform_id == 0:
            raise HTTPException(status_code=400, detail="El 'origin_platform_id' no puede ser 0. Use 'null' para reservas directas.")
        existing_platform = db.query(BookingPlatform).filter(BookingPlatform.id == platform_id).first()
        if not existing_platform:
            raise HTTPException(status_code=400, detail=f"El 'origin_platform_id' {platform_id} no existe en la base de datos de plataformas de reserva.")
    elif "origin_platform_id" in updated_data and updated_data["origin_platform_id"] is None:
        # Si se envía explícitamente null, permitimos que se borre la referencia a la plataforma
        pass # No se necesita validación adicional aquí

    # Lógica de cálculo de amount_ars al actualizar
    if "amount_usd" in updated_data and updated_data["amount_usd"] is not None:
        updated_data["amount_ars"] = updated_data["amount_usd"] * USD_TO_ARS_RATE
    # Si amount_usd se envía como None y amount_ars tampoco se envía, se mantendrá el amount_ars actual de la reserva.
    # Si amount_ars se envía como None y no hay amount_usd, esto podría causar un problema
    # si el modelo de DB no permite NULL. La validación está en el commit al final.
    elif "amount_ars" in updated_data and updated_data["amount_ars"] is None:
        # Si el usuario intenta establecer amount_ars a None explícitamente, pero la columna no es nullable
        raise HTTPException(status_code=400, detail="'amount_ars' no puede ser nulo. Debe proporcionar un valor válido.")


    # Actualizar los campos de la reserva con los datos nuevos
    for field, value in updated_data.items():
        setattr(reservation, field, value)

    # Validar fechas si se actualizaron (usando los valores actualizados en 'reservation')
    check_in = reservation.check_in
    check_out = reservation.check_out
    department_id = reservation.department_id

    check_overlapping_reservation(db, check_in, check_out, department_id, reservation_id=reservation.id)

    # Recalcular total_revenue_ars si es necesario (basado en el amount_ars actualizado)
    if reservation.total_revenue_ars is None and reservation.amount_ars is not None:
        reservation.total_revenue_ars = reservation.amount_ars

    # Recalcular amount_due después de posibles cambios en total_revenue_ars o down_payment_ars
    if reservation.total_revenue_ars is not None:
        if reservation.down_payment_ars is not None:
            if reservation.down_payment_ars > reservation.total_revenue_ars:
                raise HTTPException(status_code=400, detail="El valor de la seña no puede ser mayor que el total de ganancias.")
            reservation.amount_due = reservation.total_revenue_ars - reservation.down_payment_ars
        else:
            # Si no hay seña pero sí total_revenue_ars, el monto adeudado es el total_revenue_ars
            reservation.amount_due = reservation.total_revenue_ars
    else:
        reservation.amount_due = None # Si no hay total_revenue_ars, no hay monto adeudado


    db.commit()
    db.refresh(reservation)
    return reservation

# El resto de las rutas (list_reservations, get_reservation, delete_reservation, get_net_profit)
# no necesitan cambios, ya que operan sobre los datos persistidos.

# Eliminar una reserva
@router.delete("/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    db.delete(reservation)
    db.commit()
    return {"ok": True}


#endpoint para calcular la ganancia neta de una reserva, es decir:
#Ganancia neta = total_revenue_ars (o amount_ars si no hay total) - suma de todos los costos asociados a esa reserva.
@router.get("/{reservation_id}/net_profit")
def get_net_profit(reservation_id: int = Path(..., description="ID de la reserva"), db: Session = Depends(get_db)):
    # Buscar la reserva
    reservation = db.query(Reservation).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    # Obtener ingreso
    # Ahora usamos total_revenue_ars. Si es None, usamos amount_ars.
    total_income = reservation.total_revenue_ars or reservation.amount_ars

    # Sumar los costos asociados
    total_cost = db.query(func.coalesce(func.sum(ReservationCost.amount), 0)) \
        .filter(ReservationCost.reservation_id == reservation_id) \
        .scalar()

    # Calcular ganancia neta
    net_profit = total_income - total_cost

    return {
        "reserva_id": reservation_id,
        "ingreso_total": total_income,
        "costo_total": total_cost,
        "ganancia_neta": net_profit
    }