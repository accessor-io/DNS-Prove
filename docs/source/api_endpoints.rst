REST API Endpoints
================

The DNS Prove API provides RESTful endpoints for DNS verification and proof generation.

Base URL: ``/api/v1``

Authentication
-------------

All endpoints require API key authentication via the ``Authorization`` header:

.. code-block:: text

    Authorization: Bearer <your-api-key>

Endpoints
--------

Verify Domain
~~~~~~~~~~~~

.. http:post:: /verify

   Verify a single domain's DNS records.

   **Example request**:

   .. sourcecode:: http

      POST /verify HTTP/1.1
      Host: api.dns-prove.com
      Authorization: Bearer <your-api-key>
      Content-Type: application/json

      {
          "domain": "example.eth",
          "record_type": "TXT",
          "check_ens": true,
          "priority": 1
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "status": "success",
          "domain": "example.eth",
          "proof": {
              "name": "example.eth",
              "rrsig": { ... },
              "rrset": { ... }
          },
          "timestamp": "2024-01-20T12:34:56Z"
      }

   :reqheader Authorization: Bearer token authentication
   :reqheader Content-Type: application/json
   :resheader Content-Type: application/json

   :<json string domain: Domain name to verify
   :<json string record_type: DNS record type (default: "TXT")
   :<json boolean check_ens: Whether to check ENS resolution
   :<json integer priority: Request priority (1-5)

   :>json string status: Status of verification ("success" or "failed")
   :>json string domain: Domain that was verified
   :>json object proof: DNSSEC proof data
   :>json string timestamp: ISO 8601 timestamp

Batch Processing
~~~~~~~~~~~~~~

.. http:post:: /batch

   Process multiple domains in batch.

   **Example request**:

   .. sourcecode:: http

      POST /batch HTTP/1.1
      Host: api.dns-prove.com
      Authorization: Bearer <your-api-key>
      Content-Type: application/json

      {
          "domains": [
              "example1.eth",
              "example2.eth"
          ],
          "record_type": "TXT",
          "check_ens": true,
          "parallel": true,
          "priority": 1
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "domain": "example1.eth",
              "status": "success",
              "proof": { ... },
              "timestamp": "2024-01-20T12:34:56Z"
          },
          {
              "domain": "example2.eth",
              "status": "failed",
              "error": "Domain not found",
              "timestamp": "2024-01-20T12:34:57Z"
          }
      ]

   :reqheader Authorization: Bearer token authentication
   :reqheader Content-Type: application/json

   :<json array domains: List of domains to process
   :<json string record_type: DNS record type (default: "TXT")
   :<json boolean check_ens: Whether to check ENS resolution
   :<json boolean parallel: Process domains in parallel
   :<json integer priority: Batch priority (1-5)

   :>json array results: Array of verification results

Rate Limiting
------------

The API implements rate limiting:

- ``/verify``: 100 requests per minute
- ``/batch``: 20 requests per minute

Error Responses
-------------

.. sourcecode:: http

   HTTP/1.1 400 Bad Request
   Content-Type: application/json

   {
       "error": "Invalid domain name",
       "detail": "Domain contains invalid characters"
   }

.. sourcecode:: http

   HTTP/1.1 429 Too Many Requests
   Content-Type: application/json

   {
       "error": "Rate limit exceeded",
       "retry_after": 30
   }

Monitoring
---------

The API exposes Prometheus metrics at ``/metrics``:

- ``dns_prove_requests_total``: Total requests processed
- ``dns_prove_request_latency_seconds``: Request latency
- ``dns_prove_cache_hits_total``: Cache hit count
- ``dns_prove_active_requests``: Active request gauge

OpenTelemetry tracing is also available for request tracking. 