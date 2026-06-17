import asyncio
import datetime as dt
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User

SAMPLE_EVENTS = [
    {
        "title": "Festival de Jazz na Praça",
        "description": "Um final de semana com o melhor do jazz local e nacional em um ambiente aberto e gratuito.",
        "venue_name": "Praça Central",
        "address": "Rua das Flores, 123",
        "neighborhood": "Centro",
        "city": "Rio de Janeiro",
        "category_name": "show",
    },
    {
        "title": "Exposição: Sombras e Luzes",
        "description": "Uma mostra contemporânea explorando o contraste na fotografia urbana.",
        "venue_name": "Galeria de Arte Moderna",
        "address": "Av. Paulista, 1500",
        "neighborhood": "Bela Vista",
        "city": "São Paulo",
        "category_name": "exposicao",
    },
    {
        "title": "Hamlet - O Clássico Revisitado",
        "description": "Uma interpretação moderna da tragédia de Shakespeare, focada nas tensões políticas atuais.",
        "venue_name": "Teatro Municipal",
        "address": "Praça Ramos de Azevedo, s/n",
        "neighborhood": "Centro",
        "city": "São Paulo",
        "category_name": "peca",
    },
    {
        "title": "Carnaval de Rua: Bloco dos Amigos",
        "description": "O bloco mais animado do bairro desfila celebrando a amizade e a cultura popular.",
        "venue_name": "Rua da Alegria",
        "address": "Rua da Alegria, 10",
        "neighborhood": "Santa Teresa",
        "city": "Rio de Janeiro",
        "category_name": "festival",
    },
    {
        "title": "Oficina de Escultura em Argila",
        "description": "Aprenda as técnicas básicas de modelagem em argila com artistas locais.",
        "venue_name": "Centro Cultural Comunitário",
        "address": "Rua Esperança, 45",
        "neighborhood": "Vila Nova",
        "city": "Belo Horizonte",
        "category_name": "outro",
    },
]

async def seed_events():
    async with AsyncSessionLocal() as session:
        # Get admin user
        result = await session.execute(select(User).where(User.email == "admin@agendacultural.com"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Error: Admin user not found. Please run app.seed first.")
            return

        # Get categories
        result = await session.execute(select(Category))
        categories = {c.name: c.id for c in result.scalars().all()}
        
        if not categories:
            print("Error: No categories found. Please run app.seed first.")
            return

        # Add sample events
        today = dt.date.today()
        for i, item in enumerate(SAMPLE_EVENTS):
            cat_id = categories.get(item["category_name"])
            if not cat_id:
                # Fallback to 'outro' if specific category doesn't exist
                cat_id = categories.get("outro")
            
            # Check if event already exists by title
            res = await session.execute(select(Event).where(Event.title == item["title"]))
            if res.scalar_one_or_none():
                continue

            event = Event(
                title=item["title"],
                description=item["description"],
                date=today + dt.timedelta(days=random.randint(1, 30)),
                start_time=dt.time(hour=random.randint(18, 21), minute=0),
                venue_name=item["venue_name"],
                address=item["address"],
                neighborhood=item["neighborhood"],
                city=item["city"],
                category_id=cat_id,
                created_by=admin.id,
                status=EventStatus.aprovado, # Auto-approved for seed
                reviewed_by=admin.id,
                reviewed_at=dt.datetime.now(dt.UTC)
            )
            session.add(event)
        
        await session.commit()
        print("Sample events seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_events())
