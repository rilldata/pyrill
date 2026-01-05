from typing import Optional
from pydantic import BaseModel, Field


class Org(BaseModel):
    """Org model matching REST API response"""
    id: Optional[str] = None
    name: str
    display_name: Optional[str] = Field(None, alias="displayName")
    description: Optional[str] = None
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    favicon_url: Optional[str] = Field(None, alias="faviconUrl")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    custom_domain: Optional[str] = Field(None, alias="customDomain")
    default_project_role_id: Optional[str] = Field(None, alias="defaultProjectRoleId")
    billing_customer_id: Optional[str] = Field(None, alias="billingCustomerId")
    payment_customer_id: Optional[str] = Field(None, alias="paymentCustomerId")
    billing_email: Optional[str] = Field(None, alias="billingEmail")
    billing_plan_name: Optional[str] = Field(None, alias="billingPlanName")
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")

    model_config = {"populate_by_name": True}