from sqlalchemy import Column, DateTime, Integer, String, Text, func
from app.core.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False)
    input_json = Column(Text, default="")
    output_json = Column(Text, default="")
    status = Column(String(50), default="success")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
