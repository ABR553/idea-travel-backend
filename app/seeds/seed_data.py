"""Seed data with real destinations, accommodations and experiences."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.database import async_session_factory
from app.domain.models.accommodation import Accommodation, AccommodationTranslation
from app.domain.models.blog_post import BlogPost, BlogPostTranslation
from app.domain.models.destination import Destination, DestinationTranslation
from app.domain.models.experience import Experience, ExperienceTranslation
from app.domain.models.pack import Pack, PackTranslation
from app.domain.models.product import Product, ProductTranslation
from app.domain.models.route_step import RouteStep, RouteStepTranslation


def _id() -> uuid.UUID:
    return uuid.uuid4()


def _make_accommodation(
    dest_id: uuid.UUID, tier: str, price: float, image: str,
    amenities: list[str], rating: float,
    name_es: str, desc_es: str, name_en: str, desc_en: str,
    booking_url: str | None = None, nights: int = 1,
) -> Accommodation:
    acc_id = _id()
    return Accommodation(
        id=acc_id, destination_id=dest_id, tier=tier, price_per_night=price,
        currency="EUR", image=image, amenities=amenities, rating=rating,
        booking_url=booking_url, nights=nights,
        translations=[
            AccommodationTranslation(id=_id(), accommodation_id=acc_id, locale="es", name=name_es, description=desc_es),
            AccommodationTranslation(id=_id(), accommodation_id=acc_id, locale="en", name=name_en, description=desc_en),
        ],
    )


def _make_experience(
    dest_id: uuid.UUID, provider: str, url: str, price: float, image: str, rating: float,
    title_es: str, desc_es: str, dur_es: str,
    title_en: str, desc_en: str, dur_en: str,
) -> Experience:
    exp_id = _id()
    return Experience(
        id=exp_id, destination_id=dest_id, provider=provider, affiliate_url=url,
        price=price, currency="EUR", image=image, rating=rating,
        translations=[
            ExperienceTranslation(id=_id(), experience_id=exp_id, locale="es", title=title_es, description=desc_es, duration=dur_es),
            ExperienceTranslation(id=_id(), experience_id=exp_id, locale="en", title=title_en, description=desc_en, duration=dur_en),
        ],
    )


def _make_route_step(pack_id, dest_id, day, t_es, d_es, t_en, d_en) -> RouteStep:
    rs_id = _id()
    return RouteStep(
        id=rs_id, pack_id=pack_id, destination_id=dest_id, day=day,
        translations=[
            RouteStepTranslation(id=_id(), route_step_id=rs_id, locale="es", title=t_es, description=d_es),
            RouteStepTranslation(id=_id(), route_step_id=rs_id, locale="en", title=t_en, description=d_en),
        ],
    )


def _dest(pack_id, order, image, es, en, accs=None, exps=None, days=1) -> Destination:
    did = _id()
    return Destination(
        id=did, pack_id=pack_id, image=image, display_order=order, days=days,
        translations=[
            DestinationTranslation(id=_id(), destination_id=did, locale="es", **es),
            DestinationTranslation(id=_id(), destination_id=did, locale="en", **en),
        ],
        accommodations=accs or [], experiences=exps or [],
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 1: PARIS
# ──────────────────────────────────────────────────────────────────────
def _pack_paris() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        {"name": "Paris", "country": "Francia", "description": "La Ciudad de la Luz enamora con sus bulevares, museos de talla mundial, la Torre Eiffel y una gastronomia que es Patrimonio de la Humanidad."},
        {"name": "Paris", "country": "France", "description": "The City of Light captivates with its boulevards, world-class museums, the Eiffel Tower and a gastronomy that is UNESCO Intangible Heritage."},
        days=5,
        accs=[
            _make_accommodation(None, "budget", 30, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Terraza rooftop", "Bar", "Cocina compartida", "Taquillas"], 4.2,
                "Generator Paris", "Albergue de diseno en el distrito 10, a pasos del Canal Saint-Martin. Terraza rooftop con vistas a Montmartre y ambiente cosmopolita.",
                "Generator Paris", "Design hostel in the 10th district, steps from Canal Saint-Martin. Rooftop terrace with Montmartre views and cosmopolitan atmosphere.",
                booking_url="https://www.booking.com/hotel/fr/generator-paris.html", nights=5),
            _make_accommodation(None, "standard", 200, "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
                ["WiFi", "Desayuno continental", "Conserjeria", "Edificio historico siglo XVII"], 4.5,
                "Hotel de la Bretonnerie", "Hotel boutique en el corazon de Le Marais, en una casa del siglo XVII. Habitaciones unicas con caracter historico.",
                "Hotel de la Bretonnerie", "Boutique hotel in the heart of Le Marais, housed in a 17th-century townhouse. Unique rooms with historic character.",
                booking_url="https://www.booking.com/hotel/fr/de-la-bretonnerie.html", nights=5),
            _make_accommodation(None, "premium", 550, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Spa con piscina", "Restaurante gourmet", "Jardin privado", "Bicicletas gratis", "Mayordomo"], 4.9,
                "Le Pavillon de la Reine & Spa", "Joya oculta de cinco estrellas en la Place des Vosges. Spa completo, jardin secreto y restaurante galardonado.",
                "Le Pavillon de la Reine & Spa", "Hidden five-star gem on Place des Vosges. Full spa, secret garden and award-winning restaurant.",
                booking_url="https://www.booking.com/hotel/fr/le-pavillon-de-la-reine.html", nights=5),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/paris-l16/paris-guided-tour-eiffel-tower-ticket-t29942/", 75,
                "https://images.unsplash.com/photo-1570097703229-b195d6dd291f?w=800", 4.8,
                "Torre Eiffel: visita guiada con acceso a la cima", "Sube a la Torre Eiffel sin colas con guia experto. Visita el apartamento de Gustave Eiffel en la cima a 276 m y disfruta de vistas 360 sobre Paris.", "1.5 horas",
                "Eiffel Tower: guided tour with summit access", "Skip the queue and ascend the Eiffel Tower with an expert guide. Visit Gustave Eiffel's apartment at the summit (276 m) and enjoy 360 views over Paris.", "1.5 hours"),
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/paris/skip-the-line-louvre-museum-guided-tour/", 65,
                "https://images.unsplash.com/photo-1565099824688-e93eb20fe622?w=800", 4.7,
                "Museo del Louvre: visita guiada sin colas", "Evita las colas del museo mas visitado del mundo. Descubre la Mona Lisa, la Venus de Milo y la Victoria de Samotracia con guia certificado.", "2.5 horas",
                "Louvre Museum: skip-the-line guided tour", "Beat the queues at the world's most visited museum. Discover the Mona Lisa, Venus de Milo and Winged Victory with a certified guide.", "2.5 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/paris-l16/paris-seine-river-sightseeing-cruise-by-bateaux-mouches-t735394/", 25,
                "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800", 4.6,
                "Crucero nocturno por el Sena", "Navega por el Sena al anochecer pasando bajo 37 puentes iluminados con vistas a Notre-Dame, el Louvre y la Torre Eiffel centelleante.", "1 hora",
                "Seine River night cruise", "Glide along the Seine at dusk passing under 37 illuminated bridges with views of Notre-Dame, the Louvre and the sparkling Eiffel Tower.", "1 hour"),
        ],
    )
    # Fix dest_id references in accs/exps
    for a in d1.accommodations:
        a.destination_id = d1.id
    for e in d1.experiences:
        e.destination_id = d1.id

    routes = [
        (1, "Llegada y Le Marais", "Llegada a Paris. Paseo por Place des Vosges, Notre-Dame y Sainte-Chapelle. Cena en Le Marais.", "Arrival & Le Marais", "Arrive in Paris. Walk through Place des Vosges, Notre-Dame and Sainte-Chapelle. Dinner in Le Marais."),
        (2, "Louvre y Tullerias", "Visita guiada al Louvre. Paseo por el Jardin de las Tullerias y Palais-Royal.", "Louvre & Tuileries", "Guided Louvre visit. Stroll through Tuileries Garden and Palais-Royal."),
        (3, "Torre Eiffel y Champs-Elysees", "Torre Eiffel con acceso a la cima. Picnic en el Champ-de-Mars. Champs-Elysees y Arco del Triunfo.", "Eiffel Tower & Champs-Elysees", "Eiffel Tower with summit access. Picnic at Champ-de-Mars. Champs-Elysees and Arc de Triomphe."),
        (4, "Montmartre y Sacre-Coeur", "Subida al Sacre-Coeur. Place du Tertre y artistas callejeros. Moulin Rouge y Canal Saint-Martin.", "Montmartre & Sacre-Coeur", "Climb to Sacre-Coeur. Place du Tertre and street artists. Moulin Rouge and Canal Saint-Martin."),
        (5, "Museo d'Orsay y despedida", "Museo d'Orsay (impresionismo). Saint-Germain-des-Pres y Jardin de Luxemburgo. Crucero nocturno por el Sena.", "Musee d'Orsay & farewell", "Musee d'Orsay (Impressionism). Saint-Germain-des-Pres and Luxembourg Gardens. Seine night cruise."),
    ]
    steps = [_make_route_step(pk, d1.id, r[0], r[1], r[2], r[3], r[4]) for r in routes]

    return Pack(
        id=pk, slug="paris-ciudad-de-la-luz", cover_image="https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1200",
        duration_days=5, price_from=480, price_to=3200, price_currency="EUR", featured=True,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Paris: La Ciudad de la Luz",
                description="Descubre Paris a tu ritmo en 5 dias inolvidables. Museos de talla mundial, la Torre Eiffel, Montmartre, cruceros por el Sena y la mejor gastronomia francesa.",
                short_description="5 dias entre museos, monumentos y la magia parisina.", duration="5 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Paris: The City of Light",
                description="Discover Paris at your own pace in 5 unforgettable days. World-class museums, the Eiffel Tower, Montmartre, Seine cruises and the finest French gastronomy.",
                short_description="5 days of museums, monuments and Parisian magic.", duration="5 days"),
        ],
        destinations=[d1], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 2: RUTA POR ITALIA
# ──────────────────────────────────────────────────────────────────────
def _pack_italia() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800",
        {"name": "Roma", "country": "Italia", "description": "La Ciudad Eterna concentra 3.000 anos de historia: el Coliseo, el Vaticano, la Fontana di Trevi y una gastronomia inigualable."},
        {"name": "Rome", "country": "Italy", "description": "The Eternal City packs 3,000 years of history: the Colosseum, the Vatican, the Trevi Fountain and unmatched gastronomy."},
        days=3,
        accs=[
            _make_accommodation(None, "budget", 30, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Bar", "Terraza", "Cocina compartida", "Taquillas"], 4.1,
                "Generator Rome", "Albergue de diseno en un edificio del siglo XIX a 10 minutos de Termini. Ambiente cosmopolita y bar animado.",
                "Generator Rome", "Design hostel in a 19th-century building 10 minutes from Termini. Cosmopolitan vibe and lively bar.",
                booking_url="https://www.booking.com/hotel/it/generator-rome.html", nights=3),
            _make_accommodation(None, "standard", 177, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Desayuno gratuito", "Minibar", "Conserjeria 24h", "Aire acondicionado"], 4.6,
                "Hotel Davanzati", "Hotel boutique de tres estrellas en el centro de Florencia, a 5 minutos del Ponte Vecchio. Desayuno incluido.",
                "Hotel Davanzati", "Three-star boutique hotel in Florence's center, 5 minutes from Ponte Vecchio. Breakfast included.",
                booking_url="https://www.booking.com/hotel/it/davanzati.html", nights=3),
            _make_accommodation(None, "premium", 600, "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800",
                ["WiFi", "Restaurante Terrazza Danieli", "Spa", "Gym", "Gondola privada", "Mayordomo"], 4.9,
                "Hotel Danieli, Venecia", "Palacio veneciano del siglo XIV en primera linea de la laguna, junto al Palacio Ducal. Lujo absoluto.",
                "Hotel Danieli, Venice", "14th-century Venetian palace on the lagoon waterfront, next to the Doge's Palace. Absolute luxury.",
                booking_url="https://www.booking.com/hotel/it/hoteldanielivenice.html", nights=3),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/rome/colosseum-roman-forum-palatine-hill-guided-tour/", 72,
                "https://images.unsplash.com/photo-1626435001540-5ab7bdb97254?w=800", 4.8,
                "Visita guiada al Coliseo, Foro Romano y Palatino", "Explora los tres monumentos mas emblematicos de la Roma imperial con guia y entrada sin colas.", "3 horas",
                "Colosseum, Roman Forum & Palatine guided tour", "Explore the three most iconic monuments of Imperial Rome with a guide and skip-the-line entry.", "3 hours"),
        ],
    )
    d2 = _dest(pk, 1, "https://images.unsplash.com/photo-1640077433514-8bb81960846b?w=800",
        {"name": "Florencia", "country": "Italia", "description": "Cuna del Renacimiento: el Duomo, la Galeria Uffizi, el Ponte Vecchio y los vinedos del Chianti."},
        {"name": "Florence", "country": "Italy", "description": "Cradle of the Renaissance: the Duomo, the Uffizi Gallery, the Ponte Vecchio and the Chianti vineyards."},
        days=3,
        accs=[
            _make_accommodation(None, "budget", 35, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Jardin", "Cocina compartida", "Taquillas"], 4.3,
                "Hostel Archi Rossi", "Albergue en el centro de Florencia, a 250 m de Santa Maria Novella. Jardin y ambiente social.",
                "Hostel Archi Rossi", "Hostel in central Florence, 250 m from Santa Maria Novella station. Garden and social vibe.",
                booking_url="https://www.booking.com/hotel/it/ostello-archi-rossi.html", nights=3),
            _make_accommodation(None, "standard", 180, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Desayuno incluido", "Minibar", "Caja fuerte", "Aire acondicionado"], 4.6,
                "Hotel Spadai", "Hotel boutique de 4 estrellas a pasos del Duomo y Piazza della Repubblica. Desayuno incluido.",
                "Hotel Spadai", "4-star boutique hotel steps from the Duomo and Piazza della Repubblica. Breakfast included.",
                booking_url="https://www.booking.com/hotel/it/hotel-spadai-florence.html", nights=3),
            _make_accommodation(None, "premium", 900, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Spa de dos plantas", "Restaurante Michelin", "Jardines privados", "Piscina", "Mayordomo"], 4.9,
                "Four Seasons Hotel Firenze", "Palazzo renacentista con los jardines privados mas grandes del centro. Spa, restaurante Michelin y suites de lujo.",
                "Four Seasons Hotel Firenze", "Renaissance palazzo with the largest private gardens in the center. Spa, Michelin restaurant and luxury suites.",
                booking_url="https://www.booking.com/hotel/it/four-seasons-firenze.html", nights=3),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/florence-l32/florence-full-day-tuscan-wine-trail-t52419/", 65,
                "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=800", 4.7,
                "Tour enologico por las colinas del Chianti", "Excursion a las colinas del Chianti con visita a dos bodegas, paseo entre vinedos y degustacion de Chianti Classico DOCG.", "5 horas",
                "Chianti Hills wine tour", "Excursion to the Chianti hills visiting two wineries, vineyard walks and Chianti Classico DOCG tasting.", "5 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/florence-l32/florence-cathedral-terraces-and-dome-skip-the-line-tour-t234032/", 45,
                "https://images.unsplash.com/photo-1640077433514-8bb81960846b?w=800", 4.8,
                "Catedral, terrazas y cupula de Brunelleschi", "Visita guiada sin colas a la Catedral, terrazas exclusivas y subida a la cupula de Brunelleschi con vistas panoramicas.", "3 horas",
                "Cathedral, terraces & Brunelleschi's Dome", "Skip-the-line tour of the Cathedral, exclusive terraces and Brunelleschi's Dome climb with panoramic views.", "3 hours"),
        ],
    )
    d3 = _dest(pk, 2, "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800",
        {"name": "Venecia", "country": "Italia", "description": "Construida sobre 118 islas unidas por 400 puentes. Canales, gondolas, la Plaza de San Marcos y el Palacio Ducal."},
        {"name": "Venice", "country": "Italy", "description": "Built on 118 islands connected by 400 bridges. Canals, gondolas, St. Mark's Square and the Doge's Palace."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 40, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Terraza con canal", "Cocina", "Coworking"], 4.2,
                "Combo Venezia", "Albergue con estilo en un monasterio del siglo XII en Cannaregio. Terraza con vistas al canal.",
                "Combo Venezia", "Stylish hostel in a 12th-century monastery in Cannaregio. Canal-view terrace.",
                booking_url="https://www.booking.com/hotel/it/we-crociferi.html", nights=2),
            _make_accommodation(None, "standard", 200, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Desayuno buffet", "Vistas al Gran Canal", "Terraza panoramica"], 4.5,
                "Hotel Canal Grande", "Palacio historico frente al Gran Canal con habitaciones clasicas y terraza panoramica.",
                "Hotel Canal Grande", "Historic palazzo facing the Grand Canal with classic rooms and panoramic terrace.",
                booking_url="https://www.booking.com/hotel/it/canal-grande.html", nights=2),
            _make_accommodation(None, "premium", 700, "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800",
                ["WiFi", "Restaurante Terrazza Danieli", "Spa", "Gym", "Gondola privada", "Mayordomo"], 4.9,
                "Hotel Danieli", "Palazzo gotico del siglo XIV frente a la laguna, junto a San Marcos. Restaurante en la azotea con vistas incomparables.",
                "Hotel Danieli", "14th-century Gothic palazzo on the lagoon, next to St. Mark's. Rooftop restaurant with unmatched views.",
                booking_url="https://www.booking.com/hotel/it/hoteldanielivenice.html", nights=2),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/venice/gondola-canal-tour/", 33,
                "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800", 4.6,
                "Paseo en gondola por los canales de Venecia", "La experiencia mas iconica de Venecia: gondola compartida por canales secretos pasando junto al Teatro La Fenice.", "30 minutos",
                "Gondola ride through Venice canals", "Venice's most iconic experience: shared gondola through secret canals past the Teatro La Fenice.", "30 minutes"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/venice-l35/murano-burano-boat-tour-with-guide-glass-factory-visit-t415014/", 30,
                "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800", 4.7,
                "Excursion a Murano y Burano en barco", "Barco a Murano (demostracion de soplado de vidrio) y Burano (casas de colores y encaje). Guia en vivo.", "5 horas",
                "Murano & Burano boat tour", "Boat to Murano (glassblowing demo) and Burano (colorful houses and lace). Live guide.", "5 hours"),
        ],
    )
    d4 = _dest(pk, 3, "https://images.unsplash.com/photo-1558629173-2b20b2a72ef3?w=800",
        {"name": "Costa Amalfitana", "country": "Italia", "description": "Patrimonio UNESCO. Pueblos de colores sobre acantilados, calas turquesas y la carretera mas bonita del mundo."},
        {"name": "Amalfi Coast", "country": "Italy", "description": "UNESCO Heritage. Colorful villages on cliffs, turquoise coves and what many call the most beautiful road in the world."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 110, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Balcon privado", "Vistas al mar", "Desayuno"], 4.3,
                "Casa Buonocore", "Encantadora casa de huespedes familiar en Positano con balcones y vistas al mar Tirreno.",
                "Casa Buonocore", "Charming family guesthouse in Positano with balconies and Tyrrhenian Sea views.",
                booking_url="https://www.booking.com/hotel/it/casa-buonocore.html", nights=2),
            _make_accommodation(None, "standard", 280, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Piscina infinity", "Playa privada", "Spa", "Terraza panoramica"], 4.6,
                "Hotel Marincanto", "Hotel de 4 estrellas en Positano con piscina infinity, playa privada y vistas al Mediterraneo.",
                "Hotel Marincanto", "4-star hotel in Positano with infinity pool, private beach and Mediterranean views.",
                booking_url="https://www.booking.com/hotel/it/marincanto.html", nights=2),
            _make_accommodation(None, "premium", 1000, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Piscina infinita", "Restaurante La Sponda", "Bar Champagne", "Coleccion de arte"], 4.9,
                "Le Sirenuse", "El hotel mas legendario de la Costa Amalfitana desde 1951. Villa del siglo XVIII con vistas espectaculares.",
                "Le Sirenuse", "The Amalfi Coast's most legendary hotel since 1951. 18th-century villa with spectacular views.",
                booking_url="https://www.booking.com/hotel/it/le-sirenuse.html", nights=2),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/amalfi-l699/amalfi-coast-boat-tour-with-caves-beaches-snorkeling-t468917/", 95,
                "https://images.unsplash.com/photo-1558629173-2b20b2a72ef3?w=800", 4.8,
                "Tour en barco por la Costa Amalfitana", "Navega la costa en grupo reducido: cuevas, playas ocultas, snorkel, parada en Positano. Prosecco y limoncello incluidos.", "6 horas",
                "Amalfi Coast boat tour", "Sail the coast in a small group: caves, hidden beaches, snorkeling, Positano stop. Prosecco and limoncello included.", "6 hours"),
        ],
    )
    # Fix dest_id refs
    for d in [d1, d2, d3, d4]:
        for a in d.accommodations:
            a.destination_id = d.id
        for e in d.experiences:
            e.destination_id = d.id

    dm = {0: d1.id, 1: d2.id, 2: d3.id, 3: d4.id}
    routes = [
        (1, 0, "Llegada a Roma", "Vuelo a Roma. Paseo por Trastevere y primera cena italiana junto al Panteon.", "Arrival in Rome", "Flight to Rome. Stroll through Trastevere and first Italian dinner near the Pantheon."),
        (2, 0, "Coliseo y Vaticano", "Visita guiada al Coliseo, Foro Romano y Palatino. Tarde en los Museos Vaticanos y Capilla Sixtina.", "Colosseum & Vatican", "Guided tour of Colosseum, Roman Forum and Palatine. Afternoon at Vatican Museums and Sistine Chapel."),
        (3, 0, "Roma Barroca y tren a Florencia", "Plaza Navona, Fontana di Trevi y Panteon. Tren Frecciarossa a Florencia (1h30).", "Baroque Rome & train to Florence", "Piazza Navona, Trevi Fountain and Pantheon. Frecciarossa train to Florence (1h30)."),
        (4, 1, "Galeria Uffizi y Ponte Vecchio", "Visita guiada a la Galeria Uffizi. Tarde en el Ponte Vecchio y Palazzo Pitti.", "Uffizi Gallery & Ponte Vecchio", "Guided Uffizi Gallery visit. Afternoon at Ponte Vecchio and Palazzo Pitti."),
        (5, 1, "Tour enologico por el Chianti", "Excursion a las colinas del Chianti: dos bodegas y degustacion de Chianti Classico.", "Chianti wine tour", "Excursion to Chianti hills: two wineries and Chianti Classico tasting."),
        (6, 1, "Cupula del Duomo y tren a Venecia", "Subida a la cupula de Brunelleschi. Tren Frecciarossa a Venecia (2h). Primer paseo en vaporetto.", "Duomo dome & train to Venice", "Climb Brunelleschi's Dome. Frecciarossa train to Venice (2h). First vaporetto ride."),
        (7, 2, "San Marcos y Palacio Ducal", "Piazza San Marco, Basilica y Palacio Ducal. Tarde libre por Cannaregio y Dorsoduro.", "St. Mark's & Doge's Palace", "Piazza San Marco, Basilica and Doge's Palace. Free afternoon in Cannaregio and Dorsoduro."),
        (8, 2, "Gondola y traslado a la Costa Amalfitana", "Paseo en gondola. Tren a Napoles y bus por la SS163 hasta Positano.", "Gondola & transfer to Amalfi Coast", "Gondola ride. Train to Naples and bus along SS163 to Positano."),
        (9, 3, "Tour en barco por la Costa Amalfitana", "Crucero en grupo reducido: cuevas, playas ocultas, snorkel y parada en Positano.", "Amalfi Coast boat tour", "Small group cruise: caves, hidden beaches, snorkeling and Positano stop."),
        (10, 3, "Positano y regreso", "Manana libre en Positano. Traslado al aeropuerto de Napoles.", "Positano & departure", "Free morning in Positano. Transfer to Naples airport."),
    ]
    steps = [_make_route_step(pk, dm[r[1]], r[0], r[2], r[3], r[4], r[5]) for r in routes]

    return Pack(
        id=pk, slug="ruta-por-italia", cover_image="https://images.unsplash.com/photo-1607027187704-5ee3f9bc8854?w=1200",
        duration_days=10, price_from=1200, price_to=5500, price_currency="EUR", featured=True,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Ruta por Italia: Roma, Florencia, Venecia y Amalfi",
                description="Descubre lo mejor de Italia en 10 dias: la grandeza imperial de Roma, el Renacimiento en Florencia, los canales de Venecia y la espectacular Costa Amalfitana.",
                short_description="10 dias de arte, historia, gastronomia y costas de ensueno.", duration="10 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Italy Route: Rome, Florence, Venice & Amalfi",
                description="Discover the best of Italy in 10 days: the imperial grandeur of Rome, the Renaissance in Florence, Venice's canals and the spectacular Amalfi Coast.",
                short_description="10 days of art, history, gastronomy and dream coastlines.", duration="10 days"),
        ],
        destinations=[d1, d2, d3, d4], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 3: MADRID Y BARCELONA
# ──────────────────────────────────────────────────────────────────────
def _pack_espana() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=800",
        {"name": "Madrid", "country": "Espana", "description": "La capital espanola combina museos de talla mundial, palacios reales, tapeo por La Latina y una vida nocturna sin igual."},
        {"name": "Madrid", "country": "Spain", "description": "Spain's capital blends world-class museums, royal palaces, tapas in La Latina and unmatched nightlife."},
        days=3,
        accs=[
            _make_accommodation(None, "budget", 18, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Bar con eventos culturales", "Terraza", "Cocina compartida", "Taquillas"], 4.3,
                "Bastardo Hostel", "Hostel autentico en Chueca-Malasana con bar, eventos culturales semanales y ambiente social muy animado.",
                "Bastardo Hostel", "Authentic hostel in Chueca-Malasana with a bar, weekly cultural events and a lively social atmosphere.",
                booking_url="https://www.booking.com/hotel/es/bastardo-hostel.html", nights=3),
            _make_accommodation(None, "standard", 140, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Balcon", "Minibar gratuito", "Aire acondicionado", "Conserjeria"], 4.5,
                "Hotel Preciados", "Hotel de 4 estrellas en pleno centro de Madrid, a 5 minutos de la Puerta del Sol y el Teatro Real.",
                "Hotel Preciados", "4-star hotel in central Madrid, 5 minutes from Puerta del Sol and Teatro Real.",
                booking_url="https://www.booking.com/hotel/es/hoprevippreciados.html", nights=3),
            _make_accommodation(None, "premium", 750, "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800",
                ["WiFi", "Spa", "Piscina interior", "Restaurante Deesa (1 estrella Michelin)", "Mayordomo 24h"], 4.9,
                "Mandarin Oriental Ritz Madrid", "Palacio Belle Epoque con 153 habitaciones, spa de clase mundial y restaurante Deesa con 1 estrella Michelin del chef Quique Dacosta.",
                "Mandarin Oriental Ritz Madrid", "Belle Epoque palace with 153 rooms, world-class spa and Deesa restaurant with 1 Michelin star by chef Quique Dacosta.",
                booking_url="https://www.booking.com/hotel/es/ritz-madrid.html", nights=3),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/madrid/prado-museum-royal-palace-tour/", 65,
                "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=800", 4.7,
                "Visita guiada al Palacio Real y Museo del Prado", "Combina los dos monumentos mas emblematicos de Madrid en una jornada con guia y entradas sin colas.", "5 horas",
                "Royal Palace & Prado Museum guided tour", "Combine Madrid's two most iconic landmarks in a single day with guide and skip-the-line tickets.", "5 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/madrid-l46/madrid-emociones-live-flamenco-performance-t198766/", 28,
                "https://images.unsplash.com/photo-1518621736915-f3b1c41bfd00?w=800", 4.8,
                "Espectaculo de flamenco en el Teatro Flamenco Madrid", "75 minutos de duende autentico: bailaores de primer nivel, cante jondo y guitarra flamenca en vivo en el barrio de Malasana.", "75 minutos",
                "Flamenco show at Teatro Flamenco Madrid", "75 minutes of authentic duende: top-level dancers, soulful singing and live flamenco guitar in Malasana.", "75 minutes"),
        ],
    )
    d2 = _dest(pk, 1, "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800",
        {"name": "Barcelona", "country": "Espana", "description": "Ciudad mediterranea donde el modernismo de Gaudi convive con playas urbanas, mercados centenarios y gastronomia de vanguardia."},
        {"name": "Barcelona", "country": "Spain", "description": "Mediterranean city where Gaudi's modernism coexists with urban beaches, centuries-old markets and cutting-edge cuisine."},
        days=4,
        accs=[
            _make_accommodation(None, "budget", 25, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Piscina exterior", "Terraza", "Bar", "Cocina compartida", "Taquillas"], 4.3,
                "TOC Hostel Barcelona", "Albergue moderno a pasos de La Rambla. Piscina exterior, terraza y ambiente cosmopolita.",
                "TOC Hostel Barcelona", "Modern hostel steps from La Rambla. Outdoor pool, terrace and cosmopolitan atmosphere.",
                booking_url="https://www.booking.com/hotel/es/toc-hostel-barcelona.html", nights=4),
            _make_accommodation(None, "standard", 110, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Aire acondicionado", "Conserjeria", "Recepcion 24h"], 4.1,
                "Hotel Condado", "Hotel de 3 estrellas en el Eixample, a 5 minutos del Passeig de Gracia. Estilo moderno en edificio tradicional.",
                "Hotel Condado", "3-star hotel in the Eixample, 5 minutes from Passeig de Gracia. Modern style in a traditional building.",
                booking_url="https://www.booking.com/hotel/es/condado.html", nights=4),
            _make_accommodation(None, "premium", 720, "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800",
                ["WiFi", "Spa de lujo", "Piscina en azotea", "Restaurante gourmet", "Bar", "Mayordomo 24h"], 4.9,
                "Mandarin Oriental Barcelona", "Cinco estrellas en el Passeig de Gracia, a 5 minutos de Casa Batllo y La Pedrera. Spa de nivel mundial.",
                "Mandarin Oriental Barcelona", "Five stars on Passeig de Gracia, 5 minutes from Casa Batllo and La Pedrera. World-class spa.",
                booking_url="https://www.booking.com/hotel/es/mandarin-oriental-barcelona.html", nights=4),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/barcelona/guell-park-sagrada-familia-tour/", 79,
                "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800", 4.9,
                "Tour combinado Sagrada Familia y Park Guell", "Visita guiada sin colas a las dos obras maestras de Gaudi. Transporte entre monumentos incluido.", "5 horas",
                "Sagrada Familia & Park Guell combo tour", "Skip-the-line guided tour of Gaudi's two masterpieces. Transport between monuments included.", "5 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/barcelona-l45/barcelona-old-town-and-gothic-quarter-walking-tour-t61664/", 18,
                "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800", 4.6,
                "Tour a pie por el Barrio Gotico", "Explora La Rambla, la Boqueria y los callejones medievales del Barrio Gotico con guia experto.", "2.5 horas",
                "Gothic Quarter walking tour", "Explore La Rambla, Boqueria Market and the medieval alleys of the Gothic Quarter with an expert guide.", "2.5 hours"),
        ],
    )
    for d in [d1, d2]:
        for a in d.accommodations:
            a.destination_id = d.id
        for e in d.experiences:
            e.destination_id = d.id

    dm = {0: d1.id, 1: d2.id}
    routes = [
        (1, 0, "Llegada a Madrid y El Retiro", "Llegada, paseo por El Retiro y primer tapeo en La Latina.", "Arrival in Madrid & Retiro Park", "Arrival, stroll through Retiro Park and first tapas in La Latina."),
        (2, 0, "Palacio Real y Museo del Prado", "Visita guiada al Palacio Real y al Prado. Noche de flamenco.", "Royal Palace & Prado Museum", "Guided tour of Royal Palace and Prado. Evening flamenco show."),
        (3, 0, "Mercado de San Miguel y AVE a Barcelona", "Mercado de San Miguel y barrio de Malasana. AVE a Barcelona (2h30).", "San Miguel Market & AVE to Barcelona", "San Miguel Market and Malasana. AVE train to Barcelona (2h30)."),
        (4, 1, "La Rambla y Barrio Gotico", "Las Ramblas, Mercado de La Boqueria y Barrio Gotico. Tapas en El Born.", "Las Ramblas & Gothic Quarter", "Las Ramblas, La Boqueria market and Gothic Quarter. Tapas in El Born."),
        (5, 1, "Sagrada Familia y Park Guell", "Tour guiado por las obras maestras de Gaudi. Cena en el Eixample.", "Sagrada Familia & Park Guell", "Guided tour of Gaudi's masterpieces. Dinner in Eixample."),
        (6, 1, "Barceloneta y Montjuic", "Playa de Barceloneta y teleferico a Montjuic. Atardecer con vistas al Mediterraneo.", "Barceloneta & Montjuic", "Barceloneta beach and cable car to Montjuic. Sunset with Mediterranean views."),
        (7, 1, "Paseo de Gracia y regreso", "Casa Batllo y Manzana de la Discordia. Ultimas compras y vuelo de regreso.", "Passeig de Gracia & departure", "Casa Batllo and Block of Discord. Last shopping and return flight."),
    ]
    steps = [_make_route_step(pk, dm[r[1]], r[0], r[2], r[3], r[4], r[5]) for r in routes]

    return Pack(
        id=pk, slug="madrid-y-barcelona", cover_image="https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=1200",
        duration_days=7, price_from=650, price_to=4500, price_currency="EUR", featured=True,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Madrid y Barcelona: Lo Mejor de Espana",
                description="Descubre las dos ciudades mas vibrantes de Espana en 7 dias. De la elegancia imperial de Madrid a la creatividad mediterranea de Barcelona.",
                short_description="7 dias de arte, flamenco, Gaudi y gastronomia espanola.", duration="7 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Madrid & Barcelona: The Best of Spain",
                description="Discover Spain's two most vibrant cities in 7 days. From Madrid's imperial elegance to Barcelona's Mediterranean creativity.",
                short_description="7 days of art, flamenco, Gaudi and Spanish gastronomy.", duration="7 days"),
        ],
        destinations=[d1, d2], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 4: ESLOVENIA Y CROACIA
# ──────────────────────────────────────────────────────────────────────
def _pack_eslovenia_croacia() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1568497092899-a4c3e9af9d4c?w=800",
        {"name": "Ljubljana", "country": "Eslovenia", "description": "Capital de cuento con castillo medieval, el rio Ljubljanica y el puente de los Dragones. Capital Verde Europea 2016."},
        {"name": "Ljubljana", "country": "Slovenia", "description": "Fairytale capital with a medieval castle, the Ljubljanica river and the Dragon Bridge. European Green Capital 2016."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 28, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Desayuno incluido", "Cocina", "Jardin con hamacas", "Galeria de arte"], 4.4,
                "Hostel Celica", "Antigua prision militar reconvertida en hostel de diseno. 20 celdas-habitacion diseñadas por artistas diferentes.",
                "Hostel Celica", "Former military prison turned design hostel. 20 cell-rooms each designed by a different artist.",
                booking_url="https://www.booking.com/hotel/si/hostel-celica.html", nights=2),
            _make_accommodation(None, "standard", 145, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Minibar", "Desayuno a la carta", "Recepcion 24h"], 4.7,
                "Hotel Cubo", "Boutique hotel de 4 estrellas en el centro historico, frente a la zona peatonal. 26 habitaciones de diseno contemporaneo.",
                "Hotel Cubo", "4-star boutique hotel in the historic center, facing the pedestrian zone. 26 contemporary design rooms.",
                booking_url="https://www.booking.com/hotel/si/cubo.html", nights=2),
            _make_accommodation(None, "premium", 280, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Spa y piscina interior", "Restaurante fine dining", "Bar panoramico 360", "Gym"], 4.8,
                "InterContinental Ljubljana", "El hotel mas alto de Ljubljana con vistas panoramicas a la ciudad y los Alpes. Spa completo y restaurante de alta cocina.",
                "InterContinental Ljubljana", "Ljubljana's tallest hotel with panoramic views of the city and Alps. Full spa and fine dining restaurant.",
                booking_url="https://www.booking.com/hotel/si/intercontinental-ljubljana.html", nights=2),
        ],
    )
    d2 = _dest(pk, 1, "https://images.unsplash.com/photo-1600983918330-01182b1372d6?w=800",
        {"name": "Lago Bled", "country": "Eslovenia", "description": "Lago glaciar de aguas esmeralda con una isla coronada por una iglesia barroca y un castillo del siglo XI sobre el acantilado."},
        {"name": "Lake Bled", "country": "Slovenia", "description": "Emerald glacial lake with an island crowned by a Baroque church and an 11th-century castle on the clifftop."},
        days=1,
        accs=[
            _make_accommodation(None, "budget", 28, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Jardin", "Bar", "Cocina compartida", "Parking gratuito"], 4.2,
                "Bled Hostel", "Albergue a 7 minutos del Castillo de Bled. Habitaciones familiares con bano privado disponibles.",
                "Bled Hostel", "Hostel 7 minutes from Bled Castle. Family rooms with private bathroom available.",
                booking_url="https://www.booking.com/hotel/si/bled-hostel-bled.html", nights=1),
            _make_accommodation(None, "standard", 100, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Parking gratuito", "Desayuno", "Vistas al lago", "Estilo alpino"], 4.4,
                "Penzion Mayer", "Pension alpina de 3 estrellas con vistas al lago y al castillo. Decoracion tradicional eslovena.",
                "Penzion Mayer", "3-star alpine guesthouse with lake and castle views. Traditional Slovenian decor.",
                booking_url="https://www.booking.com/hotel/si/penzion-mayer.html", nights=1),
            _make_accommodation(None, "premium", 280, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Piscina termal en el lago", "Spa", "Restaurante de autor", "Terraza panoramica"], 4.7,
                "Grand Hotel Toplice", "Hotel de lujo 5 estrellas en la orilla del lago. Piscina termal con acceso directo al lago y vistas a los Alpes Julianos.",
                "Grand Hotel Toplice", "5-star luxury hotel on the lake shore. Thermal pool with direct lake access and Julian Alps views.",
                booking_url="https://www.booking.com/hotel/si/grand-toplice.html", nights=1),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/bled-l1336/from-ljubljana-bled-fairytale-tour-t80526/", 78,
                "https://images.unsplash.com/photo-1600983918330-01182b1372d6?w=800", 4.8,
                "Lago Bled: barca Pletna, isla y castillo", "Excursion desde Ljubljana: barca tradicional Pletna a la isla, campana de los deseos y Castillo de Bled con vistas alpinas.", "6 horas",
                "Lake Bled: Pletna boat, island & castle", "Excursion from Ljubljana: traditional Pletna boat to the island, wishing bell and Bled Castle with Alpine views.", "6 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/bled-l1336/bled-vintgar-gorge-best-experience-and-food-tasting-t704583/", 39,
                "https://images.unsplash.com/photo-1600983918330-01182b1372d6?w=800", 4.7,
                "Desfiladero de Vintgar con degustacion local", "Pasarelas de madera, cascadas y pozas esmeralda. Finaliza con cerveza artesanal y productos locales.", "3 horas",
                "Vintgar Gorge with local tasting", "Wooden boardwalks, waterfalls and emerald pools. Ends with craft beer and local food tasting.", "3 hours"),
        ],
    )
    d3 = _dest(pk, 2, "https://images.unsplash.com/photo-1598384545086-62262b88111f?w=800",
        {"name": "Lagos de Plitvice", "country": "Croacia", "description": "Patrimonio UNESCO. 16 lagos en cascada conectados por travertinos calcareos, pasarelas de madera y barcas electricas."},
        {"name": "Plitvice Lakes", "country": "Croatia", "description": "UNESCO Heritage. 16 cascading lakes connected by limestone travertine, wooden boardwalks and electric boats."},
        days=1,
        accs=[
            _make_accommodation(None, "budget", 22, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Jardin", "Terraza", "Bar", "Shuttle al parque", "Parking gratuito"], 4.5,
                "Falling Lakes Hostel", "El mejor albergue de la zona de Plitvice, en Korenica. Shuttle diario al parque por 3.50 EUR.",
                "Falling Lakes Hostel", "Best hostel in the Plitvice area, in Korenica. Daily park shuttle for 3.50 EUR.",
                booking_url="https://www.booking.com/hotel/hr/falling-lakes-hostel.html", nights=1),
            _make_accommodation(None, "standard", 130, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "2 Restaurantes", "Spa", "Acceso directo al parque", "Parking"], 4.0,
                "Hotel Jezero", "El unico hotel dentro del Parque Nacional, a 300 m del lago Kozjak. Acceso privilegiado a los senderos.",
                "Hotel Jezero", "The only hotel inside the National Park, 300 m from Lake Kozjak. Privileged trail access.",
                booking_url="https://www.booking.com/hotel/hr/jezero.html", nights=1),
            _make_accommodation(None, "premium", 280, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Spa con jacuzzi y sauna", "Gym", "Restaurante mediterraneo", "Terraza"], 4.6,
                "Lakeside Hotel Plitvice", "Hotel de 4 estrellas a 10 minutos del parque. Spa completo con jacuzzi y restaurante mediterraneo.",
                "Lakeside Hotel Plitvice", "4-star hotel 10 minutes from the park. Full spa with hot tub and Mediterranean restaurant.",
                booking_url="https://www.booking.com/hotel/hr/lakeside-plitvice.html", nights=1),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/plitvice-lakes/tour-lagos-plitvice/", 40,
                "https://images.unsplash.com/photo-1598384545086-62262b88111f?w=800", 4.7,
                "Lagos de Plitvice: tour guiado", "Tour guiado de 4 horas por las pasarelas entre los 16 lagos en cascada. Incluye barca electrica y tren panoramico.", "4 horas",
                "Plitvice Lakes: guided tour", "4-hour guided tour along boardwalks between 16 cascading lakes. Includes electric boat and panoramic train.", "4 hours"),
        ],
    )
    d4 = _dest(pk, 3, "https://images.unsplash.com/photo-1515679523025-8d02a8dd20ed?w=800",
        {"name": "Dubrovnik", "country": "Croacia", "description": "La Perla del Adriatico. Ciudad amurallada UNESCO con murallas de 1.940 metros, tejados rojizos y escenario de Juego de Tronos."},
        {"name": "Dubrovnik", "country": "Croatia", "description": "The Pearl of the Adriatic. UNESCO walled city with 1,940-metre walls, red rooftops and Game of Thrones filming location."},
        days=3,
        accs=[
            _make_accommodation(None, "budget", 35, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Cocina compartida", "Salon comun", "Casco antiguo"], 4.1,
                "Old Town Hostel", "Albergue en el corazon del casco antiguo UNESCO de Dubrovnik, a 600 m de la playa Buza.",
                "Old Town Hostel", "Hostel in the heart of Dubrovnik's UNESCO Old Town, 600 m from Buza Beach.",
                booking_url="https://www.booking.com/hotel/hr/old-town-hostel.html", nights=3),
            _make_accommodation(None, "standard", 140, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Restaurante", "Bar", "Terraza", "Parking privado", "Transfer aeropuerto"], 4.2,
                "City Hotel Dubrovnik", "Hotel de 4 estrellas a menos de 1 km de la playa Bellevue. Restaurante con terraza.",
                "City Hotel Dubrovnik", "4-star hotel less than 1 km from Bellevue Beach. Restaurant with terrace.",
                booking_url="https://www.booking.com/hotel/hr/city-dubrovnik.html", nights=3),
            _make_accommodation(None, "premium", 408, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Spa 850 m2", "3 Restaurantes", "Playa privada", "Piscina exterior", "Vistas al Adriatico"], 4.7,
                "Hotel Excelsior Dubrovnik", "Cinco estrellas frente al Adriatico a 5 minutos del casco antiguo. Spa de 850 m2 y playa privada.",
                "Hotel Excelsior Dubrovnik", "Five stars facing the Adriatic, 5 minutes from the Old Town. 850 m2 spa and private beach.",
                booking_url="https://www.booking.com/hotel/hr/hotelexcelsiordubrovnik.html", nights=3),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/dubrovnik-l513/dubrovnik-game-of-thrones-walking-tour-t62077/", 18,
                "https://images.unsplash.com/photo-1515679523025-8d02a8dd20ed?w=800", 4.6,
                "Dubrovnik: tour Juego de Tronos", "Tour a pie de 2 horas por los escenarios de rodaje: Fortaleza de Meereen, callejones de Desembarco del Rey y escalera de la Penitencia.", "2 horas",
                "Dubrovnik: Game of Thrones tour", "2-hour walking tour of filming locations: Meereen Fortress, King's Landing alleys and Walk of Shame staircase.", "2 hours"),
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/dubrovnik/dubrovnik-guided-tour/", 12,
                "https://images.unsplash.com/photo-1515679523025-8d02a8dd20ed?w=800", 4.5,
                "Tour guiado por el casco antiguo", "Recorre el Stradun, Monasterio Franciscano, Palacio del Rector y callejones de Juego de Tronos con guia experto.", "1.5 horas",
                "Old Town guided walking tour", "Walk the Stradun, Franciscan Monastery, Rector's Palace and Game of Thrones alleys with an expert guide.", "1.5 hours"),
        ],
    )
    for d in [d1, d2, d3, d4]:
        for a in d.accommodations:
            a.destination_id = d.id
        for e in d.experiences:
            e.destination_id = d.id

    dm = {0: d1.id, 1: d2.id, 2: d3.id, 3: d4.id}
    routes = [
        (1, 0, "Llegada a Ljubljana", "Llegada y paseo por Plaza Preseren, Puente de los Dragones y terrazas del Ljubljanica.", "Arrival in Ljubljana", "Arrival and walk through Preseren Square, Dragon Bridge and Ljubljanica terraces."),
        (2, 0, "Ljubljana: Castillo y Metelkova", "Mercado Central, subida al Castillo de Ljubljana y barrio bohemio de Metelkova.", "Ljubljana: Castle & Metelkova", "Central Market, Ljubljana Castle ascent and bohemian Metelkova quarter."),
        (3, 1, "Lago Bled", "Bus a Bled (1h15). Barca Pletna, isla, campana de los deseos y Castillo con vistas alpinas.", "Lake Bled", "Bus to Bled (1h15). Pletna boat, island, wishing bell and Castle with Alpine views."),
        (4, 0, "Traslado a Zagreb", "Bus a Zagreb (2h15). Catedral, Torre Lotrscak y Mercado de Dolac.", "Transfer to Zagreb", "Bus to Zagreb (2h15). Cathedral, Lotrscak Tower and Dolac Market."),
        (5, 2, "Lagos de Plitvice", "Tour guiado por los 16 lagos en cascada. Continuacion en bus hacia Dubrovnik.", "Plitvice Lakes", "Guided tour of the 16 cascading lakes. Onward bus to Dubrovnik."),
        (6, 3, "Dubrovnik: Murallas", "Paseo por las murallas medievales (1,94 km). Casco antiguo: Stradun y Catedral.", "Dubrovnik: City Walls", "Walk along medieval walls (1.94 km). Old Town: Stradun and Cathedral."),
        (7, 3, "Tour Juego de Tronos y Lokrum", "Tour por escenarios de Juego de Tronos. Ferry a isla de Lokrum.", "Game of Thrones tour & Lokrum", "Tour of Game of Thrones locations. Ferry to Lokrum island."),
        (8, 3, "Despedida del Adriatico", "Manana libre en playa de Banje. Traslado al aeropuerto de Dubrovnik.", "Farewell to the Adriatic", "Free morning at Banje beach. Transfer to Dubrovnik airport."),
    ]
    steps = [_make_route_step(pk, dm[r[1]], r[0], r[2], r[3], r[4], r[5]) for r in routes]

    return Pack(
        id=pk, slug="eslovenia-y-croacia", cover_image="https://images.unsplash.com/photo-1600983918330-01182b1372d6?w=1200",
        duration_days=8, price_from=1290, price_to=4800, price_currency="EUR", featured=False,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Eslovenia y Croacia: de los Alpes al Adriatico",
                description="Un viaje de contrastes: castillos de Ljubljana, el Lago Bled, las cascadas de Plitvice y las murallas medievales de Dubrovnik sobre el Adriatico.",
                short_description="8 dias entre lagos alpinos, cascadas UNESCO y ciudades medievales.", duration="8 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Slovenia & Croatia: From the Alps to the Adriatic",
                description="A journey of contrasts: Ljubljana's castles, Lake Bled, Plitvice waterfalls and Dubrovnik's medieval walls above the Adriatic.",
                short_description="8 days of Alpine lakes, UNESCO waterfalls and medieval cities.", duration="8 days"),
        ],
        destinations=[d1, d2, d3, d4], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 5: JAPON ESENCIAL
# ──────────────────────────────────────────────────────────────────────
def _pack_japon() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800",
        {"name": "Tokio", "country": "Japon", "description": "La megalopolis mas poblada del mundo combina tradicion y vanguardia: mercados, barrios de manga, santuarios entre rascacielos y mas estrellas Michelin que ninguna otra ciudad."},
        {"name": "Tokyo", "country": "Japan", "description": "The world's most populous megalopolis blends tradition and innovation: markets, manga districts, shrines between skyscrapers and more Michelin stars than any other city."},
        days=5,
        accs=[
            _make_accommodation(None, "budget", 29, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Ducha privada", "Taquilla personal", "TV integrada", "Pijama de cortesia"], 4.2,
                "9h Nine Hours Shinjuku", "El hotel capsula mas elegante de Tokio. Capsulas minimalistas con iluminacion gradual y experiencia de sueno optimizada.",
                "9h Nine Hours Shinjuku", "Tokyo's most elegant capsule hotel. Minimalist capsules with gradual lighting and optimized sleep experience.",
                booking_url="https://www.booking.com/hotel/jp/nainawazuumanxin-su.html", nights=5),
            _make_accommodation(None, "standard", 89, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Rooftop bar", "Colchones Simmons", "Club lounge", "Restaurante"], 4.5,
                "Shinjuku Granbell Hotel", "Hotel boutique de diseno en el corazon de Shinjuku, a 3 minutos de la estacion JR. Rooftop bar con vistas panoramicas.",
                "Shinjuku Granbell Hotel", "Design boutique hotel in the heart of Shinjuku, 3 minutes from JR station. Rooftop bar with panoramic views.",
                booking_url="https://www.booking.com/hotel/jp/shinjuku-granbell.html", nights=5),
            _make_accommodation(None, "premium", 780, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Piscina planta 47", "Spa", "New York Bar (planta 52)", "Biblioteca", "Mayordomo"], 4.9,
                "Park Hyatt Tokyo", "El hotel de 'Lost in Translation'. Pisos 39-52 del Shinjuku Park Tower con vistas panoramicas. New York Bar en la planta 52.",
                "Park Hyatt Tokyo", "The 'Lost in Translation' hotel. Floors 39-52 of Shinjuku Park Tower with panoramic views. New York Bar on floor 52.",
                booking_url="https://www.booking.com/hotel/jp/park-hyatt-tokyo.html", nights=5),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/tokyo-l193/tokyo-akihabara-shibuya-karaoke-city-lights-night-tour-t862575/", 65,
                "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=800", 4.8,
                "Tour nocturno: Akihabara, Shibuya y karaoke", "4 horas explorando el Tokio de los neones: Akihabara, el cruce de Shibuya y sesion de karaoke en Shinjuku.", "4 horas",
                "Night tour: Akihabara, Shibuya & karaoke", "4 hours exploring neon Tokyo: Akihabara, Shibuya Crossing and karaoke session in Shinjuku.", "4 hours"),
        ],
    )
    d2 = _dest(pk, 1, "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800",
        {"name": "Kioto", "country": "Japon", "description": "Antigua capital imperial con mas de 1.600 templos, jardines zen, el barrio de geishas de Gion y los torii naranjas de Fushimi Inari."},
        {"name": "Kyoto", "country": "Japan", "description": "Ancient imperial capital with over 1,600 temples, Zen gardens, the Gion geisha district and Fushimi Inari's orange torii gates."},
        days=4,
        accs=[
            _make_accommodation(None, "budget", 25, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Zona comun", "Cerca del castillo Nijo"], 4.2,
                "Capsule Hotel Continue Nijo", "Capsula moderna en el centro de Kioto, junto al castillo Nijo. WiFi gratuito y excelente relacion calidad-precio.",
                "Capsule Hotel Continue Nijo", "Modern capsule in central Kyoto, next to Nijo Castle. Free WiFi and excellent value.",
                booking_url="https://www.booking.com/hotel/jp/continue-nijojo-kita.html", nights=4),
            _make_accommodation(None, "standard", 110, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Arquitectura kyotense", "Ubicacion centrica", "Aire acondicionado"], 4.5,
                "Cross Hotel Kyoto", "Hotel de diseno con arquitectura kyotense en Kawaramachi Sanjo. Ubicacion centrica privilegiada.",
                "Cross Hotel Kyoto", "Design hotel with Kyoto-style architecture in Kawaramachi Sanjo. Prime central location.",
                booking_url="https://www.booking.com/hotel/jp/cross-hotel-kyoto.html", nights=4),
            _make_accommodation(None, "premium", 420, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Spa de aguas termales", "Restaurante", "Jardin japones", "Mayordomo"], 4.9,
                "Hotel The Mitsui Kyoto", "Hotel de lujo 5 estrellas con spa de aguas termales minerales en el corazon historico de Kioto.",
                "Hotel The Mitsui Kyoto", "5-star luxury hotel with mineral hot spring spa in the historic heart of Kyoto.",
                booking_url="https://www.booking.com/hotel/jp/the-mitsui-kyoto-a-luxury-collection-spa.html", nights=4),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/kyoto/fushimi-inari-hike/", 42,
                "https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=800", 4.9,
                "Senderismo Fushimi Inari + ceremonia del te en Gion", "Trek guiado de 5 km entre miles de torii naranjas. Ceremonia del te tradicional con kimono en Gion.", "5 horas",
                "Fushimi Inari hike + tea ceremony in Gion", "Guided 5 km trek through thousands of orange torii gates. Traditional tea ceremony with kimono in Gion.", "5 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/kyoto-l96826/arashiyama-bamboo-forest-bike-tour-early-bird-t444196/", 38,
                "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800", 4.8,
                "Arashiyama en bici: bosque de bambu al amanecer", "Tour matutino en bici por el bosque de bambu, puente Togetsukyo y templo Tenryuji antes de las multitudes.", "3 horas",
                "Arashiyama by bike: bamboo forest at dawn", "Early morning bike tour through bamboo grove, Togetsukyo Bridge and Tenryuji Temple before the crowds.", "3 hours"),
        ],
    )
    d3 = _dest(pk, 2, "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800",
        {"name": "Osaka", "country": "Japon", "description": "La capital gastronomica de Japon: Dotonbori con sus neones, el castillo imperial, Shinsekai y la mejor comida callejera del pais."},
        {"name": "Osaka", "country": "Japan", "description": "Japan's culinary capital: Dotonbori with its neon signs, the imperial castle, Shinsekai and the country's best street food."},
        days=3,
        accs=[
            _make_accommodation(None, "budget", 28, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Cocina", "Lavadora", "Aire acondicionado", "Namba"], 4.2,
                "Acro Capsule Hotel Namba", "Capsula adults-only en Namba con cocina propia y lavadora. Ubicacion inmejorable junto a Dotonbori.",
                "Acro Capsule Hotel Namba", "Adults-only capsule in Namba with kitchenette and washing machine. Unbeatable location next to Dotonbori.",
                booking_url="https://www.booking.com/hotel/jp/acro-capsule-namba-dotonbori.html", nights=3),
            _make_accommodation(None, "standard", 145, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Restaurante", "Bar", "Gym", "Parking privado"], 4.5,
                "The Osaka Station Hotel", "Hotel 4 estrellas en Umeda con restaurante, bar y gimnasio. Elegancia urbana en el distrito de negocios.",
                "The Osaka Station Hotel", "4-star hotel in Umeda with restaurant, bar and fitness center. Urban elegance in the business district.",
                booking_url="https://www.booking.com/hotel/jp/new-osaka.html", nights=3),
            _make_accommodation(None, "premium", 370, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Spa", "Piscina interior", "Terraza", "Restaurante", "Bar", "Diseno vanguardista"], 4.8,
                "W Osaka", "Hotel de lujo 5 estrellas en Shinsaibashi. Spa, piscina interior y diseno vanguardista con vistas a la ciudad.",
                "W Osaka", "5-star luxury hotel in Shinsaibashi. Spa, indoor pool and cutting-edge design with city views.",
                booking_url="https://www.booking.com/hotel/jp/w-osaka.html", nights=3),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/osaka-l1204/osaka-2-hour-kuromon-market-walking-street-food-tour-t329176/", 45,
                "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800", 4.9,
                "Tour gastronomico: Mercado Kuromon y calles de Osaka", "2 horas, 6 paradas y 6 degustaciones: takoyaki, okonomiyaki, kushikatsu, gyoza y sake local.", "2 horas",
                "Food tour: Kuromon Market & Osaka streets", "2 hours, 6 stops and 6 tastings: takoyaki, okonomiyaki, kushikatsu, gyoza and local sake.", "2 hours"),
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/osaka/osaka-food-tour/", 34,
                "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800", 4.7,
                "Tour nocturno gastronomico por Dotonbori y Namba", "Recorrido nocturno descubriendo takoyaki, okonomiyaki y otras especialidades en los mejores puestos.", "2.5 horas",
                "Dotonbori & Namba night food tour", "Night walking tour discovering takoyaki, okonomiyaki and other specialties at the best stalls.", "2.5 hours"),
        ],
    )
    for d in [d1, d2, d3]:
        for a in d.accommodations:
            a.destination_id = d.id
        for e in d.experiences:
            e.destination_id = d.id

    dm = {0: d1.id, 1: d2.id, 2: d3.id}
    routes = [
        (1, 0, "Llegada a Tokio", "Llegada a Narita/Haneda. Transfer a Shinjuku. Primer paseo e izakaya.", "Arrival in Tokyo", "Arrive at Narita/Haneda. Transfer to Shinjuku. First walk and izakaya dinner."),
        (2, 0, "Harajuku, Shibuya y Meiji-jingu", "Santuario Meiji, Takeshita Street, cruce de Shibuya y Shibuya Sky.", "Harajuku, Shibuya & Meiji Shrine", "Meiji Shrine, Takeshita Street, Shibuya Crossing and Shibuya Sky."),
        (3, 0, "Akihabara y tour nocturno", "Asakusa y Senso-ji. Tour nocturno: Akihabara, Shibuya y karaoke.", "Akihabara & night tour", "Asakusa and Senso-ji. Night tour: Akihabara, Shibuya and karaoke."),
        (4, 0, "Tsukiji, Odaiba y Yanaka", "Mercado de Tsukiji. teamLab Borderless en Odaiba. Barrio historico de Yanaka.", "Tsukiji, Odaiba & Yanaka", "Tsukiji Market. teamLab Borderless in Odaiba. Historic Yanaka neighborhood."),
        (5, 0, "Ueno y Shinkansen a Kioto", "Parque de Ueno. Shinkansen Nozomi a Kioto (2h15). Cena en Nishiki Market.", "Ueno & Shinkansen to Kyoto", "Ueno Park. Nozomi Shinkansen to Kyoto (2h15). Dinner at Nishiki Market."),
        (6, 1, "Fushimi Inari y ceremonia del te", "Amanecer en Fushimi Inari (5 km entre torii). Ceremonia del te en Gion.", "Fushimi Inari & tea ceremony", "Sunrise at Fushimi Inari (5 km through torii). Tea ceremony in Gion."),
        (7, 1, "Arashiyama y Kinkaku-ji", "Bosque de bambu, puente Togetsukyo y Tenryu-ji. Pabellon de Oro y Ryoan-ji.", "Arashiyama & Kinkaku-ji", "Bamboo grove, Togetsukyo bridge and Tenryu-ji. Golden Pavilion and Ryoan-ji."),
        (8, 1, "Kiyomizudera y excursion a Nara", "Templo Kiyomizudera. Excursion a Nara: ciervos sagrados y Gran Buda del Todai-ji.", "Kiyomizudera & Nara day trip", "Kiyomizudera temple. Day trip to Nara: sacred deer and Todai-ji Great Buddha."),
        (9, 1, "Dia libre y traslado a Osaka", "Nishiki Market. Tren a Osaka (30 min). Primer paseo por Dotonbori.", "Free day & transfer to Osaka", "Nishiki Market. Train to Osaka (30 min). First stroll through Dotonbori."),
        (10, 2, "Mercado Kuromon y tour gastronomico", "Mercado Kuromon Ichiba. Tour de 6 degustaciones por Osaka.", "Kuromon Market & food tour", "Kuromon Ichiba Market. 6-tasting food tour through Osaka."),
        (11, 2, "Castillo de Osaka y Shinsekai", "Castillo de Osaka (museo de 8 plantas). Barrio retro de Shinsekai. Cena en Namba.", "Osaka Castle & Shinsekai", "Osaka Castle (8-floor museum). Retro Shinsekai district. Dinner in Namba."),
        (12, 2, "Regreso", "Manana libre. Transfer al aeropuerto de Kansai.", "Departure", "Free morning. Transfer to Kansai airport."),
    ]
    steps = [_make_route_step(pk, dm[r[1]], r[0], r[2], r[3], r[4], r[5]) for r in routes]

    return Pack(
        id=pk, slug="japon-esencial", cover_image="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200",
        duration_days=12, price_from=1890, price_to=7500, price_currency="EUR", featured=True,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Japon Esencial: Tokio, Kioto y Osaka",
                description="Un viaje completo por el Japon moderno y tradicional. Rascacielos de Shinjuku, torii de Fushimi Inari y el caos gastronomico de Dotonbori.",
                short_description="12 dias entre templos, tecnologia y la mejor gastronomia del mundo.", duration="12 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Essential Japan: Tokyo, Kyoto & Osaka",
                description="A complete journey through modern and traditional Japan. Shinjuku skyscrapers, Fushimi Inari torii and Dotonbori's gastronomic chaos.",
                short_description="12 days of temples, technology and the world's best gastronomy.", duration="12 days"),
        ],
        destinations=[d1, d2, d3], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 6: LONDRES
# ──────────────────────────────────────────────────────────────────────
def _pack_londres() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1529655683826-aba9b3e77383?w=800",
        {"name": "Londres", "country": "Reino Unido", "description": "Siglos de historia con palacios y torres medievales, museos gratuitos de clase mundial, y una de las noches mas vibrantes de Europa."},
        {"name": "London", "country": "United Kingdom", "description": "Centuries of history with palaces and medieval towers, free world-class museums, and one of Europe's most vibrant nightlife scenes."},
        days=5,
        accs=[
            _make_accommodation(None, "budget", 28, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Bar con DJ y karaoke", "Sala de juegos", "Lavanderia", "Recepcion 24h"], 4.2,
                "Generator London", "Hostel de referencia en Bloomsbury, junto al Museo Britanico. Bar con noches tematicas, ideal para conocer gente.",
                "Generator London", "Go-to hostel in Bloomsbury, next to the British Museum. Bar with themed nights, perfect for meeting people.",
                booking_url="https://www.booking.com/hotel/gb/thegenerator.html", nights=5),
            _make_accommodation(None, "standard", 165, "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800",
                ["WiFi", "Cama XL king", "Tablet de control", "Rooftop bar planta 9", "Canteen 24h"], 4.6,
                "citizenM Tower of London", "Hotel urbano con vistas a la Torre de Londres y Tower Bridge. Habitaciones inteligentes y rooftop bar con vistas 360.",
                "citizenM Tower of London", "Urban hotel with views of the Tower of London and Tower Bridge. Smart rooms and rooftop bar with 360 views.",
                booking_url="https://www.booking.com/hotel/gb/citizenm-tower-of-london-london.html", nights=5),
            _make_accommodation(None, "premium", 820, "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800",
                ["WiFi", "American Bar (el mas antiguo del UK)", "Savoy Grill", "Piscina interior", "Spa", "Mayordomo"], 4.9,
                "The Savoy London", "Desde 1889, sinonimo de lujo absoluto. Habitaciones eduardianas y art deco junto al Tamesis. El legendario American Bar.",
                "The Savoy London", "Since 1889, synonymous with absolute luxury. Edwardian and Art Deco rooms by the Thames. The legendary American Bar.",
                booking_url="https://www.booking.com/hotel/gb/the-savoy.html", nights=5),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/london/thames-cruise-westminster-tower-bridge/", 45,
                "https://images.unsplash.com/photo-1526129318478-62ed807ebdf9?w=800", 4.7,
                "Torre de Londres y crucero por el Tamesis", "Visita a la Torre de Londres (Joyas de la Corona y Beefeaters) mas crucero escenico de Westminster a Tower Bridge.", "4 horas",
                "Tower of London & Thames cruise", "Tower of London visit (Crown Jewels and Beefeaters) plus scenic cruise from Westminster to Tower Bridge.", "4 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/london-l57/london-harry-potter-warner-bros-studio-tour-with-transfers-t505308/", 120,
                "https://images.unsplash.com/photo-1551269901-5c5e14c25df7?w=800", 4.9,
                "Estudios de Harry Potter en Warner Bros.", "Tour completo de los estudios donde se rodaron las 8 peliculas. Gran Salon de Hogwarts, Callejon Diagon y Mantequilla de Cerveza.", "7 horas",
                "Harry Potter Warner Bros. Studio Tour", "Complete studio tour where all 8 films were made. Great Hall of Hogwarts, Diagon Alley and Butterbeer.", "7 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/london-l57/london-buckingham-palace-westminster-guided-walking-tour-t1095224/", 25,
                "https://images.unsplash.com/photo-1520986606214-8b456906c813?w=800", 4.6,
                "Tour a pie por Westminster y Buckingham", "Tour en grupo reducido: Buckingham, Cambio de Guardia, Trafalgar Square, Downing Street, Big Ben y Abadia de Westminster.", "2.5 horas",
                "Westminster & Buckingham walking tour", "Small group tour: Buckingham, Changing of the Guard, Trafalgar Square, Downing Street, Big Ben and Westminster Abbey.", "2.5 hours"),
        ],
    )
    for a in d1.accommodations:
        a.destination_id = d1.id
    for e in d1.experiences:
        e.destination_id = d1.id

    routes = [
        (1, "Llegada y Westminster", "Big Ben, Abadia de Westminster, Palacio de Buckingham y St. James's Park.", "Arrival & Westminster", "Big Ben, Westminster Abbey, Buckingham Palace and St. James's Park."),
        (2, "Torre de Londres y Tamesis", "Torre de Londres y Joyas de la Corona. Crucero por el Tamesis. Borough Market.", "Tower of London & Thames", "Tower of London and Crown Jewels. Thames cruise. Borough Market."),
        (3, "Harry Potter Studios", "Dia completo en los Estudios Warner Bros. Gran Salon de Hogwarts y Callejon Diagon.", "Harry Potter Studios", "Full day at Warner Bros. Studios. Great Hall of Hogwarts and Diagon Alley."),
        (4, "Museos y Camden Town", "Museo Britanico, Tate Modern, Globe Theatre. Tarde en Camden Town.", "Museums & Camden Town", "British Museum, Tate Modern, Globe Theatre. Afternoon in Camden Town."),
        (5, "Notting Hill y despedida", "Notting Hill, Portobello Market y Hyde Park. London Eye opcional.", "Notting Hill & farewell", "Notting Hill, Portobello Market and Hyde Park. Optional London Eye."),
    ]
    steps = [_make_route_step(pk, d1.id, r[0], r[1], r[2], r[3], r[4]) for r in routes]

    return Pack(
        id=pk, slug="londres-ciudad-imperial", cover_image="https://images.unsplash.com/photo-1522358461163-fcc21d170a26?w=1200",
        duration_days=5, price_from=520, price_to=4500, price_currency="EUR", featured=False,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Londres: Ciudad Imperial",
                description="Palacios reales, la Torre de Londres, el Tamesis, los estudios de Harry Potter y una vibrante escena cultural en la capital britanica.",
                short_description="5 dias de historia, museos, Harry Potter y pubs britanicos.", duration="5 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="London: Imperial City",
                description="Royal palaces, the Tower of London, the Thames, Harry Potter studios and a vibrant cultural scene in the British capital.",
                short_description="5 days of history, museums, Harry Potter and British pubs.", duration="5 days"),
        ],
        destinations=[d1], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 7: FIORDOS NORUEGOS
# ──────────────────────────────────────────────────────────────────────
def _pack_noruega() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800",
        {"name": "Bergen", "country": "Noruega", "description": "La Puerta de los Fiordos. Barrio historico de Bryggen (UNESCO), funicular Floibanen y mercado de pescado."},
        {"name": "Bergen", "country": "Norway", "description": "The Gateway to the Fjords. Historic Bryggen wharf (UNESCO), Floibanen funicular and fish market."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 28, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Desayuno buffet incluido", "Cocina", "BBQ exterior", "Senderismo desde el hostel"], 4.3,
                "HI Bergen Hostel Montana", "Hostel en la ladera del monte Ulriken con desayuno libre, rutas de senderismo y parking gratuito.",
                "HI Bergen Hostel Montana", "Hostel on the slopes of Mount Ulriken with all-you-can-eat breakfast, hiking trails and free parking.",
                booking_url="https://www.booking.com/hotel/no/bergen-hostel-montana.html", nights=2),
            _make_accommodation(None, "standard", 130, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Vistas al puerto", "Desayuno", "Bar de whisky", "Gym gratuito"], 4.5,
                "Scandic Torget Bergen", "Hotel de 4 estrellas con vistas panoramicas al puerto y al mercado de pescado. Ubicacion privilegiada junto a Bryggen.",
                "Scandic Torget Bergen", "4-star hotel with panoramic harbour and fish market views. Prime location next to Bryggen.",
                booking_url="https://www.booking.com/hotel/no/scandic-torget.html", nights=2),
            _make_accommodation(None, "premium", 350, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Restaurante fine dining", "Coleccion de arte", "Hora social", "Espresso en habitacion"], 4.9,
                "Opus XVI", "Hotel boutique de 5 estrellas en un edificio de 1876. Habitaciones de diseno unico, restaurante con musica en vivo y coleccion de arte curada.",
                "Opus XVI", "5-star boutique hotel in an 1876 building. Uniquely designed rooms, restaurant with live music and curated art collection.",
                booking_url="https://www.booking.com/hotel/no/opus-xvi.html", nights=2),
        ],
    )
    d2 = _dest(pk, 1, "https://images.unsplash.com/photo-1601581875309-fafbf2d3ed3a?w=800",
        {"name": "Geirangerfjord", "country": "Noruega", "description": "Patrimonio UNESCO. Paredes de roca de 1.400 m y las cascadas de las Siete Hermanas, el Velo de Novia y El Pretendiente."},
        {"name": "Geirangerfjord", "country": "Norway", "description": "UNESCO Heritage. 1,400 m rock walls and the Seven Sisters, Bridal Veil and Suitor waterfalls."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 115, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Balcones privados", "Vistas al fiordo", "Restaurante", "Desayuno buffet"], 4.3,
                "Grande Fjord Hotel", "Hotel con encanto a orillas del fiordo con balcones privados y vistas panoramicas.",
                "Grande Fjord Hotel", "Charming hotel by the fjord with private balconies and panoramic views.",
                booking_url="https://www.booking.com/hotel/no/grande-fjord.html", nights=2),
            _make_accommodation(None, "standard", 190, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Vistas al fiordo", "Cocina noruega", "Parking gratuito"], 4.5,
                "Hotel Utsikten", "Hotel historico de 1893 con vistas de infarto sobre el Geirangerfjord. Cocina noruega tradicional.",
                "Hotel Utsikten", "Historic 1893 hotel with breathtaking Geirangerfjord views. Traditional Norwegian cuisine.",
                booking_url="https://www.booking.com/hotel/no/utsikten.html", nights=2),
            _make_accommodation(None, "premium", 175, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Spa completo", "Piscina", "Jardin en azotea", "Minibar", "Vistas al fiordo"], 4.7,
                "Hotel Union Geiranger", "El gran hotel clasico del fiordo con spa completo, piscina y vistas directas al fiordo UNESCO.",
                "Hotel Union Geiranger", "The fjord's grand classic hotel with full spa, pool and direct UNESCO fjord views.",
                booking_url="https://www.booking.com/hotel/no/union.html", nights=2),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/geiranger-l4560/geiranger-fjord-and-waterfalls-sightseeing-boat-trip-t637010/", 50,
                "https://images.unsplash.com/photo-1601581875309-fafbf2d3ed3a?w=800", 4.8,
                "Crucero por el Geirangerfjord UNESCO", "Crucero de 90 minutos en barco electrico entre paredes de 1.400 m. Cascadas de las Siete Hermanas y Velo de Novia.", "90 minutos",
                "Geirangerfjord UNESCO cruise", "90-minute electric boat cruise between 1,400 m rock walls. Seven Sisters and Bridal Veil waterfalls.", "90 minutes"),
        ],
    )
    d3 = _dest(pk, 2, "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        {"name": "Flam", "country": "Noruega", "description": "El tren Flamsbana, uno de los viajes en tren mas bellos del mundo: 864 m de desnivel, 20 tuneles y la cascada Kjosfossen."},
        {"name": "Flam", "country": "Norway", "description": "The Flamsbana railway, one of the world's most beautiful train journeys: 864 m elevation, 20 tunnels and Kjosfossen waterfall."},
        days=1,
        accs=[
            _make_accommodation(None, "budget", 150, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Cocina equipada", "Terraza privada", "Vistas al Sognefjord"], 4.2,
                "Flam Marina & Apartments", "Apartamentos junto a la marina con vistas al Sognefjord. Cocina equipada y terraza privada.",
                "Flam Marina & Apartments", "Waterfront apartments with Sognefjord views. Fully equipped kitchen and private terrace.",
                booking_url="https://www.booking.com/hotel/no/flam-marina-apartments.html", nights=1),
            _make_accommodation(None, "standard", 195, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Cerveza artesanal propia", "Restaurante", "Kayak", "Senderismo guiado"], 4.5,
                "Flamsbrygga Hotel", "Hotel boutique a 100 m de la estacion de Flam. Cerveza artesanal propia y actividades de fiordo.",
                "Flamsbrygga Hotel", "Boutique hotel 100 m from Flam station. House-brewed beer and fjord activities.",
                booking_url="https://www.booking.com/hotel/no/flamsbrygga-hotell.html", nights=1),
            _make_accommodation(None, "premium", 255, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Restaurante ecologico", "Jardin", "Vistas al fiordo", "Edificio historico siglo XIX"], 4.7,
                "Fretheim Hotel", "Mansion restaurada del siglo XIX a orillas del Aurlandsfjord. Restaurante con cocina noruega ecologica.",
                "Fretheim Hotel", "Restored 19th-century manor on the Aurlandsfjord. Restaurant with organic Norwegian cuisine.",
                booking_url="https://www.booking.com/hotel/no/fretheim.html", nights=1),
        ],
        exps=[
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/bergen/fjords-flam-train-naeroy-boat-ride/", 145,
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", 4.9,
                "Flamsbana + crucero por el Naeroyfjord", "Tren Flamsbana (864 m en 20 km, parada en cascada Kjosfossen) y crucero de 2 horas por el Naeroyfjord UNESCO.", "10.5 horas",
                "Flamsbana + Naeroyfjord cruise", "Flamsbana train (864 m over 20 km, Kjosfossen waterfall stop) and 2-hour cruise on UNESCO Naeroyfjord.", "10.5 hours"),
        ],
    )
    d4 = _dest(pk, 3, "https://images.unsplash.com/photo-1554844428-1c9b6199f1be?w=800",
        {"name": "Stavanger", "country": "Noruega", "description": "Puerta al Preikestolen (604 m sobre el Lysefjord). Casco antiguo de casas blancas de madera y excelentes restaurantes de marisco."},
        {"name": "Stavanger", "country": "Norway", "description": "Gateway to Preikestolen (604 m above the Lysefjord). Old town of white wooden houses and excellent seafood restaurants."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 85, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Parking gratuito", "TV", "Cerca de la estacion"], 4.0,
                "Stavanger Bed & Breakfast", "Alojamiento economico a 5 minutos de la estacion de tren. WiFi y parking gratuitos.",
                "Stavanger Bed & Breakfast", "Budget accommodation 5 minutes from the train station. Free WiFi and parking.",
                booking_url="https://www.booking.com/hotel/no/stavanger-bed.html", nights=2),
            _make_accommodation(None, "standard", 120, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Desayuno buffet organico", "Vistas al lago Breiavatnet", "Centro de Stavanger"], 4.4,
                "Thon Hotel Maritim", "Hotel 4 estrellas junto al lago Breiavatnet. Desayuno buffet organico y ubicacion centrica.",
                "Thon Hotel Maritim", "4-star hotel by Lake Breiavatnet. Organic breakfast buffet and central location.",
                booking_url="https://www.booking.com/hotel/no/thon-bristol-maritim.html", nights=2),
            _make_accommodation(None, "premium", 155, "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
                ["WiFi", "Gym y sauna en ultimo piso", "Vistas al fiordo", "Ecologico certificado"], 4.6,
                "Radisson Blu Atlantic Stavanger", "Hotel de lujo ecologico con gimnasio y sauna en el ultimo piso con vistas al fiordo y la ciudad.",
                "Radisson Blu Atlantic Stavanger", "Eco-certified luxury hotel with top-floor gym and sauna with fjord and city views.",
                booking_url="https://www.booking.com/hotel/no/radisson-blu-atlantic-stavanger.html", nights=2),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/stavanger-l4561/from-stavanger-preikestolen-pulpit-rock-guided-hike-t181709/", 150,
                "https://images.unsplash.com/photo-1554844428-1c9b6199f1be?w=800", 4.9,
                "Senderismo al Preikestolen (Pulpit Rock)", "Caminata guiada de 8 km hasta la plataforma de 604 m sobre el Lysefjord. Una de las vistas mas impresionantes de Europa.", "7 horas",
                "Preikestolen (Pulpit Rock) guided hike", "Guided 8 km hike to the 604 m platform above the Lysefjord. One of Europe's most breathtaking views.", "7 hours"),
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/stavanger-l4561/stavanger-fjord-cruise-to-lysefjord-and-pulpit-rock-t883662/", 72,
                "https://images.unsplash.com/photo-1554844428-1c9b6199f1be?w=800", 4.7,
                "Crucero por el Lysefjord hasta Preikestolen", "Crucero desde el puerto de Stavanger por el Lysefjord. Cascada Whiskey Falls y vistas a Preikestolen desde abajo.", "2.5 horas",
                "Lysefjord cruise to Pulpit Rock", "Cruise from Stavanger harbour through the Lysefjord. Whiskey Waterfall and views of Preikestolen from below.", "2.5 hours"),
        ],
    )
    for d in [d1, d2, d3, d4]:
        for a in d.accommodations:
            a.destination_id = d.id
        for e in d.experiences:
            e.destination_id = d.id

    dm = {0: d1.id, 1: d2.id, 2: d3.id, 3: d4.id}
    routes = [
        (1, 0, "Llegada a Bergen", "Llegada y paseo por Bryggen. Mercado de Pescado y primera cena de marisco.", "Arrival in Bergen", "Arrival and Bryggen stroll. Fish Market and first seafood dinner."),
        (2, 0, "Monte Floyen y Bryggen", "Funicular Floibanen al monte Floyen (320 m). Museo Hanseatico y artesania local.", "Mount Floyen & Bryggen", "Floibanen funicular to Mount Floyen (320 m). Hanseatic Museum and local crafts."),
        (3, 1, "Bergen a Geirangerfjord", "Ruta por paisajes alpinos via Trollstigen o la Carretera del Aguila hasta Geiranger.", "Bergen to Geirangerfjord", "Drive through alpine scenery via Trollstigen or Eagle Road to Geiranger."),
        (4, 1, "Crucero Geirangerfjord y traslado a Flam", "Crucero UNESCO de 90 minutos. Traslado escenico a Flam.", "Geirangerfjord cruise & transfer to Flam", "90-minute UNESCO cruise. Scenic transfer to Flam."),
        (5, 2, "Tren Flamsbana y Sognefjord", "Tren Flamsbana (864 m, 20 tuneles, cascada Kjosfossen). Crucero opcional por Naeroyfjord.", "Flamsbana train & Sognefjord", "Flamsbana train (864 m, 20 tunnels, Kjosfossen waterfall). Optional Naeroyfjord cruise."),
        (6, 3, "Preikestolen", "Caminata guiada de 8 km hasta la plataforma de 604 m sobre el Lysefjord.", "Preikestolen", "Guided 8 km hike to the 604 m platform above the Lysefjord."),
        (7, 3, "Gamle Stavanger y regreso", "Casco antiguo de casas blancas. Museo del Petroleo opcional. Vuelo de regreso.", "Gamle Stavanger & departure", "White wooden houses old town. Optional Petroleum Museum. Return flight."),
    ]
    steps = [_make_route_step(pk, dm[r[1]], r[0], r[2], r[3], r[4], r[5]) for r in routes]

    return Pack(
        id=pk, slug="fiordos-noruegos", cover_image="https://images.unsplash.com/photo-1638140020886-587476d1e6d9?w=1200",
        duration_days=7, price_from=1490, price_to=5800, price_currency="EUR", featured=True,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Fiordos Noruegos: Bergen, Geiranger y Stavanger",
                description="Un viaje epico por los fiordos mas impresionantes del mundo. Bryggen, las Siete Hermanas, el tren Flamsbana y el Preikestolen.",
                short_description="7 dias de fiordos UNESCO, trenes panoramicos y senderismo epico.", duration="7 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Norwegian Fjords: Bergen, Geiranger & Stavanger",
                description="An epic journey through the world's most breathtaking fjords. Bryggen, the Seven Sisters, the Flamsbana train and Preikestolen.",
                short_description="7 days of UNESCO fjords, panoramic trains and epic hiking.", duration="7 days"),
        ],
        destinations=[d1, d2, d3, d4], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PACK 8: SAFARI EN KENIA
# ──────────────────────────────────────────────────────────────────────
def _pack_kenia() -> Pack:
    pk = _id()
    d1 = _dest(pk, 0, "https://images.unsplash.com/photo-1611348524140-53c9a25263d6?w=800",
        {"name": "Nairobi", "country": "Kenia", "description": "Capital vibrante con el unico parque nacional dentro de una capital del mundo. Centro de Jirafas y Santuario de Elefantes."},
        {"name": "Nairobi", "country": "Kenya", "description": "Vibrant capital with the world's only national park within a capital city. Giraffe Centre and Elephant Sanctuary."},
        days=1,
        accs=[
            _make_accommodation(None, "budget", 35, "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800",
                ["WiFi", "Ducha lluvia", "Limpieza diaria"], 4.1,
                "Jambo Guest House", "Casa de huespedes en el centro de Nairobi. Habitaciones con ducha de lluvia y servicio diario.",
                "Jambo Guest House", "Guesthouse in central Nairobi. Rooms with rainfall shower and daily housekeeping.",
                booking_url="https://www.booking.com/hotel/ke/jambo-guest-house.html", nights=1),
            _make_accommodation(None, "standard", 100, "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
                ["WiFi", "Piscina exterior", "Restaurante", "Upper Hill"], 4.4,
                "Hillpark Hotel", "Hotel 4 estrellas en Upper Hill, a 10 minutos del aeropuerto. Piscina exterior y restaurante.",
                "Hillpark Hotel", "4-star hotel in Upper Hill, 10 minutes from the airport. Outdoor pool and restaurant.",
                booking_url="https://www.booking.com/hotel/ke/hillpark-hotel-nairobi.html", nights=1),
            _make_accommodation(None, "premium", 320, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
                ["WiFi", "Mayordomo privado", "Spa", "Piscina climatizada", "Restaurante gourmet", "Barrio de Karen"], 4.8,
                "Hemingways Nairobi", "Hotel boutique de lujo en el exclusivo barrio de Karen. Mayordomo privado, spa y restaurante gourmet.",
                "Hemingways Nairobi", "Luxury boutique hotel in exclusive Karen neighbourhood. Private butler, spa and gourmet restaurant.",
                booking_url="https://www.booking.com/hotel/ke/hemingways-nairobi.html", nights=1),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/nairobi-l267/nairobi-national-park-half-day-game-drive-t212244/", 55,
                "https://images.unsplash.com/photo-1611348524140-53c9a25263d6?w=800", 4.6,
                "Safari de medio dia en el Parque Nacional de Nairobi", "4 horas en 4x4 por el unico parque nacional del mundo dentro de una capital. Posibilidad de ver los Big Five con el skyline de fondo.", "4 horas",
                "Nairobi National Park half-day safari", "4-hour game drive through the world's only national park inside a capital. Chance to spot the Big Five with the city skyline behind.", "4 hours"),
        ],
    )
    d2 = _dest(pk, 1, "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800",
        {"name": "Masai Mara", "country": "Kenia", "description": "La reserva de safari mas celebre de Africa. Llanuras de acacia, los Cinco Grandes y la Gran Migracion entre julio y octubre."},
        {"name": "Masai Mara", "country": "Kenya", "description": "Africa's most celebrated safari reserve. Acacia grasslands, the Big Five and the Great Migration from July to October."},
        days=3,
        accs=[
            _make_accommodation(None, "budget", 42, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800",
                ["Tiendas permanentes", "Ducha caliente", "WC privado", "Restaurante", "Fogata"], 4.1,
                "Miti Mingi Eco Camp", "Campamento ecologico a orillas del rio Ololaimutiek, a 500 m de la entrada al parque. Tiendas autocuidadas y desayuno incluido.",
                "Miti Mingi Eco Camp", "Eco camp on the banks of the Ololaimutiek River, 500 m from the park entrance. Self-contained tents and breakfast included.",
                booking_url="https://www.booking.com/hotel/ke/miti-mingi-eco-camp-nairagie-ngare.html", nights=3),
            _make_accommodation(None, "standard", 275, "https://images.unsplash.com/photo-1583037189850-1921ae7c6c22?w=800",
                ["WiFi", "Piscina", "Spa", "Restaurante Boma", "Minigolf", "Tiro con arco"], 4.6,
                "Sarova Mara Game Camp", "75 tiendas equipadas con ventilador, minibar y WiFi. Piscina, spa y restaurante con cocina internacional.",
                "Sarova Mara Game Camp", "75 tents equipped with fan, mini fridge and WiFi. Pool, spa and restaurant with international cuisine.",
                booking_url="https://www.booking.com/hotel/ke/sarova-mara-game-camp.html", nights=3),
            _make_accommodation(None, "premium", 1300, "https://images.unsplash.com/photo-1548574505-5e239809ee19?w=800",
                ["Suites 100m2", "Paredes de cristal panoramicas", "Piscina infinita", "Todos los safaris incluidos", "Pension completa premium"], 4.9,
                "Angama Mara", "Campamento de lujo suspendido a 300 m sobre el Valle del Rift. 30 suites con paredes de cristal de 11 m. Todo incluido.",
                "Angama Mara", "Luxury camp suspended 300 m above the Rift Valley. 30 suites with 11 m floor-to-ceiling glass walls. All-inclusive.",
                booking_url="https://angama.com/stay/angama-mara/", nights=3),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/maasai-mara-national-reserve-l97072/", 85,
                "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800", 4.8,
                "Safari en 4x4 por el Masai Mara", "Game drive al amanecer y al atardecer en 4x4 con techo pop-up. Busqueda de los Cinco Grandes con guia profesional.", "7 horas",
                "Masai Mara 4x4 game drive", "Sunrise and sunset game drive in pop-up roof 4x4. Big Five search with professional guide.", "7 hours"),
            _make_experience(None, "civitatis", "https://www.civitatis.com/en/masai-mara/", 35,
                "https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=800", 4.7,
                "Visita cultural a un poblado masai", "Danzas tradicionales, rituales de fuego y artesania local. Beneficio directo para la comunidad.", "2.5 horas",
                "Maasai village cultural visit", "Traditional dances, fire-making rituals and local crafts. Direct benefit to the community.", "2.5 hours"),
        ],
    )
    d3 = _dest(pk, 2, "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800",
        {"name": "Lago Nakuru", "country": "Kenia", "description": "Lago de sosa en el Gran Valle del Rift famoso por sus colonias de flamencos, rinocerontes negros y jirafas de Rothschild."},
        {"name": "Lake Nakuru", "country": "Kenya", "description": "Soda lake in the Great Rift Valley famous for flamingo colonies, black rhinos and Rothschild's giraffe."},
        days=1,
        accs=[
            _make_accommodation(None, "budget", 40, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800",
                ["Cabanas simples", "Restaurante", "Bar", "Jardin", "Ambiente natural"], 4.0,
                "Maili Saba Camp", "Campamento junto al parque con cabanas simples y facil acceso a la vida silvestre.",
                "Maili Saba Camp", "Camp near the park with simple cabins and easy wildlife access.",
                booking_url="https://www.booking.com/hotel/ke/maili-saba-camp.html", nights=1),
            _make_accommodation(None, "standard", 135, "https://images.unsplash.com/photo-1583037189850-1921ae7c6c22?w=800",
                ["WiFi", "Piscina con vistas", "Restaurante", "Bar", "Desk de excursiones"], 4.5,
                "Lake Nakuru Sopa Lodge", "Lodge dentro del parque con piscina con vistas, jardin exuberante y restaurante. Puntuado 8.7/10.",
                "Lake Nakuru Sopa Lodge", "Lodge inside the park with pool with a view, lush garden and restaurant. Rated 8.7/10.",
                booking_url="https://www.booking.com/hotel/ke/lake-nakuru-sopa-lodge.html", nights=1),
            _make_accommodation(None, "premium", 760, "https://images.unsplash.com/photo-1548574505-5e239809ee19?w=800",
                ["WiFi", "Pension completa", "Piscina exterior", "Reserva Soysambu UNESCO"], 4.7,
                "Lake Elmenteita Serena Camp", "Camp de lujo en la reserva Soysambu (UNESCO). Pension completa incluida, a 25 km del Lago Nakuru.",
                "Lake Elmenteita Serena Camp", "Luxury camp on Soysambu Conservancy (UNESCO). Full board included, 25 km from Lake Nakuru.",
                booking_url="https://www.booking.com/hotel/ke/lake-elementaita-serena-camp.html", nights=1),
        ],
    )
    d4 = _dest(pk, 3, "https://images.unsplash.com/photo-1535941339077-2dd1c7963098?w=800",
        {"name": "Amboseli", "country": "Kenia", "description": "A los pies del Kilimanjaro (5.895 m). Hogar de 1.600-1.900 elefantes: las estampas mas fotograficas de Africa."},
        {"name": "Amboseli", "country": "Kenya", "description": "At the foot of Kilimanjaro (5,895 m). Home to 1,600-1,900 elephants: Africa's most photogenic scenes."},
        days=2,
        accs=[
            _make_accommodation(None, "budget", 25, "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800",
                ["Restaurante", "Bar", "Jardin", "Vistas al Kilimanjaro"], 3.9,
                "Amboseli Eco Camp", "Campamento ecologico a 20 km del parque. Buenas vistas del Kilimanjaro en dias despejados.",
                "Amboseli Eco Camp", "Eco camp 20 km from the park. Good Kilimanjaro views on clear days.",
                booking_url="https://www.booking.com/hotel/ke/amboseli-eco-camp.html", nights=2),
            _make_accommodation(None, "standard", 185, "https://images.unsplash.com/photo-1583037189850-1921ae7c6c22?w=800",
                ["WiFi", "Piscina exterior", "Restaurante", "Jardin", "Terraza", "Parking"], 4.4,
                "Sentrim Amboseli Lodge", "Lodge a 2.6 km del parque con piscina, restaurante y terraza. Muy buena relacion calidad-precio.",
                "Sentrim Amboseli Lodge", "Lodge 2.6 km from the park with pool, restaurant and terrace. Very good value for money.",
                booking_url="https://www.booking.com/hotel/ke/sentrim-amboseli-lodge.html", nights=2),
            _make_accommodation(None, "premium", 330, "https://images.unsplash.com/photo-1548574505-5e239809ee19?w=800",
                ["WiFi", "Pension completa", "Piscina", "Restaurante", "Vistas al Kilimanjaro", "Ubicacion en el parque"], 4.8,
                "Ol Tukai Lodge Amboseli", "Lodge de lujo en el corazon de Amboseli con vistas directas al Kilimanjaro. Pension completa incluida.",
                "Ol Tukai Lodge Amboseli", "Luxury lodge in the heart of Amboseli with direct Kilimanjaro views. Full board included.",
                booking_url="https://www.booking.com/hotel/ke/ol-tukai-lodge-amboseli.html", nights=2),
        ],
        exps=[
            _make_experience(None, "getyourguide", "https://www.getyourguide.com/amboseli-national-park-l83994/", 120,
                "https://images.unsplash.com/photo-1535941339077-2dd1c7963098?w=800", 4.8,
                "Safari de elefantes en Amboseli bajo el Kilimanjaro", "Safari en 4x4 por los manantiales donde se congregan las manadas de elefantes con el Kilimanjaro nevado de fondo.", "10 horas",
                "Amboseli elephant safari with Kilimanjaro views", "4x4 safari through the springs where elephant herds gather against snow-capped Kilimanjaro.", "10 hours"),
        ],
    )
    for d in [d1, d2, d3, d4]:
        for a in d.accommodations:
            a.destination_id = d.id
        for e in d.experiences:
            e.destination_id = d.id

    dm = {0: d1.id, 1: d2.id, 2: d3.id, 3: d4.id}
    routes = [
        (1, 0, "Llegada a Nairobi", "Llegada. Centro de Jirafas y Santuario de Elefantes David Sheldrick.", "Arrival in Nairobi", "Arrival. Giraffe Centre and David Sheldrick Elephant Sanctuary."),
        (2, 1, "Viaje al Masai Mara", "5.5 h hasta la Reserva. Safari de tarde: primeros leones y cebras.", "Journey to Masai Mara", "5.5 h to the Reserve. Afternoon game drive: first lions and zebras."),
        (3, 1, "Dia completo en la sabana", "Safari al amanecer. Bush breakfast. Safari vespertino buscando los Cinco Grandes.", "Full day on the savanna", "Sunrise game drive. Bush breakfast. Evening drive searching for the Big Five."),
        (4, 1, "Visita masai y ultima manana", "Safari matutino. Visita a poblado masai: danzas y rituales de fuego.", "Maasai visit & last morning", "Morning game drive. Maasai village visit: dances and fire rituals."),
        (5, 2, "El lago de los flamencos", "Traslado a Lago Nakuru (5 h). Safari: flamencos, rinocerontes y jirafas de Rothschild.", "The flamingo lake", "Transfer to Lake Nakuru (5 h). Game drive: flamingos, rhinos and Rothschild's giraffe."),
        (6, 3, "Hacia el Kilimanjaro", "Traslado a Amboseli via Nairobi. Safari al atardecer con vistas al Kilimanjaro.", "Towards Kilimanjaro", "Transfer to Amboseli via Nairobi. Sunset game drive with Kilimanjaro views."),
        (7, 3, "Safari de elefantes", "Safari al amanecer: manadas de elefantes con Kilimanjaro nevado de fondo. El momento mas fotografico.", "Elephant safari", "Sunrise drive: elephant herds with snow-capped Kilimanjaro. The most photogenic moment."),
        (8, 0, "Regreso a Nairobi", "Safari matinal opcional. Regreso a Nairobi (4 h). Maasai Market y vuelo de regreso.", "Return to Nairobi", "Optional morning drive. Return to Nairobi (4 h). Maasai Market and return flight."),
    ]
    steps = [_make_route_step(pk, dm[r[1]], r[0], r[2], r[3], r[4], r[5]) for r in routes]

    return Pack(
        id=pk, slug="safari-en-kenia", cover_image="https://images.unsplash.com/photo-1516426122078-c23e76319801?w=1200",
        duration_days=8, price_from=1850, price_to=9800, price_currency="EUR", featured=False,
        translations=[
            PackTranslation(id=_id(), pack_id=pk, locale="es", title="Safari en Kenia: La Gran Migracion",
                description="Sumergete en la naturaleza africana: Masai Mara, los flamencos del Lago Nakuru y los elefantes bajo el Kilimanjaro en Amboseli.",
                short_description="8 dias de safari, los Cinco Grandes y la Gran Migracion.", duration="8 dias"),
            PackTranslation(id=_id(), pack_id=pk, locale="en", title="Kenya Safari: The Great Migration",
                description="Immerse yourself in African nature: Masai Mara, Lake Nakuru's flamingos and elephants beneath Kilimanjaro in Amboseli.",
                short_description="8 days of safari, the Big Five and the Great Migration.", duration="8 days"),
        ],
        destinations=[d1, d2, d3, d4], route_steps=steps,
    )


# ──────────────────────────────────────────────────────────────────────
# PRODUCTS (12, same as before)
# ──────────────────────────────────────────────────────────────────────
def _seed_products() -> list[Product]:
    data = [
        ("maleta-samsonite-spinner-55", "luggage", 129.99, "https://www.amazon.es/dp/B07EXAMPLE1?tag=ideatravel-21", "https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?w=800", 4.7,
         "Samsonite Spinner 55cm", "La maleta de cabina perfecta para viajeros frecuentes. Ultra ligera a solo 2.1kg con 4 ruedas y cierre TSA.",
         "Samsonite Spinner 55cm", "The perfect cabin suitcase for frequent travelers. Ultra-light at only 2.1kg with 4 wheels and TSA lock."),
        ("organizadores-equipaje-set-6", "luggage", 19.99, "https://www.amazon.es/dp/B07EXAMPLE2?tag=ideatravel-21", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800", 4.5,
         "Set 6 Organizadores de Equipaje", "Cubos de compresion de diferentes tamanos. Material resistente al agua y cremallera doble.",
         "6-Piece Packing Cube Set", "Compression cubes in different sizes. Water-resistant material with double zipper."),
        ("adaptador-universal-enchufe", "electronics", 24.99, "https://www.amazon.es/dp/B07EXAMPLE3?tag=ideatravel-21", "https://images.unsplash.com/photo-1625465588028-458f59e19ee6?w=800", 4.6,
         "Adaptador Universal con USB-C", "Un solo adaptador para mas de 150 paises. 3 puertos USB-A y 1 USB-C de carga rapida (30W).",
         "Universal Adapter with USB-C", "One adapter for over 150 countries. 3 USB-A ports and 1 USB-C fast charging (30W)."),
        ("powerbank-anker-20000", "electronics", 39.99, "https://www.amazon.es/dp/B07EXAMPLE4?tag=ideatravel-21", "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800", 4.8,
         "Anker PowerCore 20000mAh", "Bateria externa que carga tu movil hasta 5 veces. Puerto USB-C bidireccional. Permitida en avion.",
         "Anker PowerCore 20000mAh", "External battery that charges your phone up to 5 times. Bidirectional USB-C port. Airline approved."),
        ("auriculares-sony-wh1000xm5", "electronics", 329.99, "https://www.amazon.es/dp/B07EXAMPLE5?tag=ideatravel-21", "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800", 4.8,
         "Sony WH-1000XM5", "Los mejores auriculares con cancelacion de ruido. Hasta 30h de bateria, perfectos para vuelos largos.",
         "Sony WH-1000XM5", "The best noise-cancelling headphones. Up to 30h battery, perfect for long flights."),
        ("almohada-viaje-cervical", "comfort", 29.99, "https://www.amazon.es/dp/B07EXAMPLE6?tag=ideatravel-21", "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=800", 4.4,
         "Almohada Cervical de Espuma Memoria", "Espuma viscoelastica que se comprime a un tercio. Funda lavable y transpirable.",
         "Memory Foam Neck Pillow", "Memory foam that compresses to a third. Washable and breathable cover."),
        ("botella-agua-filtrante", "accessories", 44.99, "https://www.amazon.es/dp/B07EXAMPLE7?tag=ideatravel-21", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800", 4.6,
         "Botella con Filtro LifeStraw", "Filtra el 99.99% de bacterias y parasitos. Perfecta para trekking.",
         "LifeStraw Filter Bottle", "Filters 99.99% of bacteria and parasites. Perfect for trekking."),
        ("gopro-hero-12", "photography", 399.99, "https://www.amazon.es/dp/B07EXAMPLE8?tag=ideatravel-21", "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800", 4.7,
         "GoPro HERO 12 Black", "Captura aventuras en 5.3K con HyperSmooth 6.0. Resistente al agua hasta 10m.",
         "GoPro HERO 12 Black", "Capture adventures in 5.3K with HyperSmooth 6.0. Waterproof up to 10m."),
        ("rinonera-antirrobo", "accessories", 16.99, "https://www.amazon.es/dp/B07EXAMPLE9?tag=ideatravel-21", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800", 4.3,
         "Rinonera Antirrobo RFID", "Bloqueo RFID, compartimentos ocultos y material resistente a cortes.",
         "Anti-theft RFID Belt Bag", "RFID blocking, hidden compartments and cut-resistant material."),
        ("kindle-paperwhite", "comfort", 149.99, "https://www.amazon.es/dp/B07EXAMPLE10?tag=ideatravel-21", "https://images.unsplash.com/photo-1532104041590-1046d1a28c64?w=800", 4.7,
         "Kindle Paperwhite 2024", "Miles de libros en 200 gramos. Pantalla antirreflejos, resistente al agua.",
         "Kindle Paperwhite 2024", "Thousands of books in 200 grams. Anti-glare screen, waterproof."),
        ("tripode-viaje-compacto", "photography", 69.99, "https://www.amazon.es/dp/B07EXAMPLE11?tag=ideatravel-21", "https://images.unsplash.com/photo-1617575521317-d2974f3b56d2?w=800", 4.5,
         "Tripode de Viaje Manfrotto Compact", "Ultraligero (1.2kg), plegado 44cm. Compatible con movil y camara.",
         "Manfrotto Compact Travel Tripod", "Ultra-light (1.2kg), 44cm folded. Compatible with phone and camera."),
        ("mochila-cabina-40l", "luggage", 89.99, "https://www.amazon.es/dp/B07EXAMPLE12?tag=ideatravel-21", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800", 4.6,
         "Mochila de Cabina 40L Osprey", "Medidas maximas de equipaje de mano. Apertura tipo maleta y compartimento para portatil.",
         "Osprey 40L Cabin Backpack", "Maximum carry-on dimensions. Suitcase-style opening and laptop compartment."),
    ]
    products = []
    for slug, cat, price, url, img, rating, name_es, desc_es, name_en, desc_en in data:
        pid = _id()
        products.append(Product(
            id=pid, slug=slug, category=cat, price=price, currency="EUR",
            affiliate_url=url, image=img, rating=rating,
            translations=[
                ProductTranslation(id=_id(), product_id=pid, locale="es", name=name_es, description=desc_es),
                ProductTranslation(id=_id(), product_id=pid, locale="en", name=name_en, description=desc_en),
            ],
        ))
    return products


def _seed_blog_posts() -> list[BlogPost]:
    posts_data = [
        {
            "slug": "10-cosas-que-hacer-en-paris",
            "cover_image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200",
            "category": "guia",
            "published_at": datetime(2026, 3, 15, tzinfo=timezone.utc),
            "title_es": "10 cosas que hacer en Paris que no te puedes perder",
            "excerpt_es": "Paris es mucho mas que la Torre Eiffel. Descubre las experiencias imprescindibles para tu primer viaje a la Ciudad de la Luz.",
            "content_es": """## 1. Subir a la Torre Eiffel al atardecer

No es un cliche, es una experiencia que merece la pena. Reserva la subida para las ultimas horas de la tarde y veras como la ciudad se ilumina bajo tus pies. Consejo: compra las entradas con antelacion para evitar las colas.

## 2. Perderte por Le Marais

El barrio mas bohemio de Paris. Galerias de arte, tiendas vintage, falafels en Rue des Rosiers y cafes con encanto en cada esquina. Dejate llevar sin mapa.

## 3. Visitar el Louvre (con estrategia)

El museo es inmenso. No intentes verlo todo en un dia. Elige 2-3 salas que te interesen y disfruta sin prisas. La Mona Lisa esta siempre abarrotada; las salas de escultura griega son igual de impresionantes y mucho mas tranquilas.

## 4. Crucero por el Sena

Una de las mejores formas de ver los monumentos de Paris. Los Bateaux Mouches salen cada 30 minutos desde el Pont de l'Alma. Al atardecer es magico.

## 5. Montmartre y el Sacre-Coeur

Sube las escaleras (o toma el funicular) hasta la basilica y disfruta de las mejores vistas de Paris. Luego baja por las callejuelas de Montmartre, donde Picasso y Toulouse-Lautrec encontraron inspiracion.

## 6. Comer croissants en una boulangerie local

Olvida las cadenas. Busca una boulangerie de barrio y pide un croissant au beurre recien hecho. La diferencia es abismal. Recomendacion: Du Pain et des Idees en el Canal Saint-Martin.

## 7. Pasear por los jardines de Luxemburgo

El parque favorito de los parisinos. Perfecto para descansar despues de una manana de museos. Lleva algo de comer y sientate junto al estanque.

## 8. Explorar Saint-Germain-des-Pres

El barrio literario por excelencia. Cafes historicos como Les Deux Magots, librerias de segunda mano y una atmosfera intelectual que se respira en cada calle.

## 9. Ver Paris desde el Centre Pompidou

Las escaleras mecanicas exteriores del Pompidou ofrecen vistas panoramicas gratuitas. Dentro, una de las mejores colecciones de arte contemporaneo del mundo.

## 10. Cenar en un bistrot autentico

Nada de restaurantes turisticos cerca de los monumentos. Busca un bistrot en el 11eme o el 5eme arrondissement. Precio medio: 25-35 EUR por persona con vino incluido.""",
            "title_en": "10 things to do in Paris you can't miss",
            "excerpt_en": "Paris is much more than the Eiffel Tower. Discover the must-have experiences for your first trip to the City of Light.",
            "content_en": """## 1. Climb the Eiffel Tower at sunset

It's not a cliche, it's an experience worth having. Book your visit for late afternoon and watch the city light up beneath you. Tip: buy tickets in advance to skip the queues.

## 2. Get lost in Le Marais

Paris' most bohemian neighborhood. Art galleries, vintage shops, falafels on Rue des Rosiers and charming cafes on every corner. Let yourself wander without a map.

## 3. Visit the Louvre (with a strategy)

The museum is huge. Don't try to see everything in one day. Pick 2-3 rooms that interest you and enjoy without rushing. The Mona Lisa is always crowded; the Greek sculpture rooms are equally impressive and much quieter.

## 4. Seine river cruise

One of the best ways to see Paris' monuments. Bateaux Mouches depart every 30 minutes from Pont de l'Alma. At sunset it's magical.

## 5. Montmartre and Sacre-Coeur

Climb the stairs (or take the funicular) to the basilica and enjoy the best views of Paris. Then wander down through Montmartre's alleyways, where Picasso and Toulouse-Lautrec found inspiration.

## 6. Eat croissants at a local boulangerie

Forget the chains. Find a neighborhood boulangerie and order a freshly made croissant au beurre. The difference is staggering. Recommendation: Du Pain et des Idees on Canal Saint-Martin.

## 7. Stroll through Luxembourg Gardens

The Parisians' favorite park. Perfect for resting after a morning of museums. Bring something to eat and sit by the pond.

## 8. Explore Saint-Germain-des-Pres

The literary quarter par excellence. Historic cafes like Les Deux Magots, second-hand bookshops and an intellectual atmosphere you can feel on every street.

## 9. See Paris from Centre Pompidou

The Pompidou's exterior escalators offer free panoramic views. Inside, one of the world's best contemporary art collections.

## 10. Dine at an authentic bistrot

Skip the tourist restaurants near monuments. Find a bistrot in the 11th or 5th arrondissement. Average price: 25-35 EUR per person with wine included.""",
        },
        {
            "slug": "cuanto-cuesta-viajar-a-japon",
            "cover_image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200",
            "category": "presupuesto",
            "published_at": datetime(2026, 3, 10, tzinfo=timezone.utc),
            "title_es": "Cuanto cuesta viajar a Japon: presupuesto real para 2 semanas",
            "excerpt_es": "Desglose completo de gastos para un viaje de 14 dias a Japon. Vuelos, alojamiento, transporte, comida y actividades con precios reales.",
            "content_es": """## Presupuesto total estimado: 2.500 - 4.000 EUR por persona

Japon tiene fama de caro, pero con planificacion se puede disfrutar sin arruinarse. Aqui va el desglose real basado en nuestra experiencia.

## Vuelos: 600 - 900 EUR

Desde Espana, los vuelos con escala suelen costar entre 600 y 900 EUR ida y vuelta. Aerolineas como Turkish Airlines, Qatar Airways o China Eastern ofrecen buenas opciones. Reserva con 2-3 meses de antelacion.

## Alojamiento: 700 - 1.400 EUR (14 noches)

- **Presupuesto bajo**: Hostels y capsule hotels (50-70 EUR/noche)
- **Presupuesto medio**: Business hotels tipo Toyoko Inn o APA Hotel (70-100 EUR/noche)
- **Presupuesto alto**: Ryokan tradicional o hoteles boutique (100-150+ EUR/noche)

Recomendacion: combina 2-3 noches en ryokan con el resto en business hotels.

## Transporte interno: 250 - 400 EUR

El Japan Rail Pass (JR Pass) de 14 dias cuesta unos 380 EUR y es imprescindible si vas a moverte entre ciudades. Cubre trenes bala (shinkansen), trenes locales y algunos ferries.

Para metro en Tokio y Osaka: tarjeta Suica o Pasmo recargable. Calcula unos 5-8 EUR/dia.

## Comida: 350 - 700 EUR (14 dias)

- **Desayuno**: Incluido en muchos hoteles o conbini (7-Eleven, Lawson) por 3-5 EUR
- **Almuerzo**: Ramen, gyudon o curry por 7-10 EUR
- **Cena**: Izakaya o restaurante local por 15-25 EUR

La comida en Japon es increiblemente buena incluso en los sitios baratos. Un ramen de 8 EUR en Tokio puede ser la mejor comida de tu viaje.

## Actividades: 200 - 400 EUR

- Templos y santuarios: muchos son gratuitos, algunos cobran 3-5 EUR
- Experiencias tipicas: ceremonia del te (25-40 EUR), onsen publico (5-10 EUR)
- Excursiones: dia en Hakone (50 EUR con transporte), Nara (gratis con JR Pass)

## Extras: 100 - 200 EUR

- SIM/eSIM de datos: 30-50 EUR (14 dias)
- Seguro de viaje: 50-80 EUR
- Souvenirs y gastos varios: 50-100 EUR

## Consejos para ahorrar

1. **Come en konbinis**: Los 7-Eleven japoneses tienen comida excelente por 3-5 EUR
2. **Usa el JR Pass al maximo**: Planifica tus trayectos largos para amortizarlo
3. **Alojate fuera del centro**: Las estaciones del metro te conectan rapido y los precios bajan mucho
4. **Visita templos gratuitos**: Fushimi Inari, Senso-ji y muchos mas no cobran entrada
5. **Lleva efectivo**: Japon sigue siendo un pais de efectivo en muchos sitios""",
            "title_en": "How much does it cost to travel to Japan: real budget for 2 weeks",
            "excerpt_en": "Complete expense breakdown for a 14-day trip to Japan. Flights, accommodation, transport, food and activities with real prices.",
            "content_en": """## Estimated total budget: 2,500 - 4,000 EUR per person

Japan has a reputation for being expensive, but with planning you can enjoy it without breaking the bank. Here's the real breakdown based on our experience.

## Flights: 600 - 900 EUR

From Spain, flights with a stopover usually cost between 600 and 900 EUR round trip. Airlines like Turkish Airlines, Qatar Airways or China Eastern offer good options. Book 2-3 months in advance.

## Accommodation: 700 - 1,400 EUR (14 nights)

- **Low budget**: Hostels and capsule hotels (50-70 EUR/night)
- **Mid budget**: Business hotels like Toyoko Inn or APA Hotel (70-100 EUR/night)
- **High budget**: Traditional ryokan or boutique hotels (100-150+ EUR/night)

Recommendation: combine 2-3 nights in a ryokan with the rest in business hotels.

## Internal transport: 250 - 400 EUR

The 14-day Japan Rail Pass (JR Pass) costs about 380 EUR and is essential if you're traveling between cities. It covers bullet trains (shinkansen), local trains and some ferries.

For metro in Tokyo and Osaka: rechargeable Suica or Pasmo card. Budget about 5-8 EUR/day.

## Food: 350 - 700 EUR (14 days)

- **Breakfast**: Included in many hotels or conbini (7-Eleven, Lawson) for 3-5 EUR
- **Lunch**: Ramen, gyudon or curry for 7-10 EUR
- **Dinner**: Izakaya or local restaurant for 15-25 EUR

Food in Japan is incredibly good even at cheap places. An 8 EUR ramen in Tokyo can be the best meal of your trip.

## Activities: 200 - 400 EUR

- Temples and shrines: many are free, some charge 3-5 EUR
- Typical experiences: tea ceremony (25-40 EUR), public onsen (5-10 EUR)
- Day trips: Hakone (50 EUR with transport), Nara (free with JR Pass)

## Extras: 100 - 200 EUR

- Data SIM/eSIM: 30-50 EUR (14 days)
- Travel insurance: 50-80 EUR
- Souvenirs and miscellaneous: 50-100 EUR

## Tips for saving money

1. **Eat at konbinis**: Japanese 7-Elevens have excellent food for 3-5 EUR
2. **Maximize your JR Pass**: Plan long trips to get your money's worth
3. **Stay outside the center**: Metro stations connect you quickly and prices drop significantly
4. **Visit free temples**: Fushimi Inari, Senso-ji and many more are free
5. **Carry cash**: Japan is still a cash country in many places""",
        },
        {
            "slug": "mejor-epoca-para-visitar-fiordos-noruegos",
            "cover_image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200",
            "category": "consejos",
            "published_at": datetime(2026, 3, 5, tzinfo=timezone.utc),
            "title_es": "Mejor epoca para visitar los fiordos noruegos (y que evitar)",
            "excerpt_es": "Guia mes a mes para planificar tu viaje a los fiordos. Clima, precios, horas de luz y que esperar en cada temporada.",
            "content_es": """## La respuesta corta: junio a agosto

Si quieres buen tiempo, dias largos y todas las rutas abiertas, el verano es tu mejor opcion. Pero cada temporada tiene su encanto.

## Verano (junio - agosto): la temporada estrella

- **Temperatura**: 15-25°C en los valles, mas frio en altitud
- **Horas de luz**: 18-24 horas (sol de medianoche en el norte)
- **Ventajas**: Todo abierto, carreteras accesibles, naturaleza en su maximo esplendor
- **Desventajas**: Precios altos, turismo masivo en los spots mas famosos
- **Precio medio alojamiento**: 120-200 EUR/noche

Julio es el mes mas popular pero tambien el mas caro y concurrido. Junio ofrece casi las mismas condiciones con menos gente.

## Primavera (abril - mayo): el despertar

- **Temperatura**: 5-15°C
- **Horas de luz**: 14-18 horas
- **Ventajas**: Cascadas en su maximo caudal por el deshielo, precios mas bajos, poca gente
- **Desventajas**: Algunas carreteras de montaria aun cerradas, tiempo impredecible
- **Precio medio alojamiento**: 80-140 EUR/noche

Mayo es un mes excelente si no te importa algo de frio. Las cascadas son espectaculares.

## Otorio (septiembre - octubre): colores y tranquilidad

- **Temperatura**: 5-15°C
- **Horas de luz**: 10-14 horas
- **Ventajas**: Colores otoniales, precios mas bajos, menos turistas, posibilidad de auroras boreales
- **Desventajas**: Dias mas cortos, algunas actividades cierran
- **Precio medio alojamiento**: 80-130 EUR/noche

Septiembre es quizas el mejor mes en relacion calidad-precio. El paisaje es increible con los colores del otorio.

## Invierno (noviembre - marzo): auroras boreales

- **Temperatura**: -5 a 5°C
- **Horas de luz**: 4-8 horas (noche polar en el norte)
- **Ventajas**: Auroras boreales, paisajes nevados, precios bajos
- **Desventajas**: Muchas carreteras cerradas, dias muy cortos, actividades limitadas
- **Precio medio alojamiento**: 70-120 EUR/noche

Solo recomendado si tu objetivo principal son las auroras boreales o deportes de invierno.

## Nuestra recomendacion

**Primera visita**: segunda quincena de junio. Buen tiempo, dias larguisimos, todo abierto y algo menos de gente que julio.

**Con presupuesto ajustado**: septiembre. Precios mucho mas bajos, paisajes espectaculares y aun con buen tiempo.

**Para aventureros**: febrero-marzo en Tromso o Lofoten para auroras boreales.""",
            "title_en": "Best time to visit the Norwegian fjords (and what to avoid)",
            "excerpt_en": "Month-by-month guide to plan your fjords trip. Weather, prices, daylight hours and what to expect in each season.",
            "content_en": """## The short answer: June to August

If you want good weather, long days and all routes open, summer is your best bet. But each season has its charm.

## Summer (June - August): peak season

- **Temperature**: 15-25°C in valleys, cooler at altitude
- **Daylight hours**: 18-24 hours (midnight sun in the north)
- **Pros**: Everything open, roads accessible, nature at its best
- **Cons**: High prices, mass tourism at famous spots
- **Average accommodation price**: 120-200 EUR/night

July is the most popular month but also the most expensive and crowded. June offers almost the same conditions with fewer people.

## Spring (April - May): the awakening

- **Temperature**: 5-15°C
- **Daylight hours**: 14-18 hours
- **Pros**: Waterfalls at peak flow from snowmelt, lower prices, few people
- **Cons**: Some mountain roads still closed, unpredictable weather
- **Average accommodation price**: 80-140 EUR/night

May is an excellent month if you don't mind some cold. The waterfalls are spectacular.

## Autumn (September - October): colors and tranquility

- **Temperature**: 5-15°C
- **Daylight hours**: 10-14 hours
- **Pros**: Autumn colors, lower prices, fewer tourists, northern lights possible
- **Cons**: Shorter days, some activities close
- **Average accommodation price**: 80-130 EUR/night

September might be the best value-for-money month. The landscape is incredible with autumn colors.

## Winter (November - March): northern lights

- **Temperature**: -5 to 5°C
- **Daylight hours**: 4-8 hours (polar night in the north)
- **Pros**: Northern lights, snowy landscapes, low prices
- **Cons**: Many roads closed, very short days, limited activities
- **Average accommodation price**: 70-120 EUR/night

Only recommended if your main goal is northern lights or winter sports.

## Our recommendation

**First visit**: second half of June. Good weather, very long days, everything open and slightly less crowded than July.

**On a budget**: September. Much lower prices, spectacular scenery and still good weather.

**For adventurers**: February-March in Tromso or Lofoten for northern lights.""",
        },
    ]

    posts = []
    for data in posts_data:
        post_id = _id()
        posts.append(BlogPost(
            id=post_id,
            slug=data["slug"],
            cover_image=data["cover_image"],
            category=data["category"],
            published=True,
            published_at=data["published_at"],
            translations=[
                BlogPostTranslation(
                    id=_id(), blog_post_id=post_id, locale="es",
                    title=data["title_es"], excerpt=data["excerpt_es"], content=data["content_es"],
                ),
                BlogPostTranslation(
                    id=_id(), blog_post_id=post_id, locale="en",
                    title=data["title_en"], excerpt=data["excerpt_en"], content=data["content_en"],
                ),
            ],
        ))
    return posts


async def seed() -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(func.count()).select_from(Pack))
        if result.scalar() > 0:
            print("Database already seeded, skipping...")
            return

        packs = [
            _pack_paris(),
            _pack_italia(),
            _pack_espana(),
            _pack_eslovenia_croacia(),
            _pack_japon(),
            _pack_londres(),
            _pack_noruega(),
            _pack_kenia(),
        ]
        products = _seed_products()
        blog_posts = _seed_blog_posts()

        session.add_all(packs)
        session.add_all(products)
        session.add_all(blog_posts)
        await session.commit()
        print(f"Seeded {len(packs)} packs, {len(products)} products and {len(blog_posts)} blog posts!")


if __name__ == "__main__":
    asyncio.run(seed())
