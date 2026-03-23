from sqladmin import ModelView

from app.domain.models.accommodation import Accommodation, AccommodationTranslation
from app.domain.models.blog_post import BlogPost, BlogPostTranslation
from app.domain.models.destination import Destination, DestinationTranslation
from app.domain.models.experience import Experience, ExperienceTranslation
from app.domain.models.pack import Pack, PackTranslation
from app.domain.models.product import Product, ProductTranslation
from app.domain.models.link_click import LinkClick
from app.domain.models.route_step import RouteStep, RouteStepTranslation


class PackAdmin(ModelView, model=Pack):
    name = "Pack"
    name_plural = "Packs"
    icon = "fa-solid fa-suitcase-rolling"
    column_list = [Pack.id, Pack.slug, Pack.duration_days, Pack.price_from, Pack.price_to, Pack.price_currency, Pack.featured, Pack.created_at]
    column_searchable_list = [Pack.slug]
    column_sortable_list = [Pack.slug, Pack.duration_days, Pack.price_from, Pack.featured, Pack.created_at]
    column_default_sort = ("created_at", True)
    page_size = 25


class PackTranslationAdmin(ModelView, model=PackTranslation):
    name = "Pack Translation"
    name_plural = "Pack Translations"
    icon = "fa-solid fa-language"
    column_list = [PackTranslation.id, PackTranslation.pack_id, PackTranslation.locale, PackTranslation.title, PackTranslation.short_description]
    column_searchable_list = [PackTranslation.title, PackTranslation.locale]
    column_sortable_list = [PackTranslation.locale, PackTranslation.title]
    page_size = 25


class DestinationAdmin(ModelView, model=Destination):
    name = "Destination"
    name_plural = "Destinations"
    icon = "fa-solid fa-map-location-dot"
    column_list = [Destination.id, Destination.pack_id, Destination.image, Destination.display_order, Destination.days, Destination.created_at]
    column_sortable_list = [Destination.display_order, Destination.days, Destination.created_at]
    column_default_sort = ("display_order", False)
    page_size = 25


class DestinationTranslationAdmin(ModelView, model=DestinationTranslation):
    name = "Destination Translation"
    name_plural = "Destination Translations"
    icon = "fa-solid fa-language"
    column_list = [DestinationTranslation.id, DestinationTranslation.destination_id, DestinationTranslation.locale, DestinationTranslation.name, DestinationTranslation.country]
    column_searchable_list = [DestinationTranslation.name, DestinationTranslation.country, DestinationTranslation.locale]
    column_sortable_list = [DestinationTranslation.locale, DestinationTranslation.name]
    page_size = 25


class RouteStepAdmin(ModelView, model=RouteStep):
    name = "Route Step"
    name_plural = "Route Steps"
    icon = "fa-solid fa-route"
    column_list = [RouteStep.id, RouteStep.pack_id, RouteStep.destination_id, RouteStep.day, RouteStep.created_at]
    column_sortable_list = [RouteStep.day, RouteStep.created_at]
    column_default_sort = ("day", False)
    page_size = 25


class RouteStepTranslationAdmin(ModelView, model=RouteStepTranslation):
    name = "Route Step Translation"
    name_plural = "Route Step Translations"
    icon = "fa-solid fa-language"
    column_list = [RouteStepTranslation.id, RouteStepTranslation.route_step_id, RouteStepTranslation.locale, RouteStepTranslation.title]
    column_searchable_list = [RouteStepTranslation.title, RouteStepTranslation.locale]
    column_sortable_list = [RouteStepTranslation.locale, RouteStepTranslation.title]
    page_size = 25


class AccommodationAdmin(ModelView, model=Accommodation):
    name = "Accommodation"
    name_plural = "Accommodations"
    icon = "fa-solid fa-hotel"
    column_list = [Accommodation.id, Accommodation.destination_id, Accommodation.tier, Accommodation.price_per_night, Accommodation.currency, Accommodation.rating, Accommodation.nights, Accommodation.created_at]
    column_searchable_list = [Accommodation.tier]
    column_sortable_list = [Accommodation.tier, Accommodation.price_per_night, Accommodation.rating, Accommodation.nights, Accommodation.created_at]
    column_default_sort = ("created_at", True)
    page_size = 25


class AccommodationTranslationAdmin(ModelView, model=AccommodationTranslation):
    name = "Accommodation Translation"
    name_plural = "Accommodation Translations"
    icon = "fa-solid fa-language"
    column_list = [AccommodationTranslation.id, AccommodationTranslation.accommodation_id, AccommodationTranslation.locale, AccommodationTranslation.name]
    column_searchable_list = [AccommodationTranslation.name, AccommodationTranslation.locale]
    column_sortable_list = [AccommodationTranslation.locale, AccommodationTranslation.name]
    page_size = 25


class ExperienceAdmin(ModelView, model=Experience):
    name = "Experience"
    name_plural = "Experiences"
    icon = "fa-solid fa-compass"
    column_list = [Experience.id, Experience.destination_id, Experience.provider, Experience.price, Experience.currency, Experience.rating, Experience.created_at]
    column_searchable_list = [Experience.provider]
    column_sortable_list = [Experience.provider, Experience.price, Experience.rating, Experience.created_at]
    column_default_sort = ("created_at", True)
    page_size = 25


class ExperienceTranslationAdmin(ModelView, model=ExperienceTranslation):
    name = "Experience Translation"
    name_plural = "Experience Translations"
    icon = "fa-solid fa-language"
    column_list = [ExperienceTranslation.id, ExperienceTranslation.experience_id, ExperienceTranslation.locale, ExperienceTranslation.title, ExperienceTranslation.duration]
    column_searchable_list = [ExperienceTranslation.title, ExperienceTranslation.locale]
    column_sortable_list = [ExperienceTranslation.locale, ExperienceTranslation.title]
    page_size = 25


class ProductAdmin(ModelView, model=Product):
    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-box"
    column_list = [Product.id, Product.slug, Product.category, Product.price, Product.currency, Product.rating, Product.created_at]
    column_searchable_list = [Product.slug, Product.category]
    column_sortable_list = [Product.slug, Product.category, Product.price, Product.rating, Product.created_at]
    column_default_sort = ("created_at", True)
    page_size = 25


class ProductTranslationAdmin(ModelView, model=ProductTranslation):
    name = "Product Translation"
    name_plural = "Product Translations"
    icon = "fa-solid fa-language"
    column_list = [ProductTranslation.id, ProductTranslation.product_id, ProductTranslation.locale, ProductTranslation.name]
    column_searchable_list = [ProductTranslation.name, ProductTranslation.locale]
    column_sortable_list = [ProductTranslation.locale, ProductTranslation.name]
    page_size = 25


class LinkClickAdmin(ModelView, model=LinkClick):
    name = "Link Click"
    name_plural = "Link Clicks"
    icon = "fa-solid fa-chart-line"
    column_list = [LinkClick.id, LinkClick.entity_type, LinkClick.entity_id, LinkClick.clicked_at]
    column_searchable_list = [LinkClick.entity_type]
    column_sortable_list = [LinkClick.entity_type, LinkClick.clicked_at]
    column_default_sort = ("clicked_at", True)
    page_size = 50
    can_create = False
    can_edit = False
    can_delete = False


class BlogPostAdmin(ModelView, model=BlogPost):
    name = "Blog Post"
    name_plural = "Blog Posts"
    icon = "fa-solid fa-newspaper"
    column_list = [BlogPost.id, BlogPost.slug, BlogPost.category, BlogPost.published, BlogPost.published_at, BlogPost.created_at]
    column_searchable_list = [BlogPost.slug, BlogPost.category]
    column_sortable_list = [BlogPost.slug, BlogPost.category, BlogPost.published, BlogPost.published_at, BlogPost.created_at]
    column_default_sort = ("created_at", True)
    page_size = 25


class BlogPostTranslationAdmin(ModelView, model=BlogPostTranslation):
    name = "Blog Post Translation"
    name_plural = "Blog Post Translations"
    icon = "fa-solid fa-language"
    column_list = [BlogPostTranslation.id, BlogPostTranslation.blog_post_id, BlogPostTranslation.locale, BlogPostTranslation.title, BlogPostTranslation.excerpt]
    column_searchable_list = [BlogPostTranslation.title, BlogPostTranslation.locale]
    column_sortable_list = [BlogPostTranslation.locale, BlogPostTranslation.title]
    page_size = 25


ALL_VIEWS = [
    PackAdmin,
    PackTranslationAdmin,
    DestinationAdmin,
    DestinationTranslationAdmin,
    RouteStepAdmin,
    RouteStepTranslationAdmin,
    AccommodationAdmin,
    AccommodationTranslationAdmin,
    ExperienceAdmin,
    ExperienceTranslationAdmin,
    ProductAdmin,
    ProductTranslationAdmin,
    BlogPostAdmin,
    BlogPostTranslationAdmin,
    LinkClickAdmin,
]
