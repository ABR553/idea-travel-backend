from pydantic import BaseModel, Field


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
