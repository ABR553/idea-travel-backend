#!/usr/bin/env python3
"""Seed route-step products and detailed descriptions via HTTP API.

Discovers available products from the target API, maps them by role,
then POSTs enrichment data pack by pack.

Usage:
    BASE_URL=https://api.tengounviaje.com ADMIN_SECRET=xxx python -m app.seeds.seed_route_products_http

Variables de entorno:
    BASE_URL        URL base de la API (default: https://api.tengounviaje.com)
    ADMIN_SECRET    Clave de admin para endpoints protegidos (requerida)
"""

import os
import sys

import requests

# ─── Config ──────────────────────────────────────────────────────────────────

BASE_URL: str = os.getenv("BASE_URL", "https://api.tengounviaje.com").rstrip("/")
ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "")

PRODUCTS_URL: str = f"{BASE_URL}/api/v1/products?locale=es&limit=100"
ENRICH_URL: str = f"{BASE_URL}/api/v1/seed-route-products"


# ─── Product role mapping ────────────────────────────────────────────────────
# Each role maps to (category_keywords, name_keywords) for auto-discovery.

PRODUCT_ROLES: dict[str, tuple[list[str], list[str]]] = {
    "adapter":    (["electronics", "tecnologia"],       ["adaptador", "adapter", "enchufe"]),
    "powerbank":  (["electronics", "tecnologia"],       ["powerbank", "power bank", "anker", "bateria"]),
    "headphones": (["electronics", "tecnologia"],       ["auricular", "headphone", "sony", "noise"]),
    "gopro":      (["photography", "camaras_accion"],   ["gopro", "hero"]),
    "tripod":     (["photography"],                     ["tripode", "tripod"]),
    "pillow":     (["comfort", "accesorios_confort"],   ["almohada", "pillow", "cervical"]),
    "kindle":     (["comfort", "electronics"],          ["kindle", "ebook", "e-reader"]),
    "organizers": (["luggage", "maletas"],              ["organizador", "organizer", "cubo", "packing"]),
    "backpack":   (["luggage", "mochilas_cabina"],      ["mochila", "backpack"]),
    "samsonite":  (["luggage", "maletas"],              ["maleta", "samsonite", "spinner", "suitcase"]),
    "bottle":     (["accessories", "accesorios_confort"], ["botella", "bottle", "agua", "water", "filtrant"]),
    "fanny_pack": (["accessories", "accesorios_confort"], ["rinonera", "fanny", "antirrobo", "anti-theft"]),
    "scale":      (["electronics", "tecnologia"],       ["bascula", "scale", "pesa"]),
    "sleep_mask": (["comfort", "accesorios_confort"],   ["antifaz", "sleep mask", "eye mask"]),
    "earplugs":   (["comfort", "accesorios_confort"],   ["tapones", "earplugs", "ear plug"]),
    "action_cam": (["photography", "camaras_accion"],   ["action", "dji", "osmo", "camara"]),
    "tsa_lock":   (["accessories", "candados_tsa"],     ["candado", "lock", "tsa"]),
}


def discover_products(session: requests.Session) -> dict[str, str]:
    """Fetch products from the API and map each role to an actual slug."""
    print("Discovering products from API...")
    resp = session.get(PRODUCTS_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", data) if isinstance(data, dict) else data

    print(f"  Found {len(items)} products")

    # Build role → slug mapping
    # Require BOTH category AND keyword match (on name/slug only, not description)
    role_to_slug: dict[str, str] = {}
    used_slugs: set[str] = set()  # prevent same product mapped to multiple roles

    for role, (cats, keywords) in PRODUCT_ROLES.items():
        best_match: str | None = None
        for item in items:
            cat = (item.get("category") or "").lower()
            name = (item.get("name") or "").lower()
            slug = item.get("slug", "")
            searchable = f"{name} {slug}"  # only name and slug, NOT description

            cat_match = any(c.lower() in cat for c in cats)
            kw_match = any(kw.lower() in searchable for kw in keywords)

            if cat_match and kw_match and slug not in used_slugs:
                best_match = slug
                break

        if best_match:
            role_to_slug[role] = best_match
            used_slugs.add(best_match)
            print(f"  {role:15s} → {best_match[:60]}")
        else:
            print(f"  {role:15s} → NOT FOUND")

    return role_to_slug


# ─── Step builder helper ─────────────────────────────────────────────────────

def step(
    day: int,
    products: list[tuple[str, int, str]],
    desc_es: str,
    desc_en: str,
) -> dict:
    """Build a step dict for the API payload.

    products: list of (role_key, position, context_text)
    """
    return {
        "day": day,
        "products": [
            {"product_slug": role, "position": pos, "context_text": ctx}
            for role, pos, ctx in products
        ],
        "detailed_description_es": desc_es,
        "detailed_description_en": desc_en,
    }


# ─── Pack enrichment data ────────────────────────────────────────────────────

def build_all_packs() -> dict[str, list[dict]]:
    """Return {pack_slug: [step_dicts]} with role keys as product slugs."""
    return {
        "paris-ciudad-de-la-luz": [
            step(1, [
                ("organizers", 0, "Lleva la maleta organizada desde el primer dia con estos cubos de equipaje"),
                ("adapter", 1, "Francia usa enchufes tipo E; este adaptador te cubre en toda Europa"),
                ("powerbank", 2, "Google Maps, fotos y redes consumen bateria; lleva siempre carga extra"),
            ],
                "Aterrizas en Paris y comienza la aventura. Tras recoger tu equipaje, el trayecto al centro es sencillo con el RER B (unos 50 min desde CDG).\n\nPasea por la **Place des Vosges**, la plaza mas antigua de Paris, y acercate a **Notre-Dame** para ver el avance de su restauracion. Pierdete por las calles de Le Marais, donde cada esquina esconde una boulangerie o una galeria de arte.\n\n> **Tip:** Compra la tarjeta Navigo Decouverte (semana) si llegas en lunes; amortizas metro y RER ilimitados por ~30 EUR.",
                "You land in Paris and the adventure begins. After collecting your luggage, getting to the center is easy via RER B (about 50 min from CDG).\n\nStroll through **Place des Vosges**, the oldest planned square in Paris, and stop by **Notre-Dame** to see the restoration progress. Wander through Le Marais, where every corner hides a boulangerie or art gallery.\n\n> **Tip:** Buy the Navigo Decouverte weekly pass if you arrive on Monday; you'll get unlimited metro & RER for ~30 EUR.",
            ),
            step(2, [
                ("gopro", 0, "Captura la grandiosidad del Louvre y sus obras maestras en alta calidad"),
                ("fanny_pack", 1, "Lleva documentos, movil y cartera seguros en el museo mas visitado del mundo"),
            ],
                "Reserva la **entrada al Louvre** con hora. Sin reserva, la cola puede superar las 2 horas. Dedica al menos 3 horas: la Mona Lisa, la Venus de Milo y la Victoria de Samotracia son imprescindibles, pero el ala de arte islamico es una joya escondida.\n\nDespues, pasea por el **Jardin de las Tullerias** hasta la Place de la Concorde. Si el dia acompana, es perfecto para un cafe en una terraza.\n\n> **Tip:** Los miercoles y viernes el Louvre cierra a las 21:45; la visita nocturna es mas tranquila y atmosferica.",
                "Book your **Louvre timed entry** in advance. Without a reservation, the queue can exceed 2 hours. Allow at least 3 hours: the Mona Lisa, Venus de Milo and Winged Victory are must-sees, but the Islamic Art wing is a hidden gem.\n\nAfterwards, stroll through the **Tuileries Garden** to Place de la Concorde. If the weather is good, perfect for a terrace coffee.\n\n> **Tip:** On Wednesdays and Fridays the Louvre stays open until 9:45 PM; the evening visit is calmer and more atmospheric.",
            ),
            step(3, [
                ("gopro", 0, "Graba la Torre Eiffel y las vistas desde la cima en 5.3K"),
                ("tripod", 1, "Imprescindible para timelapses y fotos nocturnas de la torre iluminada"),
            ],
                "Hoy toca el icono: la **Torre Eiffel**. Si subes a la cima, reserva con semanas de antelacion (se agotan rapido). La segunda planta tiene las mejores vistas para fotos sin cristal.\n\nBaja caminando por el **Champ de Mars** y cruza el puente hacia el Trocadero para la foto clasica. Sigue por los **Champs-Elysees** hasta el Arco del Triunfo; la subida merece la pena al atardecer.\n\n> **Tip:** Lleva un picnic al Champ de Mars: una baguette, queso y una botella de vino. Es la experiencia mas parisina que puedes vivir.",
                "Today is the icon: the **Eiffel Tower**. If you're going to the top, book weeks in advance (slots sell out fast). The second floor has the best views for photos without glass.\n\nWalk down through the **Champ de Mars** and cross the bridge to Trocadero for the classic photo. Continue along the **Champs-Elysees** to the Arc de Triomphe; the climb is worth it at sunset.\n\n> **Tip:** Bring a picnic to the Champ de Mars: a baguette, cheese and a bottle of wine. It's the most Parisian experience you can have.",
            ),
            step(4, [
                ("bottle", 0, "Montmartre tiene cuestas empinadas; hidratate con agua filtrada"),
                ("backpack", 1, "Mochila de cabina perfecta para la excursion a Montmartre"),
            ],
                "Sube a **Montmartre** temprano, antes de que lleguen las multitudes. La basilica del **Sacre-Coeur** ofrece vistas de 360 grados de Paris desde su cupula.\n\nExplora la **Place du Tertre** donde pintores y retratistas trabajan al aire libre. Baja por callejuelas hasta el **Moulin Rouge** (la foto exterior es gratis). El barrio es perfecto para perderse sin mapa.\n\n> **Tip:** Prueba un crepe de Nutella en las creperies de la Rue Lepic; las mas autenticas estan alejadas de la plaza principal.",
                "Head up to **Montmartre** early, before the crowds arrive. The **Sacre-Coeur** basilica offers 360-degree views of Paris from its dome.\n\nExplore **Place du Tertre** where painters and portrait artists work outdoors. Wind down through alleys to the **Moulin Rouge** (the exterior photo is free). This neighborhood is perfect for wandering without a map.\n\n> **Tip:** Try a Nutella crepe at the creperies on Rue Lepic; the most authentic ones are away from the main square.",
            ),
            step(5, [
                ("headphones", 0, "Cancelacion de ruido para descansar en el vuelo de vuelta"),
                ("pillow", 1, "Almohada cervical para dormir comodo en el avion"),
                ("kindle", 2, "Lectura ligera para las horas de espera y el vuelo de regreso"),
            ],
                "Ultimo dia en Paris. Dedica la manana al **Museo d'Orsay**, la catedral del impresionismo: Monet, Renoir, Degas y Van Gogh te esperan. El edificio, una antigua estacion de tren, es una obra de arte en si mismo.\n\nDespues, pasea por **Saint-Germain-des-Pres**: la libreria Shakespeare & Company, el Cafe de Flore y Les Deux Magots son paradas obligadas. Ultimo macaron en Laduree antes de despedirte.\n\n> **Tip:** La tarjeta Paris Museum Pass (2 dias) cubre Orsay, Louvre y otros 50 museos. Si no la compraste antes, el Orsay solo merece las 2-3 horas.",
                "Last day in Paris. Spend the morning at the **Musee d'Orsay**, the cathedral of Impressionism: Monet, Renoir, Degas and Van Gogh await. The building, a former train station, is a work of art itself.\n\nThen stroll through **Saint-Germain-des-Pres**: Shakespeare & Company bookshop, Cafe de Flore and Les Deux Magots are must-stops. Last macaron at Laduree before saying goodbye.\n\n> **Tip:** The Paris Museum Pass (2 days) covers Orsay, Louvre and 50+ other museums. If you didn't buy it earlier, Orsay alone is worth the 2-3 hours.",
            ),
        ],
        "ruta-por-italia": [
            step(1, [("organizers", 0, "10 dias multi-ciudad; los cubos de equipaje son esenciales"), ("adapter", 1, "Italia usa enchufes tipo L; con este adaptador cargas todo"), ("fanny_pack", 2, "Roma tiene carteristas; lleva tus objetos de valor seguros")],
                "Bienvenido a Roma. El traslado desde Fiumicino al centro es rapido con el **Leonardo Express** (32 min a Termini, 14 EUR).\n\nTu primer paseo es por **Trastevere**, el barrio mas autentico: callejuelas empedradas, ropa tendida entre balcones y trattorias familiares. Cena junto al **Panteon** (entrada gratuita) iluminado de noche.\n\n> **Tip:** Prueba la supplì (croqueta de arroz romana) en Supplizio; es el mejor aperitivo para empezar tu viaje italiano.",
                "Welcome to Rome. Transfer from Fiumicino to the center is quick via the **Leonardo Express** (32 min to Termini, 14 EUR).\n\nYour first walk is through **Trastevere**, the most authentic neighborhood: cobblestone alleys, laundry hanging between balconies and family-run trattorias. Dinner by the **Pantheon** (free entry) lit up at night.\n\n> **Tip:** Try the supplì (Roman rice croquette) at Supplizio; it's the best appetizer to kick off your Italian trip.",
            ),
            step(3, [("pillow", 0, "Comodidad extra para el tren Frecciarossa Roma-Florencia (1h30)"), ("headphones", 1, "Cancelacion de ruido para descansar en el tren"), ("kindle", 2, "Lectura perfecta para los trayectos en tren por Italia")],
                "Ultimo dia en Roma antes del tren. Empieza en la **Plaza Navona** con sus tres fuentes barrocas (la de Bernini es espectacular). Lanza una moneda en la **Fontana di Trevi** (1 moneda = volveras a Roma) y visita el Panteon por dentro.\n\nPor la tarde, toma el **Frecciarossa** a Florencia (1h30, desde 19 EUR si reservas con antelacion). Llegaras justo para una passeggiata por el Ponte Vecchio al atardecer.\n\n> **Tip:** Compra los billetes de Trenitalia con 2-3 semanas de antelacion; los precios suben mucho en fechas cercanas.",
                "Last day in Rome before the train. Start at **Piazza Navona** with its three baroque fountains (Bernini's is spectacular). Toss a coin in the **Trevi Fountain** (1 coin = you'll return to Rome) and visit the Pantheon inside.\n\nIn the afternoon, catch the **Frecciarossa** to Florence (1h30, from 19 EUR if booked in advance). You'll arrive just in time for a passeggiata over the Ponte Vecchio at sunset.\n\n> **Tip:** Buy Trenitalia tickets 2-3 weeks ahead; prices increase significantly closer to the date.",
            ),
            step(5, [("gopro", 0, "Graba los vinedos del Chianti con calidad cinematografica"), ("bottle", 1, "Hidratacion esencial durante la excursion por las colinas toscanas")],
                "Dia de escapada al campo toscano. Una **excursion al Chianti** te lleva por colinas de cipresses, dos bodegas con cata de Chianti Classico DOCG y un almuerzo con productos km 0.\n\nLos paisajes son de postal: vinedos infinitos, casas de piedra y pueblos como Greve in Chianti o Castellina. Si vas por libre, alquila un coche o reserva un tour en grupo reducido.\n\n> **Tip:** No conduzcas si vas a catar; los controles de alcoholemia en las carreteras toscanas son frecuentes.",
                "A day trip to the Tuscan countryside. A **Chianti excursion** takes you through cypress hills, two wineries with Chianti Classico DOCG tastings and a lunch with local km-0 products.\n\nThe landscapes are postcard-perfect: endless vineyards, stone houses and villages like Greve in Chianti or Castellina. If going independently, rent a car or book a small group tour.\n\n> **Tip:** Don't drive if you're tasting; drink-driving checkpoints on Tuscan roads are frequent.",
            ),
            step(8, [("gopro", 0, "Resistente al agua: perfecta para grabar el paseo en gondola"), ("tripod", 1, "Estabiliza tus fotos en los canales de Venecia")],
                "Tu ultimo dia en Venecia. Un **paseo en gondola** (80 EUR / 30 min, negociable) es turistico pero magico: los canales estrechos, los puentes bajos y las fachadas desconchadas tienen un encanto unico.\n\nDespues, toma el tren a **Napoles** (5h30 con cambio en Roma, o vuelo 1h). Desde Napoles, un bus SITA por la **SS163** te deja en Positano con unas vistas que quitan el aliento.\n\n> **Tip:** La gondola es mas barata si la compartes con otra pareja; pregunta en el embarcadero si alguien quiere unirse.",
                "Your last day in Venice. A **gondola ride** (80 EUR / 30 min, negotiable) is touristy but magical: the narrow canals, low bridges and peeling facades have a unique charm.\n\nThen take the train to **Naples** (5h30 with change in Rome, or 1h flight). From Naples, a SITA bus along the **SS163** drops you in Positano with breathtaking views.\n\n> **Tip:** A gondola is cheaper if shared with another couple; ask at the dock if anyone wants to join.",
            ),
            step(9, [("gopro", 0, "Sumergible: ideal para snorkel y el crucero por la costa Amalfitana"), ("powerbank", 1, "Un dia entero en el mar; asegura bateria para fotos y GPS")],
                "Dia de mar en la **Costa Amalfitana**. El crucero en grupo reducido recorre cuevas escondidas, playas inaccesibles por tierra y paradas para snorkel en aguas turquesas.\n\nPositano desde el mar es hipnotico: las casas de colores apiladas en el acantilado con el azul del Tirreno de fondo. Almuerzo a bordo o en una trattoria costera.\n\n> **Tip:** Lleva proteccion solar alta y zapatos de agua; las playas de la Amalfitana son de guijarros, no de arena.",
                "A sea day on the **Amalfi Coast**. The small-group cruise visits hidden caves, beaches inaccessible by land and snorkeling stops in turquoise waters.\n\nPositano from the sea is mesmerizing: colorful houses stacked on the cliff with the blue Tyrrhenian as backdrop. Lunch on board or at a coastal trattoria.\n\n> **Tip:** Bring high SPF sunscreen and water shoes; Amalfi beaches are pebble, not sand.",
            ),
        ],
        "madrid-y-barcelona": [
            step(1, [("fanny_pack", 0, "Madrid tiene zonas con carteristas; lleva tus objetos de valor seguros"), ("bottle", 1, "El Retiro es enorme; lleva agua filtrada para el paseo"), ("powerbank", 2, "Dia largo de exploracion; no te quedes sin bateria")],
                "Llegas a Madrid, capital de Espana. El traslado desde Barajas es rapido con el metro (L8 + L10, unos 40 min) o el Exprés Aeropuerto (bus 24h).\n\nPasea por el **Parque del Retiro**: el Palacio de Cristal, el estanque con barcas y los jardines de Cecilio Rodriguez son imprescindibles. Al caer la tarde, baja a **La Latina** para tus primeras tapas: croquetas, patatas bravas y vermut.\n\n> **Tip:** Madrid tiene la hora de cenar mas tardia de Europa; los restaurantes se llenan a partir de las 21:30.",
                "You arrive in Madrid, Spain's capital. Transfer from Barajas is quick via metro (L8 + L10, about 40 min) or Airport Express bus (24h).\n\nWalk through **Retiro Park**: the Crystal Palace, the rowboat lake and Cecilio Rodriguez gardens are must-sees. As evening falls, head to **La Latina** for your first tapas: croquetas, patatas bravas and vermouth.\n\n> **Tip:** Madrid has the latest dinner time in Europe; restaurants fill up from 9:30 PM onwards.",
            ),
            step(3, [("pillow", 0, "Almohada cervical perfecta para las 2.5 horas de AVE a Barcelona"), ("headphones", 1, "Cancelacion de ruido para descansar en el AVE"), ("kindle", 2, "Lectura ligera para el trayecto Madrid-Barcelona")],
                "Manana en el **Mercado de San Miguel**: ostras, jamon iberico, croquetas y una copa de Ribera del Duero. Es caro pero la experiencia merece la pena. Despues, explora **Malasana**, el barrio mas hipster de Madrid.\n\nPor la tarde, toma el **AVE** a Barcelona (2h30, desde 25 EUR). El tren de alta velocidad es comodo y puntual; llegaras al centro de Barcelona directamente.\n\n> **Tip:** Reserva el AVE en renfe.com con antelacion; los billetes mesa (4 asientos con mesa) son geniales para grupos.",
                "Morning at **Mercado de San Miguel**: oysters, Iberian ham, croquettes and a glass of Ribera del Duero. It's pricey but the experience is worth it. Then explore **Malasana**, Madrid's hippest neighborhood.\n\nIn the afternoon, catch the **AVE** to Barcelona (2h30, from 25 EUR). The high-speed train is comfortable and punctual; you'll arrive in central Barcelona directly.\n\n> **Tip:** Book the AVE on renfe.com in advance; mesa tickets (4 seats with table) are great for groups.",
            ),
            step(5, [("gopro", 0, "Graba la arquitectura de Gaudi en calidad cinematografica"), ("tripod", 1, "Estabiliza las fotos del interior de la Sagrada Familia")],
                "Hoy es el dia de Gaudi. Empieza con la **Sagrada Familia** (reserva obligatoria); la luz que entra por las vidrieras de colores es sobrecogedora. Sube a una de las torres para ver Barcelona desde arriba.\n\nContinua al **Park Guell** (zona monumental de pago): el banco ondulado, el dragon de mosaico y las vistas al mar son iconicos. Cena en el **Eixample**, el barrio modernista por excelencia.\n\n> **Tip:** Compra las entradas de Sagrada Familia y Park Guell con minimo 2 semanas; se agotan especialmente en temporada alta.",
                "Today is Gaudi day. Start with the **Sagrada Familia** (booking required); the light streaming through the colored stained glass is breathtaking. Climb one of the towers for views over Barcelona.\n\nContinue to **Park Guell** (paid monumental zone): the wavy bench, mosaic dragon and sea views are iconic. Dinner in the **Eixample**, the modernist neighborhood par excellence.\n\n> **Tip:** Book Sagrada Familia and Park Guell tickets at least 2 weeks in advance; they sell out especially in high season.",
            ),
            step(6, [("gopro", 0, "Resistente al agua para la playa de la Barceloneta"), ("bottle", 1, "Hidratacion en la playa y durante la subida a Montjuic")],
                "Dia de mar y montana. La **Barceloneta** es la playa urbana mas famosa de Europa: chiringuitos, voley y un paseo maritimo lleno de vida. No esperes arena fina, pero el ambiente es inigualable.\n\nPor la tarde, sube en **teleferico a Montjuic**: la Fundacion Miro, los jardines y las vistas del puerto al atardecer son espectaculares. Cena en uno de los restaurantes del puerto olimpico.\n\n> **Tip:** Evita dejar objetos de valor en la toalla; la Barceloneta tiene carteristas especialmente en verano.",
                "A day of sea and mountain. **Barceloneta** is Europe's most famous urban beach: chiringuitos, volleyball and a lively promenade. Don't expect fine sand, but the atmosphere is unmatched.\n\nIn the afternoon, take the **cable car to Montjuic**: Fundacio Miro, the gardens and the sunset harbor views are spectacular. Dinner at one of the Olympic port restaurants.\n\n> **Tip:** Avoid leaving valuables on your towel; Barceloneta has pickpockets especially in summer.",
            ),
        ],
        "eslovenia-y-croacia": [
            step(1, [("adapter", 0, "Eslovenia usa enchufes tipo F; este adaptador universal te cubre"), ("organizers", 1, "8 dias con multiples traslados en bus; organiza bien tu equipaje")],
                "Ljubljana te recibe con su encanto de ciudad pequena y cosmopolita. Pasea por la **Plaza Preseren**, cruza el **Puente de los Dragones** y sientate en una terraza junto al rio Ljubljanica.\n\nLa capital eslovena es peatonal en su centro historico desde 2007; todo se recorre a pie en unas horas. La escena gastronomica ha explotado: prueba la bureka y un vino de la region de Goriska Brda.\n\n> **Tip:** Eslovenia es mas barata que Croacia; aprovecha para cenar bien aqui.",
                "Ljubljana welcomes you with its charming small-city cosmopolitan feel. Walk through **Preseren Square**, cross the **Dragon Bridge** and sit at a terrace along the Ljubljanica river.\n\nThe Slovenian capital has been car-free in its old town since 2007; everything is walkable within hours. The food scene has boomed: try burek and a wine from the Goriska Brda region.\n\n> **Tip:** Slovenia is cheaper than Croatia; take advantage and dine well here.",
            ),
            step(3, [("gopro", 0, "El Lago Bled es uno de los paisajes mas fotografiados de Europa"), ("tripod", 1, "Tripode ligero para fotos del lago con el castillo de fondo")],
                "Excursion al **Lago Bled**: un lago glacial de cuento con una isla en el centro y un castillo en el acantilado. La barca **Pletna** (tradicional, sin motor) te lleva a la isla donde puedes tocar la campana de los deseos.\n\nSube al **Castillo de Bled** para las mejores vistas; la entrada incluye un museo y una imprenta medieval. Almuerzo con kremsnita (tarta de crema), el postre tipico.\n\n> **Tip:** Madruga para llegar a Bled antes de las 10; la luz de la manana sobre el lago es magica y hay menos gente.",
                "Day trip to **Lake Bled**: a fairytale glacial lake with an island in the center and a castle on the cliff. The **Pletna** boat (traditional, no motor) takes you to the island where you can ring the wishing bell.\n\nClimb up to **Bled Castle** for the best views; entry includes a museum and a medieval printing press. Lunch with kremsnita (cream cake), the local specialty.\n\n> **Tip:** Arrive at Bled before 10 AM; the morning light on the lake is magical and there are fewer crowds.",
            ),
            step(6, [("gopro", 0, "Imprescindible para las vistas panoramicas desde las murallas"), ("bottle", 1, "Las murallas no tienen sombra; lleva agua"), ("fanny_pack", 2, "Manos libres para subir y bajar las escaleras de las murallas")],
                "Hoy caminas sobre historia: las **Murallas de Dubrovnik** (1.94 km, 35 EUR) rodean todo el casco antiguo. Las vistas al Adriatico y los tejados de terracota son de las mejores del Mediterraneo.\n\nDentro, la calle **Stradun** es el corazon: cafes, heladerias y tiendas. No te pierdas la catedral y el Palacio del Rector.\n\n> **Tip:** Recorre las murallas a primera hora (abren a las 8); al mediodia el sol y las colas son brutales.",
                "Today you walk on history: **Dubrovnik's Walls** (1.94 km, 35 EUR) encircle the entire old town. The Adriatic views and terracotta rooftops are among the best in the Mediterranean.\n\nInside, **Stradun** street is the heart: cafes, gelato shops and stores. Don't miss the cathedral and the Rector's Palace.\n\n> **Tip:** Walk the walls first thing in the morning (they open at 8); by midday the sun and queues are brutal.",
            ),
            step(7, [("gopro", 0, "La isla de Lokrum es perfecta para grabaciones acuaticas"), ("powerbank", 1, "Un dia de tour + isla; asegura bateria para fotos todo el dia")],
                "Dia de cine y naturaleza. Por la manana, **tour de Juego de Tronos**: visita las localizaciones de King's Landing (Fort Lovrijenac, escalinata jesuitica, Pile Gate). Dubrovnik ES Desembarco del Rey.\n\nPor la tarde, ferry a **Lokrum** (15 min, frecuente). La isla tiene un monasterio benedictino, un lago salado para banarse y pavos reales en libertad. Lleva banador y snorkel.\n\n> **Tip:** El ultimo ferry de Lokrum sale a las 18:00 (17:00 en temporada baja); no lo pierdas o te quedas en la isla.",
                "A day of cinema and nature. In the morning, **Game of Thrones tour**: visit King's Landing filming locations (Fort Lovrijenac, Jesuit staircase, Pile Gate). Dubrovnik IS King's Landing.\n\nIn the afternoon, ferry to **Lokrum** (15 min, frequent). The island has a Benedictine monastery, a saltwater lake for swimming and free-roaming peacocks. Bring a swimsuit and snorkel.\n\n> **Tip:** The last Lokrum ferry leaves at 6 PM (5 PM in low season); don't miss it or you'll be stranded on the island.",
            ),
        ],
        "japon-esencial": [
            step(1, [("adapter", 0, "Japon usa enchufes tipo A/B (110V); necesitas adaptador"), ("organizers", 1, "12 dias de viaje: organiza maleta por destino"), ("powerbank", 2, "Dia entero con Google Maps en un pais con otro alfabeto")],
                "Bienvenido a Tokio, la ciudad mas fascinante del mundo. Desde Narita, el **Narita Express** (N'EX) te deja en Shinjuku en 80 min (3.250 JPY).\n\nActiva tu **Japan Rail Pass** (JR Pass) para el dia en que cojas el Shinkansen. Tu primera noche en Shinjuku: rascacielos, neon y una cena en un izakaya bajo las vias del tren (Memory Lane / Omoide Yokocho).\n\n> **Tip:** Compra una tarjeta Suica/Pasmo en el aeropuerto; funciona en metro, buses, konbinis y maquinas expendedoras.",
                "Welcome to Tokyo, the world's most fascinating city. From Narita, the **Narita Express** (N'EX) takes you to Shinjuku in 80 min (3,250 JPY).\n\nActivate your **Japan Rail Pass** (JR Pass) for the day you take the Shinkansen. Your first night in Shinjuku: skyscrapers, neon and dinner at an izakaya under the train tracks (Memory Lane / Omoide Yokocho).\n\n> **Tip:** Buy a Suica/Pasmo card at the airport; it works on metro, buses, konbinis and vending machines.",
            ),
            step(2, [("gopro", 0, "Captura el cruce de Shibuya y la energia de Harajuku"), ("fanny_pack", 1, "Harajuku y Shibuya tienen mucha gente; lleva tus cosas seguras")],
                "Empieza en el **Santuario Meiji-jingu**: un oasis de bosque en pleno Tokio. A la salida, la **calle Takeshita** en Harajuku es pura explosion de color y moda japonesa.\n\nBaja a **Shibuya**: el cruce mas famoso del mundo, Shibuya Sky (300m de altura) y la estatua de Hachiko. De noche, los bares de Shibuya y Ebisu son perfectos.\n\n> **Tip:** Visita Meiji-jingu a primera hora; si tienes suerte veras una boda sintoista tradicional.",
                "Start at **Meiji-jingu Shrine**: a forest oasis in the middle of Tokyo. Upon exit, **Takeshita Street** in Harajuku is a pure explosion of color and Japanese fashion.\n\nHead to **Shibuya**: the world's most famous crossing, Shibuya Sky (300m high) and the Hachiko statue. At night, bars in Shibuya and Ebisu are perfect.\n\n> **Tip:** Visit Meiji-jingu first thing in the morning; if you're lucky you'll see a traditional Shinto wedding.",
            ),
            step(5, [("pillow", 0, "El Shinkansen a Kioto son 2h15; llega descansado"), ("headphones", 1, "Cancelacion de ruido perfecta para el tren bala")],
                "Manana en **Ueno**: el parque, el Museo Nacional de Tokio y si es primavera, los cerezos en flor. Almuerzo en Ameya-Yokocho, el mercado callejero bajo las vias del tren.\n\nPor la tarde, **Shinkansen** a Kioto (2h15 con JR Pass). El tren bala es una experiencia en si mismo: puntual al segundo, limpio y con vistas al Monte Fuji si te sientas en el lado derecho.\n\n> **Tip:** Compra un ekiben (bento de estacion) en Tokyo Station; es tradicion japonesa comer en el Shinkansen.",
                "Morning in **Ueno**: the park, Tokyo National Museum and if it's spring, the cherry blossoms. Lunch at Ameya-Yokocho, the street market under the train tracks.\n\nIn the afternoon, **Shinkansen** to Kyoto (2h15 with JR Pass). The bullet train is an experience in itself: punctual to the second, spotless and with views of Mt. Fuji if you sit on the right side.\n\n> **Tip:** Buy an ekiben (station bento) at Tokyo Station; it's a Japanese tradition to eat on the Shinkansen.",
            ),
            step(8, [("gopro", 0, "Graba los ciervos de Nara y los templos de Kioto"), ("tripod", 1, "Tripode compacto para fotos estables en templos con poca luz")],
                "Doble plan hoy. Empieza en **Kiyomizudera**, el templo de la terraza de madera suspendida sobre el bosque. Las calles Ninenzaka y Sannenzaka que bajan son preciosas.\n\nPor la tarde, excursion a **Nara** (45 min en tren): los ciervos sagrados te saludan (literalmente hacen reverencia por galletas), el **Gran Buda de Todai-ji** impresiona y el parque es enorme.\n\n> **Tip:** No lleves comida a la vista en Nara; los ciervos son adorables pero insistentes y te rodearan.",
                "Double plan today. Start at **Kiyomizudera**, the temple with the wooden terrace suspended over the forest. The streets Ninenzaka and Sannenzaka leading down are beautiful.\n\nIn the afternoon, day trip to **Nara** (45 min by train): the sacred deer greet you (they literally bow for crackers), the **Great Buddha at Todai-ji** is impressive and the park is vast.\n\n> **Tip:** Don't carry food in plain sight in Nara; the deer are adorable but pushy and will surround you.",
            ),
            step(12, [("organizers", 0, "Reorganiza tu maleta despues de 12 dias de compras en Japon"), ("samsonite", 1, "Si necesitas facturar recuerdos, una maleta solida es clave")],
                "Ultimo dia. Manana libre para compras de ultima hora: si buscas recuerdos, el barrio de **Shinsekai** tiene tiendas retro y la Torre Tsutenkaku.\n\nTraslado al **Aeropuerto de Kansai** (tren Haruka, 75 min). Aprovecha el duty-free para comprar Kit-Kats de sabores japoneses, matcha y sake.\n\n> **Tip:** Si compraste mucho, Japon tiene envio de maletas por takkyubin (mensajeria); las envias desde el hotel al aeropuerto por unos 2.000 JPY.",
                "Last day. Free morning for last-minute shopping: if looking for souvenirs, **Shinsekai** neighborhood has retro shops and Tsutenkaku Tower.\n\nTransfer to **Kansai Airport** (Haruka train, 75 min). Use the duty-free for Japanese Kit-Kat flavors, matcha and sake.\n\n> **Tip:** If you bought a lot, Japan has luggage shipping by takkyubin (courier); you can send bags from your hotel to the airport for about 2,000 JPY.",
            ),
        ],
        "londres-ciudad-imperial": [
            step(1, [("adapter", 0, "Reino Unido usa enchufes tipo G; imprescindible un adaptador"), ("backpack", 1, "Mochila ideal para moverte por el metro londinense"), ("powerbank", 2, "Londres es enorme; necesitaras bateria para GPS todo el dia")],
                "Bienvenido a Londres. Desde Heathrow, el **Heathrow Express** (15 min a Paddington) o el **Piccadilly Line** (1h, mas barato) te llevan al centro.\n\nTu primer paseo es por **Westminster**: Big Ben, la Abadia de Westminster, Buckingham Palace y St. James's Park. Si llegas antes de las 11:00, puedes ver el Cambio de Guardia (lunes, miercoles, viernes y domingos).\n\n> **Tip:** Consigue una Oyster Card o usa tu tarjeta contactless; el transporte en Londres es caro pero con tope diario.",
                "Welcome to London. From Heathrow, the **Heathrow Express** (15 min to Paddington) or the **Piccadilly Line** (1h, cheaper) take you to the center.\n\nYour first walk is through **Westminster**: Big Ben, Westminster Abbey, Buckingham Palace and St. James's Park. If you arrive before 11 AM, you can see the Changing of the Guard (Mon, Wed, Fri and Sun).\n\n> **Tip:** Get an Oyster Card or use your contactless card; London transport is pricey but has a daily cap.",
            ),
            step(3, [("gopro", 0, "Graba cada rincon de los estudios de Harry Potter"), ("tripod", 1, "Fotos estables en los decorados oscuros de Hogwarts")],
                "Dia magico: **Warner Bros. Studio Tour - The Making of Harry Potter**. Reserva obligatoria (se agotan semanas antes). El autobus desde Watford Junction tarda 15 min.\n\nVeras el Gran Comedor, el Callejon Diagon, el Hogwarts Express y maquetas increibles. Dedica al menos 4 horas. La tienda es enorme y peligrosa para tu cartera.\n\n> **Tip:** Llega 20 min antes de tu hora de entrada; hay colas para el autobus y para acceder a los estudios.",
                "Magical day: **Warner Bros. Studio Tour - The Making of Harry Potter**. Booking required (sells out weeks in advance). The bus from Watford Junction takes 15 min.\n\nYou'll see the Great Hall, Diagon Alley, the Hogwarts Express and incredible models. Allow at least 4 hours. The shop is huge and dangerous for your wallet.\n\n> **Tip:** Arrive 20 min before your entry time; there are queues for the bus and to access the studios.",
            ),
            step(5, [("headphones", 0, "Cancelacion de ruido para descansar en el vuelo de vuelta"), ("pillow", 1, "Almohada cervical para dormir en el avion de regreso"), ("kindle", 2, "Lectura ligera mientras esperas en Heathrow")],
                "Ultimo dia. **Notting Hill** es el barrio mas colorido de Londres: casas pastel, el **Portobello Market** (sabados es el mejor dia) y librerias independientes.\n\nPasea por **Hyde Park** para despedirte de la ciudad. Si tienes tiempo, el **London Eye** ofrece vistas de 360 grados de toda la ciudad (30 min de vuelta).\n\n> **Tip:** El Portobello Market tiene los mejores precios al fondo, lejos de la entrada de Notting Hill Gate; camina hasta el final.",
                "Last day. **Notting Hill** is London's most colorful neighborhood: pastel houses, **Portobello Market** (Saturdays are best) and independent bookshops.\n\nWalk through **Hyde Park** to say goodbye to the city. If you have time, the **London Eye** offers 360-degree views of the whole city (30 min ride).\n\n> **Tip:** Portobello Market has the best prices at the far end, away from the Notting Hill Gate entrance; walk to the end.",
            ),
        ],
        "fiordos-noruegos": [
            step(1, [("adapter", 0, "Noruega usa enchufes tipo F; este adaptador te cubre"), ("backpack", 1, "Mochila resistente para un viaje con mucho senderismo")],
                "Llegas a Bergen, la puerta de los fiordos. Pasea por **Bryggen**, el muelle hanseatico con sus casas de madera de colores (Patrimonio UNESCO). El **Fish Market** (Fisketorget) es obligatorio: prueba el salmon fresco y las gambas.\n\nBergen es la ciudad mas lluviosa de Europa (200+ dias/ano), asi que lleva siempre una chaqueta impermeable.\n\n> **Tip:** La Bergen Card (24/72h) incluye funicular, museos y transporte; se amortiza rapidamente.",
                "You arrive in Bergen, gateway to the fjords. Walk through **Bryggen**, the Hanseatic wharf with colorful wooden houses (UNESCO Heritage). The **Fish Market** (Fisketorget) is a must: try fresh salmon and shrimp.\n\nBergen is Europe's rainiest city (200+ days/year), so always carry a waterproof jacket.\n\n> **Tip:** The Bergen Card (24/72h) includes funicular, museums and transport; it pays for itself quickly.",
            ),
            step(4, [("gopro", 0, "El Geirangerfjord es Patrimonio UNESCO; grabalo sumergible"), ("tripod", 1, "Estabiliza las fotos desde el barco con oleaje")],
                "El dia mas espectacular del viaje: crucero por el **Geirangerfjord** (Patrimonio UNESCO). 90 minutos navegando entre acantilados de 1.000 m, cascadas como las Siete Hermanas y el Pretendiente, y aguas verde esmeralda.\n\nDespues, traslado escenico a **Flam** por carreteras de montana con vistas que quitan el aliento.\n\n> **Tip:** Lleva ropa de abrigo incluso en verano; en el fiordo la temperatura baja 5-10 grados respecto a tierra.",
                "The most spectacular day of the trip: cruise through **Geirangerfjord** (UNESCO Heritage). 90 minutes sailing between 1,000 m cliffs, waterfalls like the Seven Sisters and the Suitor, and emerald-green waters.\n\nThen a scenic transfer to **Flam** via mountain roads with breathtaking views.\n\n> **Tip:** Bring warm clothing even in summer; in the fjord temperatures drop 5-10 degrees compared to land.",
            ),
            step(5, [("gopro", 0, "El tren Flamsbana cruza 20 tuneles; grabalo todo"), ("kindle", 1, "Lectura perfecta para los trayectos lentos entre fiordos")],
                "Hoy te espera uno de los trayectos en tren mas bonitos del mundo: el **Flamsbana**. 20 km de descenso con 864 m de desnivel, 20 tuneles y la espectacular parada en la cascada Kjosfossen.\n\nOpcionalmente, un crucero por el **Naeroyfjord** (el fiordo mas estrecho del mundo, tambien UNESCO) completa un dia perfecto.\n\n> **Tip:** Sientate en el lado izquierdo del tren (direccion descenso) para las mejores vistas; y ten la camara lista en Kjosfossen.",
                "Today one of the world's most beautiful train journeys awaits: the **Flamsbana**. 20 km descent with 864 m elevation drop, 20 tunnels and the spectacular stop at Kjosfossen waterfall.\n\nOptionally, a cruise through **Naeroyfjord** (the narrowest fjord in the world, also UNESCO) completes a perfect day.\n\n> **Tip:** Sit on the left side of the train (going downhill) for the best views; and have your camera ready at Kjosfossen.",
            ),
            step(6, [("gopro", 0, "Graba la subida al Preikestolen y las vistas desde 604 m"), ("bottle", 1, "4 horas de senderismo; hidratacion esencial")],
                "El reto del viaje: la subida al **Preikestolen** (Pulpit Rock). Son 8 km (ida y vuelta), unas 4 horas, con desnivel moderado. La recompensa: una plataforma de roca plana a 604 m sobre el **Lysefjord**.\n\nEs una de las fotos mas impresionantes que haras en tu vida. El sendero esta bien marcado pero lleva calzado de montana, agua y algo de comer.\n\n> **Tip:** Empieza la subida antes de las 9; al mediodia la plataforma se llena y no podras hacer buenas fotos.",
                "The trip's challenge: the hike to **Preikestolen** (Pulpit Rock). It's 8 km round trip, about 4 hours, with moderate elevation. The reward: a flat rock platform 604 m above **Lysefjord**.\n\nIt's one of the most impressive photos you'll ever take. The trail is well-marked but bring hiking boots, water and snacks.\n\n> **Tip:** Start the hike before 9 AM; by noon the platform gets crowded and good photos become difficult.",
            ),
        ],
        "safari-en-kenia": [
            step(1, [("adapter", 0, "Kenia usa enchufes tipo G (como UK); lleva adaptador"), ("organizers", 1, "8 dias de safari con traslados largos; organiza bien"), ("powerbank", 2, "Los lodges tienen electricidad limitada; lleva bateria extra")],
                "Llegas a Nairobi, capital de Kenia. Tu primera parada es el **Centro de Jirafas** donde puedes alimentar jirafas Rothschild cara a cara desde una plataforma elevada. Despues, visita el **Orfanato de Elefantes David Sheldrick** (solo abre 11:00-12:00; reserva online).\n\nNairobi es una ciudad vibrante pero con precauciones de seguridad necesarias; no camines solo de noche y usa taxis de confianza (Bolt o Uber funcionan bien).\n\n> **Tip:** Cambia dinero en el aeropuerto solo lo minimo; el M-Pesa (pago movil) se usa en todas partes en Kenia.",
                "You arrive in Nairobi, Kenya's capital. Your first stop is the **Giraffe Centre** where you can feed Rothschild giraffes face to face from a raised platform. Then visit the **David Sheldrick Elephant Orphanage** (open 11 AM-12 PM only; book online).\n\nNairobi is a vibrant city but requires security awareness; don't walk alone at night and use trusted taxis (Bolt or Uber work well).\n\n> **Tip:** Only change minimal money at the airport; M-Pesa (mobile payment) is used everywhere in Kenya.",
            ),
            step(3, [("gopro", 0, "Captura los Big Five en safari con video 5.3K"), ("tripod", 1, "Estabiliza fotos de fauna desde el vehiculo en movimiento"), ("bottle", 2, "Safaris de 8+ horas; hidratacion constante bajo el sol africano")],
                "El dia mas intenso del safari: **dia completo en el Masai Mara**. Safari al amanecer (5:30 AM) cuando los depredadores son mas activos. Bush breakfast en mitad de la sabana.\n\nSafari vespertino buscando los **Cinco Grandes**: leon, leopardo, elefante, bufalo y rinoceronte. El Mara es uno de los pocos lugares del mundo donde puedes verlos a todos en un dia.\n\n> **Tip:** Lleva prismaticos, proteccion solar alta y ropa de colores neutros (caqui, verde oliva); evita azul oscuro y negro que atraen tsetse.",
                "The most intense safari day: **full day in the Masai Mara**. Sunrise safari (5:30 AM) when predators are most active. Bush breakfast in the middle of the savanna.\n\nAfternoon safari seeking the **Big Five**: lion, leopard, elephant, buffalo and rhino. The Mara is one of the few places in the world where you can see them all in one day.\n\n> **Tip:** Bring binoculars, high SPF sunscreen and neutral-colored clothing (khaki, olive green); avoid dark blue and black which attract tsetse flies.",
            ),
            step(7, [("gopro", 0, "Amanecer con elefantes y Kilimanjaro: el momento mas fotografico"), ("tripod", 1, "Tripode para fotos de larga exposicion al amanecer africano")],
                "El momento cumbre del viaje: **safari al amanecer en Amboseli** con el **Kilimanjaro** nevado de fondo. Las manadas de elefantes caminando ante la montana mas alta de Africa es la imagen mas iconica del continente.\n\nAmboseli tiene los elefantes mas grandes y con colmillos mas largos de toda Kenia. Los flamencos del lago y las garzas completan el paisaje.\n\n> **Tip:** El Kilimanjaro suele estar despejado al amanecer y se nubla a partir de las 10 AM; madruga o te lo perderas.",
                "The trip's peak moment: **sunrise safari in Amboseli** with the snow-capped **Kilimanjaro** as backdrop. Elephant herds walking before Africa's highest mountain is the continent's most iconic image.\n\nAmboseli has Kenya's largest elephants with the longest tusks. Flamingos on the lake and herons complete the landscape.\n\n> **Tip:** Kilimanjaro is usually clear at sunrise and clouds over by 10 AM; wake up early or you'll miss it.",
            ),
        ],
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    if not ADMIN_SECRET:
        print("[ERROR] ADMIN_SECRET env var is required.")
        print("Usage: ADMIN_SECRET=xxx python -m app.seeds.seed_route_products_http")
        sys.exit(1)

    print("=" * 60)
    print("Seed route-step products via HTTP")
    print("=" * 60)
    print(f"  API: {BASE_URL}")
    print()

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Admin-Secret": ADMIN_SECRET,
    })

    # 1. Discover products
    role_to_slug = discover_products(session)
    if not role_to_slug:
        print("[ERROR] No products could be mapped. Aborting.")
        sys.exit(1)
    print()

    # 2. Build pack data with resolved slugs
    all_packs = build_all_packs()

    # Replace role keys with actual slugs, deduplicating per step
    for pack_slug, steps in all_packs.items():
        for s in steps:
            resolved: list[dict] = []
            seen_slugs: set[str] = set()
            for p in s["products"]:
                actual_slug = role_to_slug.get(p["product_slug"])
                if not actual_slug:
                    print(f"  [WARN] Role '{p['product_slug']}' not mapped, skipping in {pack_slug} day {s['day']}")
                elif actual_slug in seen_slugs:
                    print(f"  [WARN] Duplicate slug '{actual_slug[:40]}' in {pack_slug} day {s['day']}, skipping")
                else:
                    seen_slugs.add(actual_slug)
                    resolved.append({**p, "product_slug": actual_slug})
            s["products"] = resolved

    # 3. Send pack by pack
    total_links = 0
    total_descs = 0
    all_warnings: list[str] = []

    for pack_slug, steps in all_packs.items():
        url = f"{ENRICH_URL}/{pack_slug}"
        payload = {"steps": steps}
        print(f"  POST {pack_slug} ({len(steps)} steps)...", end=" ", flush=True)

        try:
            resp = session.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            links = result.get("links_created", 0)
            descs = result.get("descriptions_updated", 0)
            warnings = result.get("warnings", [])
            total_links += links
            total_descs += descs
            all_warnings.extend(warnings)
            print(f"OK (links={links}, descs={descs})")
            if warnings:
                for w in warnings:
                    print(f"    [WARN] {w}")
        except requests.HTTPError as exc:
            print(f"FAILED ({exc.response.status_code}: {exc.response.text[:200]})")
        except requests.RequestException as exc:
            print(f"FAILED ({exc})")

    # 4. Summary
    print()
    print("=" * 60)
    print("Seed completado:")
    print(f"  Links creados       : {total_links}")
    print(f"  Descripciones upd.  : {total_descs}")
    print(f"  Warnings            : {len(all_warnings)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
