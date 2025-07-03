from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Department
from app.schemas.department_schema import DepartmentCreate, DepartmentRead, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentRead)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = Department(
        name=department.name,
        direction=department.direction
        )
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@router.get("/", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).get(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return department

@router.put("/{department_id}", response_model=DepartmentRead)
def update_department(department_id: int, department_data: DepartmentUpdate, db: Session = Depends(get_db)):
    department = db.query(Department).get(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    department.name = department_data.name
    department.direction = department_data.direction
    db.commit()
    db.refresh(department)
    return department

@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).get(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    db.delete(department)
    db.commit()
    return {"ok": True, "mensaje": "Departamento eliminado correctamente"}
