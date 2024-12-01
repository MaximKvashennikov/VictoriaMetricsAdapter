from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Optional, Union, List


class BaseMetricLabel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metric_name: str = Field(alias="__name__")
    job: str = "DefaultJob"
    instance: str = "default-instance-id"
    application_id: str = "DefaultApp"
    application_instance_id: str = "DefaultInstance"
    service_instance_id: str = "default-service-id"
    service_name: str = "DefaultService"
    service_version: str = "1.0.0"
    telemetry_sdk_language: str = "default-language"
    telemetry_sdk_name: str = "default-sdk"
    telemetry_sdk_version: str = "1.0.0"

class BaseMetricData(BaseModel):
    metric: BaseMetricLabel
    values: List[Union[int, float]]
    timestamps: List[int]


class ExampleMetricLabel(BaseMetricLabel):
    security: str = "Unsafe"
    step_count: Optional[str] = None
    risk_name: Optional[str] = None

    @field_validator("step_count", mode="before")
    @classmethod
    def convert_step_count(cls, v):
        if v is not None:
            return str(v)
        return v


class ExampleMetricData(BaseMetricData):
    metric: ExampleMetricLabel
