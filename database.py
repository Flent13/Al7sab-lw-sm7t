from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define the SQLite database
DATABASE_URL = "sqlite:///inventory.db"

# Create the database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define the Item model
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)

# Define the Invoice model
class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    subtotal = Column(Float, nullable=False)
    salestax = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    date = Column(String, nullable=False)

# Define the InvoiceItem model
class InvoiceItem(Base):
    __tablename__ = 'invoice_items'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    item = relationship("Item")

Invoice.items = relationship("InvoiceItem", order_by=InvoiceItem.id, back_populates="invoice")

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a sessionmaker
Session = sessionmaker(bind=engine)
