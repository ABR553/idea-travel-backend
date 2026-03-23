from pydantic import BaseModel, Field


class BlogPostTranslationCreate(BaseModel):
    locale: str
    title: str
    excerpt: str
    content: str


class BlogPostCreate(BaseModel):
    slug: str
    cover_image: str = Field(alias="coverImage")
    category: str
    published: bool = False
    published_at: str | None = Field(default=None, alias="publishedAt")
    related_pack_slug: str | None = Field(default=None, alias="relatedPackSlug")
    translations: list[BlogPostTranslationCreate]

    model_config = {"populate_by_name": True}


class BlogPostUpdate(BaseModel):
    slug: str | None = None
    cover_image: str | None = Field(default=None, alias="coverImage")
    category: str | None = None
    published: bool | None = None
    published_at: str | None = Field(default=None, alias="publishedAt")
    related_pack_slug: str | None = Field(default=None, alias="relatedPackSlug")
    translations: list[BlogPostTranslationCreate] | None = None

    model_config = {"populate_by_name": True}


class BlogPostListResponse(BaseModel):
    id: str
    slug: str
    title: str
    excerpt: str
    cover_image: str = Field(alias="coverImage")
    category: str
    published_at: str | None = Field(alias="publishedAt")
    related_pack_slug: str | None = Field(default=None, alias="relatedPackSlug")

    model_config = {"populate_by_name": True}


class BlogPostResponse(BaseModel):
    id: str
    slug: str
    title: str
    excerpt: str
    content: str
    cover_image: str = Field(alias="coverImage")
    category: str
    published_at: str | None = Field(alias="publishedAt")
    related_pack_slug: str | None = Field(default=None, alias="relatedPackSlug")

    model_config = {"populate_by_name": True}
