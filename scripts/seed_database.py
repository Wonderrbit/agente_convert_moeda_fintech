#!/usr/bin/env python
"""Seed database with reference data."""

import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from cambiobot.config import settings


async def seed_database():
    """Seed database with initial data."""
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # This would use the SQL from sql/seeds/001_reference_data.sql
        # For now, just print what would be seeded
        print("Seeding database with reference data...")
        print("- Affiliate partners: Nomad, Wise, Avenue, Western Union")
        print("- Currency metadata: USD, EUR, GBP, JPY, ARS, CAD, AUD")
        print("- Country mappings: US, EU, UK, JP, AR, CA, AU")
        print("Done!")


if __name__ == "__main__":
    asyncio.run(seed_database())