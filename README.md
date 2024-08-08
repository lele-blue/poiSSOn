# Very simple and specific SSO

This is an SSO service that is tailored to operate primarily on nginx `auth_request` directive.

# Setup
Something like
```bash
cd src
npm i
npm run build
cd ..
docker compose build
docker compose up
```

Then add this to each server block in nginx where you want to pretect routes (can be an external 
```nginx
            error_page 401 = @error401;
            location /auth/api/ping {
                    internal;
                    proxy_pass 'http://localhost:2312'; # This has to point to your INTERNAL sso instance
                    proxy_set_header Host $host;
                    proxy_set_header X-Original-URL $scheme://$host:$server_port$request_uri;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
            location @error401 {
                    return 302 https://public_sso.domain.url/auth/go/unauthenticated?url=$scheme://$host:$server_port$request_uri; # sso URL, this has to point to your PUBLIC sso instance
            }
            location /_sso/ {
                    proxy_pass http://localhost:2312/auth/crossorigin; # sso URL, this has to point to your INTERNAL sso instance
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
            }
```

And finally this to your locations you want to protect

```nginx
auth_request /auth/api/ping;
```

then create a service via `/auth/go/admin`, fill in sub_url as your nginx location (WITHOUT origin), and use domain:port as origin (no https://)
