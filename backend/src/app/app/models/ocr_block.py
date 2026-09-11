from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from app.database.base import Base


class OCRBlock(Base):
    __tablename__ = "ocr_blocks"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False, index=True)

    page_number = Column(Integer, nullable=False, default=1)
    block_index = Column(Integer, nullable=False, default=0)
    type = Column(String, nullable=False, default="paragraph") # header | paragraph | table | list | line
    text = Column(Text, nullable=False, default="")
    bbox_json = Column(String, nullable=True) # JSON string array [x0, y0, x1, y1]
    confidence = Column(Float, nullable=False, default=1.0)
