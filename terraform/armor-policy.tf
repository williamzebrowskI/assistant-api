resource "google_compute_security_policy" "armor_policy" {
  advanced_options_config {
    json_parsing = "DISABLED"
  }

  description = "Policy to add defaults to cloudflare ip ranges and rate limiting"
  name        = "armor-policy"
  project     = local.ws_vars["project-id"]

  rule {
    action      = "allow"
    description = "Cloud Flare IP Range Group B"

    match {
      config {
        src_ip_ranges = ["104.16.0.0/13", "104.24.0.0/14", "131.0.72.0/22", "162.158.0.0/15", "172.64.0.0/13"]
      }

      versioned_expr = "SRC_IPS_V1"
    }

    priority = 150
  }

  rule {
    action      = "allow"
    description = "CloudFlare IP Range Group A"

    match {
      config {
        src_ip_ranges = ["103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22", "108.162.192.0/18", "141.101.64.0/18", "173.245.48.0/20", "188.114.96.0/20", "190.93.240.0/20", "197.234.240.0/22", "198.41.128.0/17"]
      }

      versioned_expr = "SRC_IPS_V1"
    }

    priority = 100
  }

  rule {
    action      = "deny(403)"
    description = "default rule"

    match {
      config {
        src_ip_ranges = ["*"]
      }

      versioned_expr = "SRC_IPS_V1"
    }

    priority = 2147483647
  }

  rule {
    action      = "rate_based_ban"
    description = "Rate Limiting"

    match {
      expr {
        expression = "true"
      }
    }

    priority = 200

    rate_limit_options {
      ban_duration_sec = 180
      conform_action   = "allow"
      exceed_action    = "deny(429)"

      rate_limit_threshold {
        count        = 50
        interval_sec = 120
      }
    }
  }

  type = "CLOUD_ARMOR"
}