from pprint import pprint
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, date
import datetime


class CustomerReading(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    phone_number: int | None = Field(index=True)
    meter_date: date | None = None
    meter_reading: int | None = None
    is_bill_date: bool | None = None


class Bill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bill_date: date | None = None
    bill_reading: int | None = None
    meter_date: date | None = None
    meter_reading: int | None = None
    estimated_reading: int | None = Field(default=None, index=True)
    estimated_bill: float | None = None


sqlite_file_name = "reading.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/readings/")
def store_meter_reading(customer_reading: CustomerReading):
    with Session(engine) as session:
        customer_reading.id = int(customer_reading.id)
        customer_reading.phone_number = int(customer_reading.phone_number)
        # pprint(datetime.datetime.strptime(customer_reading.meter_date,'%Y-%m-%d'))
        customer_reading.meter_date = datetime.datetime.strptime(customer_reading.meter_date, '%Y-%m-%d')
        customer_reading.meter_reading = int(customer_reading.meter_reading)
        customer_reading.is_bill_date = bool(customer_reading.is_bill_date)
        pprint(customer_reading)
        session.add(customer_reading)
        session.commit()
        session.refresh(customer_reading)
        return customer_reading


@app.get("/readings/")
async def show_readings():
    with Session(engine) as session:
        customer_readings = session.exec(select(CustomerReading)).all()
        return customer_readings


def calculate_bill_amount(estimated_reading):
    pprint(estimated_reading)
    estimated_bill = float(estimated_reading / 100.00)
    if estimated_reading < 500:
        pprint("Bill uses Lower Scale calculation.")
        if estimated_reading in range(401, 500):
            pprint("range 401 - 500")
            estimated_bill = (estimated_reading - 400) * 6.00 + 400 * 4.50 + 200 * 2.25
        if estimated_reading in range(201, 400):
            pprint("range 201 - 400")
            estimated_bill = (estimated_reading - 200) * 4.50 + 200 * 2.25
        if estimated_reading in range(101, 200):
            pprint("range 101 - 200")
            estimated_bill = (estimated_reading - 100) * 2.25
        if estimated_reading in range(1, 100):
            pprint("range 1 - 100")
            estimated_bill = 0
    else:
        pprint("Bill uses Higher Scale calculation.")
        if estimated_reading > 1000:
            pprint("range more than 1000")
            estimated_bill = (estimated_reading - 1000) * 11.00 + 200 * 10.00 + 200 * 9.00 + 100 * 8.00 + 100 * 6.00 + 300 * 4.50
        if estimated_reading in range(801, 1000):
            pprint("range 801 - 1000")
            estimated_bill = (estimated_reading - 800) * 10.00 + 200 * 9.00 + 100 * 8.00 + 100 * 6.00 + 300 * 4.50
        if estimated_reading in range(601, 800):
            pprint("range 601 - 800")
            estimated_bill = (estimated_reading - 600) * 9.00 + 100 * 8.00 + 100 * 6.00 + 300 * 4.50
        if estimated_reading in range(501, 600):
            pprint("range 501 - 600")
            estimated_bill = (estimated_reading - 500) * 8.00 + 100 * 6.00 + 300 * 4.50
        if estimated_reading in range(1, 500):
            pprint("range 1 - 500")
            estimated_bill = 9999
    print("Estimated bill is %s calculated from estimated reading of %s", str(estimated_bill), str(estimated_reading))
    return estimated_bill


@app.post("/estimated-bill/")
def estimate_bill_amount(bill_reading: Bill):
    with Session(engine) as session:
        bill_reading.id = int(bill_reading.id)
        bill_reading.bill_date = datetime.datetime.strptime(bill_reading.bill_date, '%Y-%m-%d')
        bill_reading.bill_reading = int(bill_reading.bill_reading)
        bill_reading.meter_date = datetime.datetime.strptime(bill_reading.meter_date, '%Y-%m-%d')
        bill_reading.meter_reading = int(bill_reading.meter_reading)
        bill_reading.estimated_reading = bill_reading.meter_reading - bill_reading.bill_reading
        # bill_reading.estimated_bill = float(bill_reading.estimated_reading / 100.00)
        bill_reading.estimated_bill = calculate_bill_amount(bill_reading.estimated_reading)
        session.add(bill_reading)
        session.commit()
        session.refresh(bill_reading)
        return bill_reading


@app.get("/estimated-bill/")
async def show_estimated_bill_amounts():
    with Session(engine) as session:
        bill_readings = session.exec(select(Bill)).all()
        return bill_readings

# uvicorn main:app --host 0.0.0.0 --port 8001
