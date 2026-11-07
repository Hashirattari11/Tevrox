"""Pydantic schemas for administrative endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

# ─── Statistics ─────────────────────────────────────────────────────

class AdminStatsOverviewResponse(BaseModel):
    totalProducts: int
    verifiedProducts: int
    unverifiedProducts: int
    rejectedProducts: int
    totalUsers: int
    activeUsers: int
    totalIngredients: int
    unreviewedIngredients: int
    pendingReviewItems: int
    recentActivity: int


class AdminSignupPoint(BaseModel):
    date: str
    count: int


# Response model alias: list of daily signup points
AdminSignupsStatsResponse = list[AdminSignupPoint]


# ─── Users ──────────────────────────────────────────────────────────

class AdminUserItem(BaseModel):
    id: str
    email: str
    name: str
    role: str
    active: bool
    created: datetime | None = None
    lastLogin: datetime | None = None


class AdminUsersListResponse(BaseModel):
    users: list[AdminUserItem]
    total: int
    skip: int
    limit: int


class AdminActionResponse(BaseModel):
    message: str


# ─── Audit Logs ─────────────────────────────────────────────────────

class AdminAuditLogItem(BaseModel):
    id: str
    actor: str
    action: str
    entityType: str
    entityId: str | None = None
    beforeSummary: str | None = None
    afterSummary: str | None = None
    createdAt: datetime | None = None


class AdminAuditLogsListResponse(BaseModel):
    logs: list[AdminAuditLogItem]
    total: int
    skip: int
    limit: int


# ─── Products Bulk Actions ─────────────────────────────────────────

class AdminBulkProductActionRequest(BaseModel):
    product_ids: list[str] = Field(min_length=1, max_length=100)


class AdminBulkActionResponse(BaseModel):
    message: str
