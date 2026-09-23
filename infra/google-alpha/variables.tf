variable "project_id" {
  description = "Identificador do projeto Google Cloud dedicado a alpha."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id deve ser um identificador Google Cloud valido."
  }
}

variable "region" {
  description = "Regiao europeia comum ao Cloud Run e Cloud SQL."
  type        = string
  default     = "europe-west1"

  validation {
    condition     = startswith(var.region, "europe-")
    error_message = "A alpha deve permanecer numa regiao europeia."
  }
}

variable "container_image" {
  description = "Imagem imutavel, incluindo digest sha256, a publicar no Cloud Run."
  type        = string
  default     = ""

  validation {
    condition = (
      !var.deploy_application ||
      can(regex("@sha256:[0-9a-f]{64}$", var.container_image))
    )
    error_message = "Para publicar, indique uma imagem fixada por digest sha256."
  }
}

variable "deploy_application" {
  description = "So deve ser true depois de criar as versoes dos segredos."
  type        = bool
  default     = false
}

variable "bootstrap_application" {
  description = "Cria temporariamente um servico vazio para obter o URL OIDC."
  type        = bool
  default     = false
}

variable "privacy_contact_email" {
  description = "Email de privacidade mostrado aos participantes."
  type        = string
  default     = ""

  validation {
    condition = (
      !var.deploy_application ||
      can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.privacy_contact_email))
    )
    error_message = "Defina um email de privacidade valido antes da publicacao."
  }
}

variable "support_contact_email" {
  description = "Email de suporte mostrado aos participantes."
  type        = string
  default     = ""

  validation {
    condition = (
      !var.deploy_application ||
      can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.support_contact_email))
    )
    error_message = "Defina um email de suporte valido antes da publicacao."
  }
}

variable "database_tier" {
  description = "Dimensao da instancia PostgreSQL. Rever custo antes de aplicar."
  type        = string
  default     = "db-f1-micro"
}

variable "training_coach_enabled" {
  description = "Ativa o Training Coach apenas depois de configurar Gemini."
  type        = bool
  default     = false
}

variable "better_stack_enabled" {
  description = "Ativa alertas Better Stack apenas depois de configurar o respetivo DSN."
  type        = bool
  default     = false
}
