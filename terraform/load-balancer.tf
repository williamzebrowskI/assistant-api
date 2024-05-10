
# Create a global external HTTP(S) load balancer
# google_compute_global_forwarding_rule.fafsagpt-fe:
resource "google_compute_global_forwarding_rule" "fafsagpt_fe" {
  ip_address            = google_compute_global_address.fafsagpt_ip_address.address
  ip_protocol           = "TCP"
  labels                = {}
  load_balancing_scheme = "EXTERNAL_MANAGED"
  name                  = "fafsagpt-fe"
  port_range            = "443-443"
  project               = local.ws_vars["project-id"]
  source_ip_ranges      = []
  target                = google_compute_target_https_proxy.fafsagpt_proxy.id
}

resource "google_compute_global_address" "fafsagpt_ip_address" {
  name          = "fafsagpt-ip-address"
  address       = local.ws_vars["address"]
  address_type  = "EXTERNAL"
  ip_version    = "IPV4"
  prefix_length = 0
}

resource "google_compute_ssl_certificate" "cloudflare_cert" {
  name        = "cloudflare-cert"
  description = "cloudflare SSL certificate"
  project     = local.ws_vars["project-id"]
  private_key = data.google_secret_manager_secret_version.bl_wildcard_key.secret_data
  certificate = data.google_secret_manager_secret_version.bl_wildcard_crt.secret_data
}

resource "google_compute_target_https_proxy" "fafsagpt_proxy" {
  name             = "fafsagpt-lb-target-proxy"
  project          = local.ws_vars["project-id"]
  ssl_certificates = [google_compute_ssl_certificate.cloudflare_cert.id]
  url_map          = google_compute_url_map.fafsagpt_url_map.name
}

# google_compute_url_map.fafsagpt_url_map:
resource "google_compute_url_map" "fafsagpt_url_map" {
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }

  host_rule {
    hosts        = ["${local.ws_vars["subdomain"]}.bdtrust.org"]
    path_matcher = local.ws_vars["subdomain"]
  }

  name            = "fafsagpt-lb"
  project         = local.ws_vars["project-id"]

  path_matcher {
    default_service = google_compute_backend_service.fafsagpt_backend.self_link
    name            = local.ws_vars["subdomain"]

    route_rules {
      priority = 100

      route_action {
        weighted_backend_services {
          backend_service = google_compute_backend_service.fafsagpt_backend.self_link
          weight          = 100
        }
      }
    }
  }
}

# google_compute_backend_service.fafsagpt_backend
resource "google_compute_backend_service" "fafsagpt_backend" {
  description           = "Backend service for fafsagpt load balancer"
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL_MANAGED"
  locality_lb_policy    = "ROUND_ROBIN"
  name                  = "fafsagpt-backend"
  port_name             = "http"
  project               = local.ws_vars["project-id"]
  protocol              = "HTTPS"
  security_policy       = google_compute_security_policy.armor_policy.id
  session_affinity      = "NONE"
  timeout_sec           = 30

  backend {
    balancing_mode               = "UTILIZATION"
    capacity_scaler              = 1
    group                        = google_compute_region_network_endpoint_group.fafsagpt_neg.self_link
    max_connections              = 0
    max_connections_per_endpoint = 0
    max_connections_per_instance = 0
    max_rate                     = 0
    max_rate_per_endpoint        = 0
    max_rate_per_instance        = 0
    max_utilization              = 0
  }

  log_config {
    enable      = false
    sample_rate = 0
  }

  timeouts {}
}

# google_compute_region_network_endpoint_group.fafsagpt_neg:
resource "google_compute_region_network_endpoint_group" "fafsagpt_neg" {
  name                  = "fafsagpt-neg"
  network_endpoint_type = "SERVERLESS"
  project               = local.ws_vars["project-id"]
  region                = local.ws_vars["region"]
  cloud_run {
    service = google_cloud_run_v2_service.openai_assistant.name
  }
}

resource "cloudflare_record" "cloudflare_record" {
  zone_id = local.ws_vars["zone_id"]
  name    = local.ws_vars["subdomain"]
  proxied = true
  type    = "A"
  value   = google_compute_global_address.fafsagpt_ip_address.address
  ttl     = 1
}

resource "google_compute_global_forwarding_rule" "fafsa_fe_http" {
  ip_protocol           = "TCP"
  ip_version            = "IPV4"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  name                  = "fafsa-fe-http"
  port_range            = "80-80"
  project               = local.ws_vars["project-id"]
  target                = google_compute_target_http_proxy.fafsa_lb_target_proxy_2.id
}

resource "google_compute_target_http_proxy" "fafsa_lb_target_proxy_2" {
  name    = "fafsa-lb-target-proxy-2"
  project = local.ws_vars["project-id"]
  url_map = google_compute_url_map.fafsagpt_url_map.id
}