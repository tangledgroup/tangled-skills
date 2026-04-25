# JSON Configuration Structure

Caddy's native config is a JSON document:

```json
{
  "admin": {
    "listen": ":2019"
  },
  "logging": {
    "logs": {
      "default": {
        "writer": {
          "output": "file",
          "filename": "/var/log/caddy/access.log"
        }
      }
    }
  },
  "apps": {
    "http": {
      "servers": {
        "example": {
          "listen": [":443"],
          "routes": [
            {
              "handle": [
                {
                  "handler": "subroute",
                  "routes": [
                    {
                      "handle": [
                        {
                          "handler": "static_response",
                          "body": "Hello, world!"
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ],
          "tls_connection_policies": [...],
          "listeners": [...]
        }
      }
    },
    "tls": {
      "automation": {
        "policies": [...]
      }
    },
    "pki": {
      "cas": {
        "local": {}
      }
    }
  }
}
```
