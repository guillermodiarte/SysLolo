from pydantic import BaseModel

class DepartmentBase(BaseModel):
    name: str
    direction: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        from_attributes = True
