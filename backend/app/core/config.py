"""Application configuration settings."""

import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "SaaS Platform API"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Database
    database_url: str = Field(env="DATABASE_URL")

    # JWT
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Kafka (Optional)
    kafka_enabled: bool = Field(default=False, env="KAFKA_ENABLED")
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"], env="CORS_ORIGINS"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    # API
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")

    # Security
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")

    # Pagination
    default_page_size: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, env="MAX_PAGE_SIZE")

    # File upload & AWS S3
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]
    )

    aws_access_key_id: str | None = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="sa-east-1", env="AWS_REGION")
    aws_s3_bucket: str | None = Field(default=None, env="AWS_S3_BUCKET")
    s3_endpoint_url: str | None = Field(default=None, env="S3_ENDPOINT_URL")

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [ext.strip() for ext in v.split(",")]
        return v

    # AI Service - Hugging Face
    ai_provider: str = Field(default="huggingface", env="AI_PROVIDER")
    ai_model: str = Field(
        default="meta-llama/Meta-Llama-3-70B-Instruct", env="AI_MODEL"
    )
    ai_model_version: str = Field(default="1.0.0", env="AI_MODEL_VERSION")
    ai_analysis_enabled: bool = Field(default=True, env="AI_ANALYSIS_ENABLED")
    ai_max_tokens: int = Field(default=1024, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")

    huggingface_api_key: str | None = Field(default=None, env="HUGGINGFACE_API_KEY")
    together_api_key: str | None = Field(default=None, env="TOGETHER_API_KEY")
    openrouter_api_key: str | None = Field(default=None, env="OPENROUTER_API_KEY")

    # Email Service - Resend
    resend_api_key: str | None = Field(default=None, env="RESEND_API_KEY")
    from_email: str = Field(default="noreply@saas-platform.com", env="FROM_EMAIL")
    from_name: str = Field(default="SaaS Platform", env="FROM_NAME")

    # Monitoring - Sentry
    sentry_dsn_backend: str | None = Field(default=None, env="SENTRY_DSN_BACKEND")
    sentry_dsn_frontend: str | None = Field(default=None, env="SENTRY_DSN_FRONTEND")
    sentry_environment: str = Field(default="production", env="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(
        default=0.1, env="SENTRY_TRACES_SAMPLE_RATE"
    )

    # URLs (for emails and redirects)
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    backend_url: str = Field(default="http://localhost:8000", env="BACKEND_URL")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
