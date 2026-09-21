output "artifact_repository" {
  description = "Destino onde sera publicada a imagem da aplicacao."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.application.repository_id}"
}

output "cloud_sql_connection_name" {
  description = "Ligacao interna usada pelo Cloud Run. Nao contem password."
  value       = google_sql_database_instance.alpha.connection_name
}

output "secret_names" {
  description = "Cofres vazios que ainda tera de preencher manualmente."
  value       = sort(tolist(local.secret_ids))
}

output "service_url" {
  description = "Endereco da aplicacao; vazio durante a primeira fase."
  value       = var.deploy_application ? google_cloud_run_v2_service.application[0].uri : null
}
