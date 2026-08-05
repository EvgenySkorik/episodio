from datetime import datetime

from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def __repr__(self):
        def __repr__(self):
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
            return f"{self.__class__.__name__}({data})"


class Movie(Base):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_kino: Mapped[int] = mapped_column(index=True, unique=True)
    name: Mapped[str] = mapped_column(index=True)
    alternative_name: Mapped[str | None]
    movie_type: Mapped[str] = mapped_column(default="movie")
    year: Mapped[int]
    description: Mapped[str | None]
    short_description: Mapped[str | None]
    is_series: Mapped[bool] = mapped_column(default=False)
    rating_kp: Mapped[float | None]
    rating_imdb: Mapped[float | None]
    genres: Mapped[list | None] = mapped_column(JSON, nullable=True)
    countries: Mapped[list | None] = mapped_column(JSON, nullable=True)
    logo: Mapped[str | None]
    poster: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    total_seasons: Mapped[int | None] = mapped_column(default=0)
    total_episodes: Mapped[int | None] = mapped_column(default=0)
    last_checked_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


    saved_by_users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_movie",
        back_populates="movie_collections",
    )


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_vk: Mapped[int] = mapped_column(index=True, unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=True)
    telephone: Mapped[str | None] = mapped_column(nullable=True)
    avatar: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    movie_collections: Mapped[list["Movie"]] = relationship(
        "Movie",
        secondary="user_movie",
        back_populates="saved_by_users",
    )


class UserMovie(Base):
    __tablename__ = "user_movie"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movie.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)

    is_watched: Mapped[bool] = mapped_column(default=False)
    user_rating: Mapped[float] = mapped_column(nullable=True)
    is_tracking: Mapped[bool] = mapped_column(default=False)
