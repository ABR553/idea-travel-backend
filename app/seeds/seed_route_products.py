"""Seed route_step_products associations and detailed_description for route steps.

Connects existing products to route steps with contextual recommendations,
and adds rich detailed_description (markdown) to each route step translation.

Usage:
    docker-compose exec api python -m app.seeds.seed_route_products
"""
import asyncio
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session_factory
from app.domain.models.pack import Pack
from app.domain.models.product import Product
from app.domain.models.route_step import (
    RouteStep,
    RouteStepProduct,
    RouteStepTranslation,
)


# ---------------------------------------------------------------------------
# Product slug aliases (real slugs from the database)
# ---------------------------------------------------------------------------
# Luggage
P_SAMSONITE = "maleta-samsonite-spinner-55"
P_BACKPACK = "mochila-cabina-40l"
P_ORGANIZERS = "organizadores-equipaje-set-6"
# Electronics
P_ADAPTER = "adaptador-universal-enchufe"
P_HEADPHONES = "auriculares-sony-wh1000xm5"
P_POWERBANK = "powerbank-anker-20000"
# Comfort
P_PILLOW = "almohada-viaje-cervical"
P_KINDLE = "kindle-paperwhite"
# Accessories
P_BOTTLE = "botella-agua-filtrante"
P_FANNY_PACK = "rinonera-antirrobo"
# Photography
P_GOPRO = "gopro-hero-12"
P_TRIPOD = "tripode-viaje-compacto"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class ProductLink:
    product_slug: str
    position: int
    context_es: str
    context_en: str


@dataclass
class RouteStepSeed:
    day: int
    products: list[ProductLink]
    detailed_es: str | None = None
    detailed_en: str | None = None


# ---------------------------------------------------------------------------
# PARIS - paris-ciudad-de-la-luz (5 days)
# ---------------------------------------------------------------------------
PARIS_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ORGANIZERS, 0,
                "Lleva la maleta organizada desde el primer dia con estos cubos de equipaje",
                "Keep your suitcase organized from day one with these packing cubes"),
            ProductLink(P_ADAPTER, 1,
                "Francia usa enchufes tipo E; este adaptador te cubre en toda Europa",
                "France uses type E plugs; this adapter covers you across Europe"),
            ProductLink(P_POWERBANK, 2,
                "Google Maps, fotos y redes consumen bateria; lleva siempre carga extra",
                "Google Maps, photos and social media drain battery; always carry extra charge"),
        ],
        detailed_es=(
            "Aterrizas en Paris y comienza la aventura. Tras recoger tu equipaje, "
            "el trayecto al centro es sencillo con el RER B (unos 50 min desde CDG).\n\n"
            "Pasea por la **Place des Vosges**, la plaza mas antigua de Paris, y acercate "
            "a **Notre-Dame** para ver el avance de su restauracion. Pierdete por las calles "
            "de Le Marais, donde cada esquina esconde una boulangerie o una galeria de arte.\n\n"
            "> **Tip:** Compra la tarjeta Navigo Decouverte (semana) si llegas en lunes; "
            "amortizas metro y RER ilimitados por ~30 EUR."
        ),
        detailed_en=(
            "You land in Paris and the adventure begins. After collecting your luggage, "
            "getting to the center is easy via RER B (about 50 min from CDG).\n\n"
            "Stroll through **Place des Vosges**, the oldest planned square in Paris, and stop by "
            "**Notre-Dame** to see the restoration progress. Wander through Le Marais, where "
            "every corner hides a boulangerie or art gallery.\n\n"
            "> **Tip:** Buy the Navigo Decouverte weekly pass if you arrive on Monday; "
            "you'll get unlimited metro & RER for ~30 EUR."
        ),
    ),
    RouteStepSeed(
        day=2,
        products=[
            ProductLink(P_GOPRO, 0,
                "Captura la grandiosidad del Louvre y sus obras maestras en alta calidad",
                "Capture the grandeur of the Louvre and its masterpieces in high quality"),
            ProductLink(P_FANNY_PACK, 1,
                "Lleva documentos, movil y cartera seguros en el museo mas visitado del mundo",
                "Keep documents, phone and wallet safe in the world's most visited museum"),
        ],
        detailed_es=(
            "Reserva la **entrada al Louvre** con hora. Sin reserva, la cola puede superar "
            "las 2 horas. Dedica al menos 3 horas: la Mona Lisa, la Venus de Milo y la "
            "Victoria de Samotracia son imprescindibles, pero el ala de arte islamico es una "
            "joya escondida.\n\n"
            "Despues, pasea por el **Jardin de las Tullerias** hasta la Place de la Concorde. "
            "Si el dia acompana, es perfecto para un cafe en una terraza.\n\n"
            "> **Tip:** Los miercoles y viernes el Louvre cierra a las 21:45; "
            "la visita nocturna es mas tranquila y atmosferica."
        ),
        detailed_en=(
            "Book your **Louvre timed entry** in advance. Without a reservation, the queue "
            "can exceed 2 hours. Allow at least 3 hours: the Mona Lisa, Venus de Milo and "
            "Winged Victory are must-sees, but the Islamic Art wing is a hidden gem.\n\n"
            "Afterwards, stroll through the **Tuileries Garden** to Place de la Concorde. "
            "If the weather is good, perfect for a terrace coffee.\n\n"
            "> **Tip:** On Wednesdays and Fridays the Louvre stays open until 9:45 PM; "
            "the evening visit is calmer and more atmospheric."
        ),
    ),
    RouteStepSeed(
        day=3,
        products=[
            ProductLink(P_GOPRO, 0,
                "Graba la Torre Eiffel y las vistas desde la cima en 5.3K",
                "Record the Eiffel Tower and summit views in 5.3K"),
            ProductLink(P_TRIPOD, 1,
                "Imprescindible para timelapses y fotos nocturnas de la torre iluminada",
                "Essential for timelapses and night photos of the illuminated tower"),
        ],
        detailed_es=(
            "Hoy toca el icono: la **Torre Eiffel**. Si subes a la cima, reserva con semanas "
            "de antelacion (se agotan rapido). La segunda planta tiene las mejores vistas para "
            "fotos sin cristal.\n\n"
            "Baja caminando por el **Champ de Mars** y cruza el puente hacia el Trocadero para "
            "la foto clasica. Sigue por los **Champs-Elysees** hasta el Arco del Triunfo; "
            "la subida merece la pena al atardecer.\n\n"
            "> **Tip:** Lleva un picnic al Champ de Mars: una baguette, queso y una botella "
            "de vino. Es la experiencia mas parisina que puedes vivir."
        ),
        detailed_en=(
            "Today is the icon: the **Eiffel Tower**. If you're going to the top, book weeks "
            "in advance (slots sell out fast). The second floor has the best views for photos "
            "without glass.\n\n"
            "Walk down through the **Champ de Mars** and cross the bridge to Trocadero for "
            "the classic photo. Continue along the **Champs-Elysees** to the Arc de Triomphe; "
            "the climb is worth it at sunset.\n\n"
            "> **Tip:** Bring a picnic to the Champ de Mars: a baguette, cheese and a bottle "
            "of wine. It's the most Parisian experience you can have."
        ),
    ),
    RouteStepSeed(
        day=4,
        products=[
            ProductLink(P_BOTTLE, 0,
                "Montmartre tiene cuestas empinadas; hidratate con agua filtrada",
                "Montmartre has steep hills; stay hydrated with filtered water"),
            ProductLink(P_BACKPACK, 1,
                "Mochila de cabina perfecta para la excursion a Montmartre",
                "Cabin backpack perfect for the Montmartre day trip"),
        ],
        detailed_es=(
            "Sube a **Montmartre** temprano, antes de que lleguen las multitudes. La basilica "
            "del **Sacre-Coeur** ofrece vistas de 360 grados de Paris desde su cupula.\n\n"
            "Explora la **Place du Tertre** donde pintores y retratistas trabajan al aire "
            "libre. Baja por callejuelas hasta el **Moulin Rouge** (la foto exterior es "
            "gratis). El barrio es perfecto para perderse sin mapa.\n\n"
            "> **Tip:** Prueba un crepe de Nutella en las creperies de la Rue Lepic; "
            "las mas autenticas estan alejadas de la plaza principal."
        ),
        detailed_en=(
            "Head up to **Montmartre** early, before the crowds arrive. The **Sacre-Coeur** "
            "basilica offers 360-degree views of Paris from its dome.\n\n"
            "Explore **Place du Tertre** where painters and portrait artists work outdoors. "
            "Wind down through alleys to the **Moulin Rouge** (the exterior photo is free). "
            "This neighborhood is perfect for wandering without a map.\n\n"
            "> **Tip:** Try a Nutella crepe at the creperies on Rue Lepic; "
            "the most authentic ones are away from the main square."
        ),
    ),
    RouteStepSeed(
        day=5,
        products=[
            ProductLink(P_HEADPHONES, 0,
                "Cancelacion de ruido para descansar en el vuelo de vuelta",
                "Noise cancelling to rest on the return flight"),
            ProductLink(P_PILLOW, 1,
                "Almohada cervical para dormir comodo en el avion",
                "Neck pillow to sleep comfortably on the plane"),
            ProductLink(P_KINDLE, 2,
                "Lectura ligera para las horas de espera y el vuelo de regreso",
                "Light reading for waiting hours and the return flight"),
        ],
        detailed_es=(
            "Ultimo dia en Paris. Dedica la manana al **Museo d'Orsay**, la catedral del "
            "impresionismo: Monet, Renoir, Degas y Van Gogh te esperan. El edificio, una "
            "antigua estacion de tren, es una obra de arte en si mismo.\n\n"
            "Despues, pasea por **Saint-Germain-des-Pres**: la libreria Shakespeare & Company, "
            "el Cafe de Flore y Les Deux Magots son paradas obligadas. Ultimo macaron en "
            "Laduree antes de despedirte.\n\n"
            "> **Tip:** La tarjeta Paris Museum Pass (2 dias) cubre Orsay, Louvre y otros "
            "50 museos. Si no la compraste antes, el Orsay solo merece las 2-3 horas."
        ),
        detailed_en=(
            "Last day in Paris. Spend the morning at the **Musee d'Orsay**, the cathedral of "
            "Impressionism: Monet, Renoir, Degas and Van Gogh await. The building, a former "
            "train station, is a work of art itself.\n\n"
            "Then stroll through **Saint-Germain-des-Pres**: Shakespeare & Company bookshop, "
            "Cafe de Flore and Les Deux Magots are must-stops. Last macaron at Laduree before "
            "saying goodbye.\n\n"
            "> **Tip:** The Paris Museum Pass (2 days) covers Orsay, Louvre and 50+ other "
            "museums. If you didn't buy it earlier, Orsay alone is worth the 2-3 hours."
        ),
    ),
]


# ---------------------------------------------------------------------------
# ITALY - ruta-por-italia (10 days)
# ---------------------------------------------------------------------------
ITALY_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ORGANIZERS, 0,
                "10 dias de viaje multi-ciudad; los cubos de equipaje son esenciales",
                "10-day multi-city trip; packing cubes are essential"),
            ProductLink(P_ADAPTER, 1,
                "Italia usa enchufes tipo L; con este adaptador cargas todo",
                "Italy uses type L plugs; this adapter charges everything"),
            ProductLink(P_FANNY_PACK, 2,
                "Roma tiene carteristas; lleva tus objetos de valor seguros",
                "Rome has pickpockets; keep your valuables safe"),
        ],
        detailed_es=(
            "Bienvenido a Roma. El traslado desde Fiumicino al centro es rapido con el "
            "**Leonardo Express** (32 min a Termini, 14 EUR).\n\n"
            "Tu primer paseo es por **Trastevere**, el barrio mas autentico: callejuelas "
            "empedradas, ropa tendida entre balcones y trattorias familiares. Cena junto al "
            "**Panteon** (entrada gratuita) iluminado de noche.\n\n"
            "> **Tip:** Prueba la supplì (croqueta de arroz romana) en Supplizio; "
            "es el mejor aperitivo para empezar tu viaje italiano."
        ),
        detailed_en=(
            "Welcome to Rome. Transfer from Fiumicino to the center is quick via the "
            "**Leonardo Express** (32 min to Termini, 14 EUR).\n\n"
            "Your first walk is through **Trastevere**, the most authentic neighborhood: "
            "cobblestone alleys, laundry hanging between balconies and family-run trattorias. "
            "Dinner by the **Pantheon** (free entry) lit up at night.\n\n"
            "> **Tip:** Try the supplì (Roman rice croquette) at Supplizio; "
            "it's the best appetizer to kick off your Italian trip."
        ),
    ),
    RouteStepSeed(
        day=3,
        products=[
            ProductLink(P_PILLOW, 0,
                "Comodidad extra para el tren Frecciarossa Roma-Florencia (1h30)",
                "Extra comfort for the Frecciarossa train Rome-Florence (1h30)"),
            ProductLink(P_HEADPHONES, 1,
                "Cancelacion de ruido para descansar en el tren",
                "Noise cancelling to rest on the train"),
            ProductLink(P_KINDLE, 2,
                "Lectura perfecta para los trayectos en tren por Italia",
                "Perfect reading for Italian train journeys"),
        ],
        detailed_es=(
            "Ultimo dia en Roma antes del tren. Empieza en la **Plaza Navona** con sus "
            "tres fuentes barrocas (la de Bernini es espectacular). Lanza una moneda en la "
            "**Fontana di Trevi** (1 moneda = volveras a Roma) y visita el Panteon por dentro.\n\n"
            "Por la tarde, toma el **Frecciarossa** a Florencia (1h30, desde 19 EUR si "
            "reservas con antelacion). Llegaras justo para una passeggiata por el Ponte Vecchio "
            "al atardecer.\n\n"
            "> **Tip:** Compra los billetes de Trenitalia con 2-3 semanas de antelacion; "
            "los precios suben mucho en fechas cercanas."
        ),
        detailed_en=(
            "Last day in Rome before the train. Start at **Piazza Navona** with its three "
            "baroque fountains (Bernini's is spectacular). Toss a coin in the **Trevi Fountain** "
            "(1 coin = you'll return to Rome) and visit the Pantheon inside.\n\n"
            "In the afternoon, catch the **Frecciarossa** to Florence (1h30, from 19 EUR if "
            "booked in advance). You'll arrive just in time for a passeggiata over the Ponte "
            "Vecchio at sunset.\n\n"
            "> **Tip:** Buy Trenitalia tickets 2-3 weeks ahead; "
            "prices increase significantly closer to the date."
        ),
    ),
    RouteStepSeed(
        day=5,
        products=[
            ProductLink(P_GOPRO, 0,
                "Graba los vinedos del Chianti con calidad cinematografica en 5.3K",
                "Film Chianti vineyards with cinematic 5.3K quality"),
            ProductLink(P_BOTTLE, 1,
                "Hidratacion esencial durante la excursion por las colinas toscanas",
                "Essential hydration during the Tuscan hills excursion"),
        ],
        detailed_es=(
            "Dia de escapada al campo toscano. Una **excursion al Chianti** te lleva por "
            "colinas de cipresses, dos bodegas con cata de Chianti Classico DOCG y un almuerzo "
            "con productos km 0.\n\n"
            "Los paisajes son de postal: vinedos infinitos, casas de piedra y pueblos como "
            "Greve in Chianti o Castellina. Si vas por libre, alquila un coche o reserva un "
            "tour en grupo reducido.\n\n"
            "> **Tip:** No conduzcas si vas a catar; los controles de alcoholemia en "
            "las carreteras toscanas son frecuentes."
        ),
        detailed_en=(
            "A day trip to the Tuscan countryside. A **Chianti excursion** takes you through "
            "cypress hills, two wineries with Chianti Classico DOCG tastings and a lunch "
            "with local km-0 products.\n\n"
            "The landscapes are postcard-perfect: endless vineyards, stone houses and villages "
            "like Greve in Chianti or Castellina. If going independently, rent a car or book a "
            "small group tour.\n\n"
            "> **Tip:** Don't drive if you're tasting; drink-driving checkpoints on "
            "Tuscan roads are frequent."
        ),
    ),
    RouteStepSeed(
        day=8,
        products=[
            ProductLink(P_GOPRO, 0,
                "Resistente al agua: perfecta para grabar el paseo en gondola",
                "Waterproof: perfect for recording the gondola ride"),
            ProductLink(P_TRIPOD, 1,
                "Estabiliza tus fotos en los canales de Venecia desde la gondola",
                "Stabilize your photos on Venice canals from the gondola"),
        ],
        detailed_es=(
            "Tu ultimo dia en Venecia. Un **paseo en gondola** (80 EUR / 30 min, negociable) "
            "es turistico pero magico: los canales estrechos, los puentes bajos y las "
            "fachadas desconchadas tienen un encanto unico.\n\n"
            "Despues, toma el tren a **Napoles** (5h30 con cambio en Roma, o vuelo 1h). Desde "
            "Napoles, un bus SITA por la **SS163** te deja en Positano con unas vistas "
            "que quitan el aliento.\n\n"
            "> **Tip:** La gondola es mas barata si la compartes con otra pareja; "
            "pregunta en el embarcadero si alguien quiere unirse."
        ),
        detailed_en=(
            "Your last day in Venice. A **gondola ride** (80 EUR / 30 min, negotiable) is "
            "touristy but magical: the narrow canals, low bridges and peeling facades have a "
            "unique charm.\n\n"
            "Then take the train to **Naples** (5h30 with change in Rome, or 1h flight). From "
            "Naples, a SITA bus along the **SS163** drops you in Positano with breathtaking "
            "views.\n\n"
            "> **Tip:** A gondola is cheaper if shared with another couple; "
            "ask at the dock if anyone wants to join."
        ),
    ),
    RouteStepSeed(
        day=9,
        products=[
            ProductLink(P_GOPRO, 0,
                "Sumergible: ideal para snorkel y el crucero por la costa Amalfitana",
                "Submersible: ideal for snorkeling and the Amalfi Coast cruise"),
            ProductLink(P_POWERBANK, 1,
                "Un dia entero en el mar; asegura bateria para fotos y GPS",
                "A full day at sea; ensure battery for photos and GPS"),
        ],
        detailed_es=(
            "Dia de mar en la **Costa Amalfitana**. El crucero en grupo reducido recorre "
            "cuevas escondidas, playas inaccesibles por tierra y paradas para snorkel en "
            "aguas turquesas.\n\n"
            "Positano desde el mar es hipnotico: las casas de colores apiladas en el acantilado "
            "con el azul del Tirreno de fondo. Almuerzo a bordo o en una trattoria costera.\n\n"
            "> **Tip:** Lleva proteccion solar alta y zapatos de agua; "
            "las playas de la Amalfitana son de guijarros, no de arena."
        ),
        detailed_en=(
            "A sea day on the **Amalfi Coast**. The small-group cruise visits hidden caves, "
            "beaches inaccessible by land and snorkeling stops in turquoise waters.\n\n"
            "Positano from the sea is mesmerizing: colorful houses stacked on the cliff with "
            "the blue Tyrrhenian as backdrop. Lunch on board or at a coastal trattoria.\n\n"
            "> **Tip:** Bring high SPF sunscreen and water shoes; "
            "Amalfi beaches are pebble, not sand."
        ),
    ),
]


# ---------------------------------------------------------------------------
# SPAIN - madrid-y-barcelona (7 days)
# ---------------------------------------------------------------------------
SPAIN_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_FANNY_PACK, 0,
                "Madrid tiene zonas con carteristas; lleva tus objetos de valor seguros",
                "Madrid has pickpocket areas; keep your valuables safe"),
            ProductLink(P_BOTTLE, 1,
                "El Retiro es enorme; lleva agua filtrada para el paseo",
                "Retiro is huge; bring filtered water for the walk"),
            ProductLink(P_POWERBANK, 2,
                "Dia largo de exploracion; no te quedes sin bateria para fotos",
                "Long day of exploring; don't run out of battery for photos"),
        ],
        detailed_es=(
            "Llegas a Madrid, capital de Espana. El traslado desde Barajas es rapido con "
            "el metro (L8 + L10, unos 40 min) o el Exprés Aeropuerto (bus 24h).\n\n"
            "Pasea por el **Parque del Retiro**: el Palacio de Cristal, el estanque con barcas "
            "y los jardines de Cecilio Rodriguez son imprescindibles. Al caer la tarde, baja "
            "a **La Latina** para tus primeras tapas: croquetas, patatas bravas y vermut.\n\n"
            "> **Tip:** Madrid tiene la hora de cenar mas tardia de Europa; "
            "los restaurantes se llenan a partir de las 21:30."
        ),
        detailed_en=(
            "You arrive in Madrid, Spain's capital. Transfer from Barajas is quick via "
            "metro (L8 + L10, about 40 min) or Airport Express bus (24h).\n\n"
            "Walk through **Retiro Park**: the Crystal Palace, the rowboat lake and Cecilio "
            "Rodriguez gardens are must-sees. As evening falls, head to **La Latina** for "
            "your first tapas: croquetas, patatas bravas and vermouth.\n\n"
            "> **Tip:** Madrid has the latest dinner time in Europe; "
            "restaurants fill up from 9:30 PM onwards."
        ),
    ),
    RouteStepSeed(
        day=3,
        products=[
            ProductLink(P_PILLOW, 0,
                "Almohada cervical perfecta para las 2.5 horas de AVE a Barcelona",
                "Neck pillow perfect for the 2.5-hour AVE to Barcelona"),
            ProductLink(P_HEADPHONES, 1,
                "Cancelacion de ruido para descansar en el AVE",
                "Noise cancelling to rest on the AVE"),
            ProductLink(P_KINDLE, 2,
                "Lectura ligera para el trayecto Madrid-Barcelona",
                "Light reading for the Madrid-Barcelona journey"),
        ],
        detailed_es=(
            "Manana en el **Mercado de San Miguel**: ostras, jamon iberico, croquetas y "
            "una copa de Ribera del Duero. Es caro pero la experiencia merece la pena. "
            "Despues, explora **Malasana**, el barrio mas hipster de Madrid.\n\n"
            "Por la tarde, toma el **AVE** a Barcelona (2h30, desde 25 EUR). El tren de alta "
            "velocidad es comodo y puntual; llegaras al centro de Barcelona directamente.\n\n"
            "> **Tip:** Reserva el AVE en renfe.com con antelacion; "
            "los billetes mesa (4 asientos con mesa) son geniales para grupos."
        ),
        detailed_en=(
            "Morning at **Mercado de San Miguel**: oysters, Iberian ham, croquettes and "
            "a glass of Ribera del Duero. It's pricey but the experience is worth it. "
            "Then explore **Malasana**, Madrid's hippest neighborhood.\n\n"
            "In the afternoon, catch the **AVE** to Barcelona (2h30, from 25 EUR). The "
            "high-speed train is comfortable and punctual; you'll arrive in central Barcelona "
            "directly.\n\n"
            "> **Tip:** Book the AVE on renfe.com in advance; "
            "mesa tickets (4 seats with table) are great for groups."
        ),
    ),
    RouteStepSeed(
        day=5,
        products=[
            ProductLink(P_GOPRO, 0,
                "Graba la arquitectura de Gaudi en calidad cinematografica",
                "Film Gaudi's architecture in cinematic quality"),
            ProductLink(P_TRIPOD, 1,
                "Estabiliza las fotos del interior de la Sagrada Familia con poca luz",
                "Stabilize low-light interior photos of the Sagrada Familia"),
        ],
        detailed_es=(
            "Hoy es el dia de Gaudi. Empieza con la **Sagrada Familia** (reserva obligatoria); "
            "la luz que entra por las vidrieras de colores es sobrecogedora. Sube a una de las "
            "torres para ver Barcelona desde arriba.\n\n"
            "Continua al **Park Guell** (zona monumental de pago): el banco ondulado, el dragon "
            "de mosaico y las vistas al mar son iconicos. Cena en el **Eixample**, el barrio "
            "modernista por excelencia.\n\n"
            "> **Tip:** Compra las entradas de Sagrada Familia y Park Guell con minimo "
            "2 semanas; se agotan especialmente en temporada alta."
        ),
        detailed_en=(
            "Today is Gaudi day. Start with the **Sagrada Familia** (booking required); "
            "the light streaming through the colored stained glass is breathtaking. Climb one "
            "of the towers for views over Barcelona.\n\n"
            "Continue to **Park Guell** (paid monumental zone): the wavy bench, mosaic dragon "
            "and sea views are iconic. Dinner in the **Eixample**, the modernist neighborhood "
            "par excellence.\n\n"
            "> **Tip:** Book Sagrada Familia and Park Guell tickets at least 2 weeks "
            "in advance; they sell out especially in high season."
        ),
    ),
    RouteStepSeed(
        day=6,
        products=[
            ProductLink(P_GOPRO, 0,
                "Resistente al agua para la playa de la Barceloneta",
                "Waterproof for Barceloneta beach"),
            ProductLink(P_BOTTLE, 1,
                "Hidratacion en la playa y durante la subida a Montjuic",
                "Hydration at the beach and during the Montjuic climb"),
        ],
        detailed_es=(
            "Dia de mar y montana. La **Barceloneta** es la playa urbana mas famosa de Europa: "
            "chiringuitos, voley y un paseo maritimo lleno de vida. No esperes arena fina, "
            "pero el ambiente es inigualable.\n\n"
            "Por la tarde, sube en **teleferico a Montjuic**: la Fundacion Miro, los jardines "
            "y las vistas del puerto al atardecer son espectaculares. Cena en uno de los "
            "restaurantes del puerto olimpico.\n\n"
            "> **Tip:** Evita dejar objetos de valor en la toalla; "
            "la Barceloneta tiene carteristas especialmente en verano."
        ),
        detailed_en=(
            "A day of sea and mountain. **Barceloneta** is Europe's most famous urban beach: "
            "chiringuitos, volleyball and a lively promenade. Don't expect fine sand, but the "
            "atmosphere is unmatched.\n\n"
            "In the afternoon, take the **cable car to Montjuic**: Fundacio Miro, the gardens "
            "and the sunset harbor views are spectacular. Dinner at one of the Olympic port "
            "restaurants.\n\n"
            "> **Tip:** Avoid leaving valuables on your towel; "
            "Barceloneta has pickpockets especially in summer."
        ),
    ),
]


# ---------------------------------------------------------------------------
# SLOVENIA & CROATIA - eslovenia-y-croacia (8 days)
# ---------------------------------------------------------------------------
SLOVENIA_CROATIA_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ADAPTER, 0,
                "Eslovenia usa enchufes tipo F; este adaptador universal te cubre",
                "Slovenia uses type F plugs; this universal adapter covers you"),
            ProductLink(P_ORGANIZERS, 1,
                "8 dias con multiples traslados en bus; organiza bien tu equipaje",
                "8 days with multiple bus transfers; organize your luggage well"),
        ],
        detailed_es=(
            "Ljubljana te recibe con su encanto de ciudad pequena y cosmopolita. Pasea por "
            "la **Plaza Preseren**, cruza el **Puente de los Dragones** y sientate en una "
            "terraza junto al rio Ljubljanica.\n\n"
            "La capital eslovena es peatonal en su centro historico desde 2007; todo se recorre "
            "a pie en unas horas. La escena gastronomica ha explotado: prueba la bureka "
            "y un vino de la region de Goriska Brda.\n\n"
            "> **Tip:** Eslovenia es mas barata que Croacia; aprovecha para cenar bien aqui."
        ),
        detailed_en=(
            "Ljubljana welcomes you with its charming small-city cosmopolitan feel. Walk "
            "through **Preseren Square**, cross the **Dragon Bridge** and sit at a terrace "
            "along the Ljubljanica river.\n\n"
            "The Slovenian capital has been car-free in its old town since 2007; everything is "
            "walkable within hours. The food scene has boomed: try burek and a wine from "
            "the Goriska Brda region.\n\n"
            "> **Tip:** Slovenia is cheaper than Croatia; take advantage and dine well here."
        ),
    ),
    RouteStepSeed(
        day=3,
        products=[
            ProductLink(P_GOPRO, 0,
                "El Lago Bled es uno de los paisajes mas fotografiados de Europa",
                "Lake Bled is one of Europe's most photographed landscapes"),
            ProductLink(P_TRIPOD, 1,
                "Trípode ligero para fotos del lago con el castillo de fondo",
                "Lightweight tripod for lake photos with the castle backdrop"),
        ],
        detailed_es=(
            "Excursion al **Lago Bled**: un lago glacial de cuento con una isla en el centro "
            "y un castillo en el acantilado. La barca **Pletna** (tradicional, sin motor) te "
            "lleva a la isla donde puedes tocar la campana de los deseos.\n\n"
            "Sube al **Castillo de Bled** para las mejores vistas; la entrada incluye un "
            "museo y una imprenta medieval. Almuerzo con kremsnita (tarta de crema), el "
            "postre tipico.\n\n"
            "> **Tip:** Madruga para llegar a Bled antes de las 10; "
            "la luz de la manana sobre el lago es magica y hay menos gente."
        ),
        detailed_en=(
            "Day trip to **Lake Bled**: a fairytale glacial lake with an island in the center "
            "and a castle on the cliff. The **Pletna** boat (traditional, no motor) takes "
            "you to the island where you can ring the wishing bell.\n\n"
            "Climb up to **Bled Castle** for the best views; entry includes a museum and a "
            "medieval printing press. Lunch with kremsnita (cream cake), the local specialty.\n\n"
            "> **Tip:** Arrive at Bled before 10 AM; "
            "the morning light on the lake is magical and there are fewer crowds."
        ),
    ),
    RouteStepSeed(
        day=6,
        products=[
            ProductLink(P_GOPRO, 0,
                "Imprescindible para las vistas panoramicas desde las murallas de Dubrovnik",
                "Essential for panoramic views from Dubrovnik's walls"),
            ProductLink(P_BOTTLE, 1,
                "Las murallas de Dubrovnik no tienen sombra; lleva agua",
                "Dubrovnik's walls have no shade; bring water"),
            ProductLink(P_FANNY_PACK, 2,
                "Manos libres para subir y bajar las escaleras de las murallas",
                "Hands-free for climbing up and down the wall stairs"),
        ],
        detailed_es=(
            "Hoy caminas sobre historia: las **Murallas de Dubrovnik** (1.94 km, 35 EUR) "
            "rodean todo el casco antiguo. Las vistas al Adriatico y los tejados de terracota "
            "son de las mejores del Mediterraneo.\n\n"
            "Dentro, la calle **Stradun** es el corazon: cafes, heladerias y tiendas. No te "
            "pierdas la catedral y el Palacio del Rector.\n\n"
            "> **Tip:** Recorre las murallas a primera hora (abren a las 8); "
            "al mediodia el sol y las colas son brutales."
        ),
        detailed_en=(
            "Today you walk on history: **Dubrovnik's Walls** (1.94 km, 35 EUR) encircle "
            "the entire old town. The Adriatic views and terracotta rooftops are among the "
            "best in the Mediterranean.\n\n"
            "Inside, **Stradun** street is the heart: cafes, gelato shops and stores. Don't "
            "miss the cathedral and the Rector's Palace.\n\n"
            "> **Tip:** Walk the walls first thing in the morning (they open at 8); "
            "by midday the sun and queues are brutal."
        ),
    ),
    RouteStepSeed(
        day=7,
        products=[
            ProductLink(P_GOPRO, 0,
                "La isla de Lokrum es perfecta para grabaciones acuaticas",
                "Lokrum island is perfect for water footage"),
            ProductLink(P_POWERBANK, 1,
                "Un dia de tour + isla; asegura bateria para fotos todo el dia",
                "A full day of tour + island; ensure battery for photos all day"),
        ],
        detailed_es=(
            "Dia de cine y naturaleza. Por la manana, **tour de Juego de Tronos**: visita "
            "las localizaciones de King's Landing (Fort Lovrijenac, escalinata jesuitica, "
            "Pile Gate). Dubrovnik ES Desembarco del Rey.\n\n"
            "Por la tarde, ferry a **Lokrum** (15 min, frecuente). La isla tiene un monasterio "
            "benedictino, un lago salado para banarse y pavos reales en libertad. Lleva "
            "banador y snorkel.\n\n"
            "> **Tip:** El ultimo ferry de Lokrum sale a las 18:00 (17:00 en temporada baja); "
            "no lo pierdas o te quedas en la isla."
        ),
        detailed_en=(
            "A day of cinema and nature. In the morning, **Game of Thrones tour**: visit "
            "King's Landing filming locations (Fort Lovrijenac, Jesuit staircase, Pile Gate). "
            "Dubrovnik IS King's Landing.\n\n"
            "In the afternoon, ferry to **Lokrum** (15 min, frequent). The island has a "
            "Benedictine monastery, a saltwater lake for swimming and free-roaming peacocks. "
            "Bring a swimsuit and snorkel.\n\n"
            "> **Tip:** The last Lokrum ferry leaves at 6 PM (5 PM in low season); "
            "don't miss it or you'll be stranded on the island."
        ),
    ),
]


# ---------------------------------------------------------------------------
# JAPAN - japon-esencial (12 days)
# ---------------------------------------------------------------------------
JAPAN_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ADAPTER, 0,
                "Japon usa enchufes tipo A/B (110V); necesitas adaptador para Europa",
                "Japan uses type A/B plugs (110V); you need an adapter for European devices"),
            ProductLink(P_ORGANIZERS, 1,
                "12 dias de viaje: organiza maleta por destino con cubos de equipaje",
                "12-day trip: organize suitcase by destination with packing cubes"),
            ProductLink(P_POWERBANK, 2,
                "Dia entero con Google Maps en un pais con otro alfabeto; bateria extra imprescindible",
                "Full day with Google Maps in a country with different alphabet; extra battery essential"),
        ],
        detailed_es=(
            "Bienvenido a Tokio, la ciudad mas fascinante del mundo. Desde Narita, "
            "el **Narita Express** (N'EX) te deja en Shinjuku en 80 min (3.250 JPY).\n\n"
            "Activa tu **Japan Rail Pass** (JR Pass) para el dia en que cojas el Shinkansen. "
            "Tu primera noche en Shinjuku: rascacielos, neon y una cena en un izakaya "
            "bajo las vias del tren (Memory Lane / Omoide Yokocho).\n\n"
            "> **Tip:** Compra una tarjeta Suica/Pasmo en el aeropuerto; "
            "funciona en metro, buses, konbinis y maquinas expendedoras."
        ),
        detailed_en=(
            "Welcome to Tokyo, the world's most fascinating city. From Narita, the "
            "**Narita Express** (N'EX) takes you to Shinjuku in 80 min (3,250 JPY).\n\n"
            "Activate your **Japan Rail Pass** (JR Pass) for the day you take the Shinkansen. "
            "Your first night in Shinjuku: skyscrapers, neon and dinner at an izakaya under "
            "the train tracks (Memory Lane / Omoide Yokocho).\n\n"
            "> **Tip:** Buy a Suica/Pasmo card at the airport; "
            "it works on metro, buses, konbinis and vending machines."
        ),
    ),
    RouteStepSeed(
        day=2,
        products=[
            ProductLink(P_GOPRO, 0,
                "Captura el cruce de Shibuya y la energia de Harajuku en 5.3K",
                "Capture the Shibuya crossing and Harajuku energy in 5.3K"),
            ProductLink(P_FANNY_PACK, 1,
                "Harajuku y Shibuya tienen mucha gente; lleva tus cosas seguras",
                "Harajuku and Shibuya are crowded; keep your things safe"),
        ],
        detailed_es=(
            "Empieza en el **Santuario Meiji-jingu**: un oasis de bosque en pleno Tokio. "
            "A la salida, la **calle Takeshita** en Harajuku es pura explosion de color y "
            "moda japonesa.\n\n"
            "Baja a **Shibuya**: el cruce mas famoso del mundo, Shibuya Sky (300m de altura) "
            "y la estatua de Hachiko. De noche, los bares de Shibuya y Ebisu son perfectos.\n\n"
            "> **Tip:** Visita Meiji-jingu a primera hora; "
            "si tienes suerte veras una boda sintoista tradicional."
        ),
        detailed_en=(
            "Start at **Meiji-jingu Shrine**: a forest oasis in the middle of Tokyo. "
            "Upon exit, **Takeshita Street** in Harajuku is a pure explosion of color and "
            "Japanese fashion.\n\n"
            "Head to **Shibuya**: the world's most famous crossing, Shibuya Sky (300m high) "
            "and the Hachiko statue. At night, bars in Shibuya and Ebisu are perfect.\n\n"
            "> **Tip:** Visit Meiji-jingu first thing in the morning; "
            "if you're lucky you'll see a traditional Shinto wedding."
        ),
    ),
    RouteStepSeed(
        day=5,
        products=[
            ProductLink(P_PILLOW, 0,
                "El Shinkansen a Kioto son 2h15; llega descansado con esta almohada",
                "The Shinkansen to Kyoto takes 2h15; arrive rested with this pillow"),
            ProductLink(P_HEADPHONES, 1,
                "Cancelacion de ruido perfecta para el tren bala",
                "Perfect noise cancelling for the bullet train"),
        ],
        detailed_es=(
            "Manana en **Ueno**: el parque, el Museo Nacional de Tokio y si es primavera, "
            "los cerezos en flor. Almuerzo en Ameya-Yokocho, el mercado callejero bajo las "
            "vias del tren.\n\n"
            "Por la tarde, **Shinkansen** a Kioto (2h15 con JR Pass). El tren bala es una "
            "experiencia en si mismo: puntual al segundo, limpio y con vistas al Monte Fuji "
            "si te sientas en el lado derecho.\n\n"
            "> **Tip:** Compra un ekiben (bento de estacion) en Tokyo Station; "
            "es tradicion japonesa comer en el Shinkansen."
        ),
        detailed_en=(
            "Morning in **Ueno**: the park, Tokyo National Museum and if it's spring, the "
            "cherry blossoms. Lunch at Ameya-Yokocho, the street market under the train "
            "tracks.\n\n"
            "In the afternoon, **Shinkansen** to Kyoto (2h15 with JR Pass). The bullet train "
            "is an experience in itself: punctual to the second, spotless and with views of "
            "Mt. Fuji if you sit on the right side.\n\n"
            "> **Tip:** Buy an ekiben (station bento) at Tokyo Station; "
            "it's a Japanese tradition to eat on the Shinkansen."
        ),
    ),
    RouteStepSeed(
        day=8,
        products=[
            ProductLink(P_GOPRO, 0,
                "Graba los ciervos de Nara y los templos de Kioto en alta calidad",
                "Film Nara's deer and Kyoto's temples in high quality"),
            ProductLink(P_TRIPOD, 1,
                "Tripode compacto para fotos estables en templos con poca luz",
                "Compact tripod for stable photos in dimly lit temples"),
        ],
        detailed_es=(
            "Doble plan hoy. Empieza en **Kiyomizudera**, el templo de la terraza de madera "
            "suspendida sobre el bosque. Las calles Ninenzaka y Sannenzaka que bajan son "
            "preciosas.\n\n"
            "Por la tarde, excursion a **Nara** (45 min en tren): los ciervos sagrados te "
            "saludan (literalmente hacen reverencia por galletas), el **Gran Buda de Todai-ji** "
            "impresiona y el parque es enorme.\n\n"
            "> **Tip:** No lleves comida a la vista en Nara; "
            "los ciervos son adorables pero insistentes y te rodearan."
        ),
        detailed_en=(
            "Double plan today. Start at **Kiyomizudera**, the temple with the wooden terrace "
            "suspended over the forest. The streets Ninenzaka and Sannenzaka leading down are "
            "beautiful.\n\n"
            "In the afternoon, day trip to **Nara** (45 min by train): the sacred deer greet "
            "you (they literally bow for crackers), the **Great Buddha at Todai-ji** is "
            "impressive and the park is vast.\n\n"
            "> **Tip:** Don't carry food in plain sight in Nara; "
            "the deer are adorable but pushy and will surround you."
        ),
    ),
    RouteStepSeed(
        day=12,
        products=[
            ProductLink(P_ORGANIZERS, 0,
                "Reorganiza tu maleta despues de 12 dias de compras en Japon",
                "Reorganize your suitcase after 12 days of shopping in Japan"),
            ProductLink(P_SAMSONITE, 1,
                "Si necesitas facturar recuerdos, una maleta solida es clave",
                "If you need to check souvenirs, a solid suitcase is key"),
        ],
        detailed_es=(
            "Ultimo dia. Manana libre para compras de ultima hora: si buscas recuerdos, "
            "el barrio de **Shinsekai** tiene tiendas retro y la Torre Tsutenkaku.\n\n"
            "Traslado al **Aeropuerto de Kansai** (tren Haruka, 75 min). Aprovecha el "
            "duty-free para comprar Kit-Kats de sabores japoneses, matcha y sake.\n\n"
            "> **Tip:** Si compraste mucho, Japon tiene envio de maletas por takkyubin "
            "(mensajeria); las envias desde el hotel al aeropuerto por unos 2.000 JPY."
        ),
        detailed_en=(
            "Last day. Free morning for last-minute shopping: if looking for souvenirs, "
            "**Shinsekai** neighborhood has retro shops and Tsutenkaku Tower.\n\n"
            "Transfer to **Kansai Airport** (Haruka train, 75 min). Use the duty-free for "
            "Japanese Kit-Kat flavors, matcha and sake.\n\n"
            "> **Tip:** If you bought a lot, Japan has luggage shipping by takkyubin "
            "(courier); you can send bags from your hotel to the airport for about 2,000 JPY."
        ),
    ),
]


# ---------------------------------------------------------------------------
# LONDON - londres-ciudad-imperial (5 days)
# ---------------------------------------------------------------------------
LONDON_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ADAPTER, 0,
                "Reino Unido usa enchufes tipo G; imprescindible un adaptador",
                "The UK uses type G plugs; an adapter is essential"),
            ProductLink(P_BACKPACK, 1,
                "Mochila de cabina ideal para moverte por el metro londinense",
                "Cabin backpack ideal for getting around the London Underground"),
            ProductLink(P_POWERBANK, 2,
                "Londres es enorme; necesitaras bateria para GPS todo el dia",
                "London is huge; you'll need battery for GPS all day"),
        ],
        detailed_es=(
            "Bienvenido a Londres. Desde Heathrow, el **Heathrow Express** (15 min a "
            "Paddington) o el **Piccadilly Line** (1h, mas barato) te llevan al centro.\n\n"
            "Tu primer paseo es por **Westminster**: Big Ben, la Abadia de Westminster, "
            "Buckingham Palace y St. James's Park. Si llegas antes de las 11:00, puedes "
            "ver el Cambio de Guardia (lunes, miercoles, viernes y domingos).\n\n"
            "> **Tip:** Consigue una Oyster Card o usa tu tarjeta contactless; "
            "el transporte en Londres es caro pero con tope diario."
        ),
        detailed_en=(
            "Welcome to London. From Heathrow, the **Heathrow Express** (15 min to Paddington) "
            "or the **Piccadilly Line** (1h, cheaper) take you to the center.\n\n"
            "Your first walk is through **Westminster**: Big Ben, Westminster Abbey, Buckingham "
            "Palace and St. James's Park. If you arrive before 11 AM, you can see the Changing "
            "of the Guard (Mon, Wed, Fri and Sun).\n\n"
            "> **Tip:** Get an Oyster Card or use your contactless card; "
            "London transport is pricey but has a daily cap."
        ),
    ),
    RouteStepSeed(
        day=3,
        products=[
            ProductLink(P_GOPRO, 0,
                "Graba cada rincon de los estudios de Harry Potter en alta definicion",
                "Record every corner of the Harry Potter studios in high definition"),
            ProductLink(P_TRIPOD, 1,
                "Fotos estables en los decorados oscuros de Hogwarts",
                "Stable photos in the dark Hogwarts sets"),
        ],
        detailed_es=(
            "Dia magico: **Warner Bros. Studio Tour - The Making of Harry Potter**. Reserva "
            "obligatoria (se agotan semanas antes). El autobus desde Watford Junction tarda "
            "15 min.\n\n"
            "Veras el Gran Comedor, el Callejon Diagon, el Hogwarts Express y maquetas "
            "increibles. Dedica al menos 4 horas. La tienda es enorme y peligrosa para "
            "tu cartera.\n\n"
            "> **Tip:** Llega 20 min antes de tu hora de entrada; "
            "hay colas para el autobus y para acceder a los estudios."
        ),
        detailed_en=(
            "Magical day: **Warner Bros. Studio Tour - The Making of Harry Potter**. Booking "
            "required (sells out weeks in advance). The bus from Watford Junction takes 15 min.\n\n"
            "You'll see the Great Hall, Diagon Alley, the Hogwarts Express and incredible "
            "models. Allow at least 4 hours. The shop is huge and dangerous for your wallet.\n\n"
            "> **Tip:** Arrive 20 min before your entry time; "
            "there are queues for the bus and to access the studios."
        ),
    ),
    RouteStepSeed(
        day=5,
        products=[
            ProductLink(P_HEADPHONES, 0,
                "Cancelacion de ruido para descansar en el vuelo de vuelta",
                "Noise cancelling to rest on the return flight"),
            ProductLink(P_PILLOW, 1,
                "Almohada cervical para dormir en el avion de regreso",
                "Neck pillow to sleep on the return plane"),
            ProductLink(P_KINDLE, 2,
                "Lectura ligera mientras esperas en el aeropuerto de Heathrow",
                "Light reading while waiting at Heathrow airport"),
        ],
        detailed_es=(
            "Ultimo dia. **Notting Hill** es el barrio mas colorido de Londres: casas pastel, "
            "el **Portobello Market** (sabados es el mejor dia) y librerias independientes.\n\n"
            "Pasea por **Hyde Park** para despedirte de la ciudad. Si tienes tiempo, el "
            "**London Eye** ofrece vistas de 360 grados de toda la ciudad (30 min de vuelta).\n\n"
            "> **Tip:** El Portobello Market tiene los mejores precios al fondo, "
            "lejos de la entrada de Notting Hill Gate; camina hasta el final."
        ),
        detailed_en=(
            "Last day. **Notting Hill** is London's most colorful neighborhood: pastel houses, "
            "**Portobello Market** (Saturdays are best) and independent bookshops.\n\n"
            "Walk through **Hyde Park** to say goodbye to the city. If you have time, the "
            "**London Eye** offers 360-degree views of the whole city (30 min ride).\n\n"
            "> **Tip:** Portobello Market has the best prices at the far end, "
            "away from the Notting Hill Gate entrance; walk to the end."
        ),
    ),
]


# ---------------------------------------------------------------------------
# NORWAY - fiordos-noruegos (7 days)
# ---------------------------------------------------------------------------
NORWAY_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ADAPTER, 0,
                "Noruega usa enchufes tipo F; este adaptador te cubre en toda Escandinavia",
                "Norway uses type F plugs; this adapter covers all of Scandinavia"),
            ProductLink(P_BACKPACK, 1,
                "Mochila resistente para un viaje con mucho senderismo y traslados",
                "Sturdy backpack for a trip with lots of hiking and transfers"),
        ],
        detailed_es=(
            "Llegas a Bergen, la puerta de los fiordos. Pasea por **Bryggen**, el muelle "
            "hanseatico con sus casas de madera de colores (Patrimonio UNESCO). El **Fish "
            "Market** (Fisketorget) es obligatorio: prueba el salmon fresco y las gambas.\n\n"
            "Bergen es la ciudad mas lluviosa de Europa (200+ dias/ano), asi que lleva "
            "siempre una chaqueta impermeable.\n\n"
            "> **Tip:** La Bergen Card (24/72h) incluye funicular, museos y transporte; "
            "se amortiza rapidamente."
        ),
        detailed_en=(
            "You arrive in Bergen, gateway to the fjords. Walk through **Bryggen**, the "
            "Hanseatic wharf with colorful wooden houses (UNESCO Heritage). The **Fish Market** "
            "(Fisketorget) is a must: try fresh salmon and shrimp.\n\n"
            "Bergen is Europe's rainiest city (200+ days/year), so always carry a waterproof "
            "jacket.\n\n"
            "> **Tip:** The Bergen Card (24/72h) includes funicular, museums and transport; "
            "it pays for itself quickly."
        ),
    ),
    RouteStepSeed(
        day=4,
        products=[
            ProductLink(P_GOPRO, 0,
                "El Geirangerfjord es Patrimonio UNESCO; grabalo sumergible en 5.3K",
                "Geirangerfjord is UNESCO Heritage; film it waterproof in 5.3K"),
            ProductLink(P_TRIPOD, 1,
                "Estabiliza las fotos desde el barco con oleaje",
                "Stabilize photos from the boat with waves"),
        ],
        detailed_es=(
            "El dia mas espectacular del viaje: crucero por el **Geirangerfjord** "
            "(Patrimonio UNESCO). 90 minutos navegando entre acantilados de 1.000 m, "
            "cascadas como las Siete Hermanas y el Pretendiente, y aguas verde esmeralda.\n\n"
            "Despues, traslado escenico a **Flam** por carreteras de montana con vistas "
            "que quitan el aliento.\n\n"
            "> **Tip:** Lleva ropa de abrigo incluso en verano; "
            "en el fiordo la temperatura baja 5-10 grados respecto a tierra."
        ),
        detailed_en=(
            "The most spectacular day of the trip: cruise through **Geirangerfjord** "
            "(UNESCO Heritage). 90 minutes sailing between 1,000 m cliffs, waterfalls like "
            "the Seven Sisters and the Suitor, and emerald-green waters.\n\n"
            "Then a scenic transfer to **Flam** via mountain roads with breathtaking views.\n\n"
            "> **Tip:** Bring warm clothing even in summer; "
            "in the fjord temperatures drop 5-10 degrees compared to land."
        ),
    ),
    RouteStepSeed(
        day=5,
        products=[
            ProductLink(P_GOPRO, 0,
                "El tren Flamsbana cruza 20 tuneles; grabalo todo con estabilizacion",
                "The Flamsbana train crosses 20 tunnels; record it all with stabilization"),
            ProductLink(P_KINDLE, 1,
                "Lectura perfecta para los trayectos lentos entre fiordos",
                "Perfect reading for the slow journeys between fjords"),
        ],
        detailed_es=(
            "Hoy te espera uno de los trayectos en tren mas bonitos del mundo: el "
            "**Flamsbana**. 20 km de descenso con 864 m de desnivel, 20 tuneles y la "
            "espectacular parada en la cascada Kjosfossen.\n\n"
            "Opcionalmente, un crucero por el **Naeroyfjord** (el fiordo mas estrecho del "
            "mundo, tambien UNESCO) completa un dia perfecto.\n\n"
            "> **Tip:** Sientate en el lado izquierdo del tren (direccion descenso) "
            "para las mejores vistas; y ten la camara lista en Kjosfossen."
        ),
        detailed_en=(
            "Today one of the world's most beautiful train journeys awaits: the "
            "**Flamsbana**. 20 km descent with 864 m elevation drop, 20 tunnels and the "
            "spectacular stop at Kjosfossen waterfall.\n\n"
            "Optionally, a cruise through **Naeroyfjord** (the narrowest fjord in the world, "
            "also UNESCO) completes a perfect day.\n\n"
            "> **Tip:** Sit on the left side of the train (going downhill) for the best "
            "views; and have your camera ready at Kjosfossen."
        ),
    ),
    RouteStepSeed(
        day=6,
        products=[
            ProductLink(P_GOPRO, 0,
                "Graba la subida al Preikestolen y las vistas del Lysefjord desde 604 m",
                "Record the Preikestolen hike and Lysefjord views from 604 m"),
            ProductLink(P_BOTTLE, 1,
                "4 horas de senderismo; hidratacion esencial con agua filtrada",
                "4 hours of hiking; essential hydration with filtered water"),
        ],
        detailed_es=(
            "El reto del viaje: la subida al **Preikestolen** (Pulpit Rock). Son 8 km "
            "(ida y vuelta), unas 4 horas, con desnivel moderado. La recompensa: una "
            "plataforma de roca plana a 604 m sobre el **Lysefjord**.\n\n"
            "Es una de las fotos mas impresionantes que haras en tu vida. El sendero esta "
            "bien marcado pero lleva calzado de montana, agua y algo de comer.\n\n"
            "> **Tip:** Empieza la subida antes de las 9; "
            "al mediodia la plataforma se llena y no podras hacer buenas fotos."
        ),
        detailed_en=(
            "The trip's challenge: the hike to **Preikestolen** (Pulpit Rock). It's 8 km "
            "round trip, about 4 hours, with moderate elevation. The reward: a flat rock "
            "platform 604 m above **Lysefjord**.\n\n"
            "It's one of the most impressive photos you'll ever take. The trail is well-marked "
            "but bring hiking boots, water and snacks.\n\n"
            "> **Tip:** Start the hike before 9 AM; "
            "by noon the platform gets crowded and good photos become difficult."
        ),
    ),
]


# ---------------------------------------------------------------------------
# KENYA - safari-en-kenia (8 days)
# ---------------------------------------------------------------------------
KENYA_STEPS: list[RouteStepSeed] = [
    RouteStepSeed(
        day=1,
        products=[
            ProductLink(P_ADAPTER, 0,
                "Kenia usa enchufes tipo G (como UK); lleva adaptador universal",
                "Kenya uses type G plugs (like UK); bring a universal adapter"),
            ProductLink(P_ORGANIZERS, 1,
                "8 dias de safari con traslados largos; organiza bien tu equipaje",
                "8-day safari with long transfers; organize your luggage well"),
            ProductLink(P_POWERBANK, 2,
                "Los lodges en reservas tienen electricidad limitada; lleva bateria extra",
                "Lodges in reserves have limited electricity; bring extra battery"),
        ],
        detailed_es=(
            "Llegas a Nairobi, capital de Kenia. Tu primera parada es el **Centro de "
            "Jirafas** donde puedes alimentar jirafas Rothschild cara a cara desde una "
            "plataforma elevada. Despues, visita el **Orfanato de Elefantes David Sheldrick** "
            "(solo abre 11:00-12:00; reserva online).\n\n"
            "Nairobi es una ciudad vibrante pero con precauciones de seguridad necesarias; "
            "no camines solo de noche y usa taxis de confianza (Bolt o Uber funcionan bien).\n\n"
            "> **Tip:** Cambia dinero en el aeropuerto solo lo minimo; "
            "el M-Pesa (pago movil) se usa en todas partes en Kenia."
        ),
        detailed_en=(
            "You arrive in Nairobi, Kenya's capital. Your first stop is the **Giraffe Centre** "
            "where you can feed Rothschild giraffes face to face from a raised platform. Then "
            "visit the **David Sheldrick Elephant Orphanage** (open 11 AM-12 PM only; book "
            "online).\n\n"
            "Nairobi is a vibrant city but requires security awareness; don't walk alone at "
            "night and use trusted taxis (Bolt or Uber work well).\n\n"
            "> **Tip:** Only change minimal money at the airport; "
            "M-Pesa (mobile payment) is used everywhere in Kenya."
        ),
    ),
    RouteStepSeed(
        day=3,
        products=[
            ProductLink(P_GOPRO, 0,
                "Captura los Big Five en safari con video 5.3K y estabilizacion",
                "Capture the Big Five on safari with 5.3K video and stabilization"),
            ProductLink(P_TRIPOD, 1,
                "Estabiliza fotos de fauna desde el vehiculo en movimiento",
                "Stabilize wildlife photos from the moving vehicle"),
            ProductLink(P_BOTTLE, 2,
                "Safaris de 8+ horas; hidratacion constante bajo el sol africano",
                "8+ hour safaris; constant hydration under the African sun"),
        ],
        detailed_es=(
            "El dia mas intenso del safari: **dia completo en el Masai Mara**. Safari al "
            "amanecer (5:30 AM) cuando los depredadores son mas activos. Bush breakfast en "
            "mitad de la sabana.\n\n"
            "Safari vespertino buscando los **Cinco Grandes**: leon, leopardo, elefante, "
            "bufalo y rinoceronte. El Mara es uno de los pocos lugares del mundo donde "
            "puedes verlos a todos en un dia.\n\n"
            "> **Tip:** Lleva prismaticos, proteccion solar alta y ropa de colores neutros "
            "(caqui, verde oliva); evita azul oscuro y negro que atraen tsetse."
        ),
        detailed_en=(
            "The most intense safari day: **full day in the Masai Mara**. Sunrise safari "
            "(5:30 AM) when predators are most active. Bush breakfast in the middle of the "
            "savanna.\n\n"
            "Afternoon safari seeking the **Big Five**: lion, leopard, elephant, buffalo and "
            "rhino. The Mara is one of the few places in the world where you can see them all "
            "in one day.\n\n"
            "> **Tip:** Bring binoculars, high SPF sunscreen and neutral-colored clothing "
            "(khaki, olive green); avoid dark blue and black which attract tsetse flies."
        ),
    ),
    RouteStepSeed(
        day=7,
        products=[
            ProductLink(P_GOPRO, 0,
                "El amanecer con elefantes y Kilimanjaro es el momento mas fotografico del viaje",
                "Sunrise with elephants and Kilimanjaro is the trip's most photogenic moment"),
            ProductLink(P_TRIPOD, 1,
                "Tripode para fotos de larga exposicion al amanecer africano",
                "Tripod for long-exposure photos at African sunrise"),
        ],
        detailed_es=(
            "El momento cumbre del viaje: **safari al amanecer en Amboseli** con el "
            "**Kilimanjaro** nevado de fondo. Las manadas de elefantes caminando ante la "
            "montana mas alta de Africa es la imagen mas iconica del continente.\n\n"
            "Amboseli tiene los elefantes mas grandes y con colmillos mas largos de toda "
            "Kenia. Los flamencos del lago y las garzas completan el paisaje.\n\n"
            "> **Tip:** El Kilimanjaro suele estar despejado al amanecer y se nubla "
            "a partir de las 10 AM; madruga o te lo perderas."
        ),
        detailed_en=(
            "The trip's peak moment: **sunrise safari in Amboseli** with the snow-capped "
            "**Kilimanjaro** as backdrop. Elephant herds walking before Africa's highest "
            "mountain is the continent's most iconic image.\n\n"
            "Amboseli has Kenya's largest elephants with the longest tusks. Flamingos on the "
            "lake and herons complete the landscape.\n\n"
            "> **Tip:** Kilimanjaro is usually clear at sunrise and clouds over by "
            "10 AM; wake up early or you'll miss it."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Master map: pack_slug → list of RouteStepSeed
# ---------------------------------------------------------------------------
PACK_ROUTE_PRODUCTS: dict[str, list[RouteStepSeed]] = {
    "paris-ciudad-de-la-luz": PARIS_STEPS,
    "ruta-por-italia": ITALY_STEPS,
    "madrid-y-barcelona": SPAIN_STEPS,
    "eslovenia-y-croacia": SLOVENIA_CROATIA_STEPS,
    "japon-esencial": JAPAN_STEPS,
    "londres-ciudad-imperial": LONDON_STEPS,
    "fiordos-noruegos": NORWAY_STEPS,
    "safari-en-kenia": KENYA_STEPS,
}


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------
async def seed_route_products() -> None:
    """Populate route_step_products and detailed_description for all packs."""
    async with async_session_factory() as session:
        # Check idempotency
        from sqlalchemy import func as sa_func
        result = await session.execute(
            select(sa_func.count()).select_from(RouteStepProduct)
        )
        if result.scalar() > 0:
            print("Route-step products already seeded, skipping...")
            return

        # Load all products indexed by slug
        prod_result = await session.execute(select(Product))
        products_by_slug: dict[str, Product] = {
            p.slug: p for p in prod_result.scalars().all()
        }

        # Load all packs with route steps + translations
        packs_result = await session.execute(
            select(Pack)
            .options(
                selectinload(Pack.route_steps).selectinload(RouteStep.translations),
            )
        )
        packs_by_slug: dict[str, Pack] = {
            p.slug: p for p in packs_result.scalars().all()
        }

        total_links = 0
        total_descriptions = 0

        for pack_slug, step_seeds in PACK_ROUTE_PRODUCTS.items():
            pack = packs_by_slug.get(pack_slug)
            if not pack:
                print(f"  WARN: Pack '{pack_slug}' not found, skipping...")
                continue

            # Index route steps by day
            steps_by_day: dict[int, RouteStep] = {
                rs.day: rs for rs in pack.route_steps
            }

            for seed in step_seeds:
                route_step = steps_by_day.get(seed.day)
                if not route_step:
                    print(f"  WARN: Day {seed.day} not found in '{pack_slug}', skipping...")
                    continue

                # Create product links
                for pl in seed.products:
                    product = products_by_slug.get(pl.product_slug)
                    if not product:
                        print(f"  WARN: Product '{pl.product_slug}' not found, skipping...")
                        continue

                    rsp = RouteStepProduct(
                        id=uuid.uuid4(),
                        route_step_id=route_step.id,
                        product_id=product.id,
                        position=pl.position,
                        context_text=pl.context_es,
                    )
                    session.add(rsp)
                    total_links += 1

                # Update detailed_description on translations
                if seed.detailed_es or seed.detailed_en:
                    for trans in route_step.translations:
                        if trans.locale == "es" and seed.detailed_es:
                            trans.detailed_description = seed.detailed_es
                            total_descriptions += 1
                        elif trans.locale == "en" and seed.detailed_en:
                            trans.detailed_description = seed.detailed_en
                            total_descriptions += 1

        await session.commit()
        print(f"Seeded {total_links} route-step-product links and "
              f"{total_descriptions} detailed descriptions!")


if __name__ == "__main__":
    asyncio.run(seed_route_products())
