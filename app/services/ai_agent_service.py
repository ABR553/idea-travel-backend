"""Servicio de generacion de contenido con IA usando pydantic_ai."""

import logging

from pydantic_ai import Agent

from app.config import settings
from app.schemas.ai_generate import (
    AIAccommodation,
    AIBlogPost,
    AIDestination,
    AIExperience,
    AIGenerateResponse,
    AIPack,
    AIRouteStep,
)

logger = logging.getLogger("ideatravel.ai")

SYSTEM_PROMPT = """\
Eres un experto creador de contenido de viajes para la plataforma "Tengo Un Viaje".
Tu trabajo es generar packs de viaje completos y articulos de blog asociados.

Reglas:
- Genera contenido BILINGUE (espanol e ingles) para cada campo.
- Los slugs deben ser URL-friendly en espanol (ej: "japon-en-7-dias").
- Las imagenes deben ser URLs validas de Unsplash con formato: https://images.unsplash.com/photo-XXXXX?w=800
- Cada destino debe tener EXACTAMENTE 3 alojamientos: uno budget, uno standard, uno premium.
- Cada destino debe tener al menos 2 experiencias con proveedores reales (getyourguide o civitatis).
- Los precios deben ser realistas en EUR.
- Los ratings deben estar entre 3.5 y 5.0.
- La ruta debe cubrir TODOS los dias del viaje, asignando cada dia a un destino.
- El blog debe ser un articulo completo en Markdown (minimo 500 palabras por idioma) relacionado con el pack.
- La categoria del blog debe ser una de: guia, presupuesto, epoca, consejos, lista.
- El cover_image del pack y del blog deben ser diferentes.
- Amenities de alojamiento en espanol.
"""

_agent: Agent[None, AIGenerateResponse] = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=SYSTEM_PROMPT,
    output_type=AIGenerateResponse,
)


def _mock_response(description: str) -> AIGenerateResponse:
    """Respuesta mock cuando no hay API key real configurada."""
    return AIGenerateResponse(
        pack=AIPack(
            slug="paris-en-5-dias",
            cover_image="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
            duration_days=5,
            price_from=450.0,
            price_to=2800.0,
            featured=True,
            title_es="Paris en 5 dias",
            title_en="Paris in 5 days",
            description_es="Descubre la Ciudad de la Luz en un viaje de 5 dias lleno de cultura, gastronomia y romanticismo. Visita la Torre Eiffel, el Louvre, Montmartre y mucho mas.",
            description_en="Discover the City of Light in a 5-day trip full of culture, gastronomy and romance. Visit the Eiffel Tower, the Louvre, Montmartre and much more.",
            short_description_es="Cultura, gastronomia y romanticismo en la Ciudad de la Luz",
            short_description_en="Culture, gastronomy and romance in the City of Light",
            duration_es="5 dias / 4 noches",
            duration_en="5 days / 4 nights",
            destinations=[
                AIDestination(
                    name_es="Paris",
                    name_en="Paris",
                    country_es="Francia",
                    country_en="France",
                    description_es="La capital francesa enamora con sus bulevares, museos y gastronomia de clase mundial.",
                    description_en="The French capital captivates with its boulevards, museums and world-class gastronomy.",
                    image="https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800",
                    days=5,
                    accommodations=[
                        AIAccommodation(
                            tier="budget",
                            name_es="Generator Paris",
                            name_en="Generator Paris",
                            description_es="Albergue de diseno en el distrito 10 con terraza rooftop.",
                            description_en="Design hostel in the 10th district with rooftop terrace.",
                            price_per_night=35.0,
                            currency="EUR",
                            amenities=["WiFi", "Terraza rooftop", "Bar", "Cocina compartida"],
                            rating=4.2,
                            image="https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                            nights=4,
                        ),
                        AIAccommodation(
                            tier="standard",
                            name_es="Hotel Le Marais",
                            name_en="Hotel Le Marais",
                            description_es="Hotel boutique en el corazon del Marais con encanto parisino.",
                            description_en="Boutique hotel in the heart of Le Marais with Parisian charm.",
                            price_per_night=180.0,
                            currency="EUR",
                            amenities=["WiFi", "Desayuno", "Conserjeria", "Aire acondicionado"],
                            rating=4.5,
                            image="https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
                            nights=4,
                        ),
                        AIAccommodation(
                            tier="premium",
                            name_es="Le Pavillon de la Reine",
                            name_en="Le Pavillon de la Reine",
                            description_es="Hotel de lujo en Place des Vosges con spa y jardin privado.",
                            description_en="Luxury hotel in Place des Vosges with spa and private garden.",
                            price_per_night=450.0,
                            currency="EUR",
                            amenities=["WiFi", "Spa", "Restaurante", "Jardin privado", "Mayordomo"],
                            rating=4.9,
                            image="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                            nights=4,
                        ),
                    ],
                    experiences=[
                        AIExperience(
                            title_es="Tour por la Torre Eiffel con acceso prioritario",
                            title_en="Eiffel Tower Tour with Priority Access",
                            description_es="Sube a la Torre Eiffel sin colas con un guia experto que te contara su historia.",
                            description_en="Skip the lines at the Eiffel Tower with an expert guide who will share its history.",
                            duration_es="2 horas",
                            duration_en="2 hours",
                            provider="getyourguide",
                            price=45.0,
                            currency="EUR",
                            rating=4.7,
                            image="https://images.unsplash.com/photo-1543349689-9a4d426bee8e?w=800",
                        ),
                        AIExperience(
                            title_es="Visita guiada al Museo del Louvre",
                            title_en="Guided Tour of the Louvre Museum",
                            description_es="Descubre las obras maestras del Louvre con un guia experto en arte.",
                            description_en="Discover the Louvre's masterpieces with an expert art guide.",
                            duration_es="3 horas",
                            duration_en="3 hours",
                            provider="civitatis",
                            price=55.0,
                            currency="EUR",
                            rating=4.8,
                            image="https://images.unsplash.com/photo-1499426600726-ac637037acf0?w=800",
                        ),
                    ],
                ),
            ],
            route_steps=[
                AIRouteStep(day=1, title_es="Llegada y Montmartre", title_en="Arrival and Montmartre", description_es="Llegada a Paris, check-in y paseo por Montmartre. Visita al Sacre-Coeur y cena en un bistrot local.", description_en="Arrive in Paris, check-in and stroll through Montmartre. Visit Sacre-Coeur and dinner at a local bistrot.", destination_name="Paris"),
                AIRouteStep(day=2, title_es="Torre Eiffel y Campos Eliseos", title_en="Eiffel Tower and Champs-Elysees", description_es="Manana en la Torre Eiffel con acceso prioritario. Tarde paseando por los Campos Eliseos hasta el Arco del Triunfo.", description_en="Morning at the Eiffel Tower with priority access. Afternoon strolling the Champs-Elysees to the Arc de Triomphe.", destination_name="Paris"),
                AIRouteStep(day=3, title_es="Louvre y Le Marais", title_en="Louvre and Le Marais", description_es="Visita guiada al Museo del Louvre. Tarde explorando el barrio de Le Marais.", description_en="Guided tour of the Louvre Museum. Afternoon exploring the Le Marais district.", destination_name="Paris"),
                AIRouteStep(day=4, title_es="Versalles", title_en="Versailles", description_es="Excursion de dia completo al Palacio de Versalles y sus jardines.", description_en="Full day excursion to the Palace of Versailles and its gardens.", destination_name="Paris"),
                AIRouteStep(day=5, title_es="Barrio Latino y despedida", title_en="Latin Quarter and farewell", description_es="Ultimo dia por el Barrio Latino, Notre-Dame y compras de recuerdos.", description_en="Last day in the Latin Quarter, Notre-Dame and souvenir shopping.", destination_name="Paris"),
            ],
        ),
        blog=AIBlogPost(
            slug="guia-completa-paris-5-dias",
            cover_image="https://images.unsplash.com/photo-1431274172761-fca41d930114?w=800",
            category="guia",
            title_es="Guia completa: Paris en 5 dias",
            title_en="Complete guide: Paris in 5 days",
            excerpt_es="Todo lo que necesitas saber para disfrutar de Paris en 5 dias: itinerario, alojamiento, presupuesto y consejos practicos.",
            excerpt_en="Everything you need to know to enjoy Paris in 5 days: itinerary, accommodation, budget and practical tips.",
            content_es="""# Guia completa: Paris en 5 dias

Paris es una de esas ciudades que hay que visitar al menos una vez en la vida. Con esta guia tendras todo lo necesario para aprovechar al maximo tus 5 dias en la Ciudad de la Luz.

## Dia 1: Llegada y Montmartre

Tu primer dia en Paris deberia ser tranquilo para adaptarte al ritmo de la ciudad. Despues del check-in, dirigete al barrio de **Montmartre**, uno de los mas encantadores de Paris. Sube hasta la **Basilica del Sacre-Coeur** para disfrutar de unas vistas panoramicas increibles.

Para cenar, busca un bistrot tipico en las calles empedradas de Montmartre. Los precios son razonables y la comida es autentica.

## Dia 2: Torre Eiffel y Campos Eliseos

No hay visita a Paris que este completa sin ver la **Torre Eiffel**. Te recomendamos reservar un tour con acceso prioritario para evitar las largas colas. Desde la cima, las vistas de Paris son inolvidables.

Por la tarde, pasea por los **Campos Eliseos** hasta llegar al **Arco del Triunfo**. Si te queda energia, sube a la terraza del Arco para otra perspectiva espectacular.

## Dia 3: Louvre y Le Marais

Dedica la manana al **Museo del Louvre**. Con una visita guiada podras ver las obras mas importantes sin perderte en sus enormes pasillos. La Mona Lisa, la Venus de Milo y la Victoria de Samotracia son imprescindibles.

Por la tarde, explora **Le Marais**, un barrio lleno de galerias de arte, tiendas vintage y cafeterias con encanto.

## Dia 4: Versalles

Una excursion al **Palacio de Versalles** es imprescindible. Los jardines son espectaculares, especialmente en primavera y verano. Reserva la entrada con antelacion.

## Dia 5: Barrio Latino y despedida

Tu ultimo dia, pasea por el **Barrio Latino**, visita los alrededores de **Notre-Dame** y compra recuerdos en las tiendas locales.

## Presupuesto estimado

- **Budget**: 450-600 EUR (albergue + transporte publico + comida economica)
- **Standard**: 1200-1600 EUR (hotel boutique + restaurantes + entradas)
- **Premium**: 2500-2800 EUR (hotel de lujo + experiencias VIP + gastronomia gourmet)

## Consejos practicos

- Compra un **Paris Visite Pass** para el transporte publico
- Reserva entradas online para museos y monumentos
- Lleva calzado comodo: Paris se recorre andando
- La mejor epoca para visitar es de abril a junio o septiembre a octubre
""",
            content_en="""# Complete Guide: Paris in 5 Days

Paris is one of those cities everyone should visit at least once. This guide will help you make the most of your 5 days in the City of Light.

## Day 1: Arrival and Montmartre

Your first day in Paris should be relaxed to get into the city's rhythm. After check-in, head to the **Montmartre** neighborhood, one of Paris's most charming areas. Climb up to the **Sacre-Coeur Basilica** for incredible panoramic views.

For dinner, find a typical bistrot in the cobblestone streets of Montmartre. Prices are reasonable and the food is authentic.

## Day 2: Eiffel Tower and Champs-Elysees

No visit to Paris is complete without seeing the **Eiffel Tower**. We recommend booking a tour with priority access to avoid the long queues. From the top, the views of Paris are unforgettable.

In the afternoon, stroll along the **Champs-Elysees** to the **Arc de Triomphe**. If you have energy left, climb to the Arc's terrace for another spectacular perspective.

## Day 3: Louvre and Le Marais

Spend the morning at the **Louvre Museum**. With a guided tour, you can see the most important works without getting lost in its enormous corridors. The Mona Lisa, Venus de Milo and Winged Victory of Samothrace are must-sees.

In the afternoon, explore **Le Marais**, a neighborhood full of art galleries, vintage shops and charming cafes.

## Day 4: Versailles

A day trip to the **Palace of Versailles** is essential. The gardens are spectacular, especially in spring and summer. Book your tickets in advance.

## Day 5: Latin Quarter and Farewell

On your last day, walk through the **Latin Quarter**, visit the area around **Notre-Dame** and pick up souvenirs from local shops.

## Estimated Budget

- **Budget**: 450-600 EUR (hostel + public transport + budget food)
- **Standard**: 1200-1600 EUR (boutique hotel + restaurants + tickets)
- **Premium**: 2500-2800 EUR (luxury hotel + VIP experiences + gourmet dining)

## Practical Tips

- Buy a **Paris Visite Pass** for public transport
- Book tickets online for museums and monuments
- Wear comfortable shoes: Paris is best explored on foot
- The best time to visit is April to June or September to October
""",
        ),
    )


async def generate_content(description: str) -> AIGenerateResponse:
    """Genera un pack y blog post usando IA o mock si no hay API key."""
    if settings.anthropic_api_key == "mock-key-replace-me":
        logger.info("Usando respuesta mock (API key no configurada)")
        return _mock_response(description)

    logger.info("Generando contenido con IA para: %s", description[:100])
    result = await _agent.run(
        f"Genera un pack de viaje completo y un articulo de blog basado en esta descripcion: {description}",
    )
    return result.data
