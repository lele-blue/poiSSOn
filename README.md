# Very simple and specific SSO

This is an SSO service that is tailored to operate primarily on the nginx `auth_request` directive.

## Key features:
* Can easily be retrofitted to services that don't support authentication (like static sites), or SSO (i retrofitted FoundryVTT with this)
* Provides anonymous One time code login for users without an account
* Provides a OIDC interface for services that support OAuth (may need a bit more work though, very basic atm)
* Provides a dashboard with a collection of links that is configurable per user

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

Note: The nginx service can also be external, in that case replace the URL `web` below with `localhost`, assuming everything is on one server

Then add this to each server block in nginx where you want to pretect routes (which can be cross-origin, in that case the user session is transferred between origins)
```nginx
            error_page 401 = @error401;
            location /auth/api/ping {
                    internal;
                    proxy_pass 'http://web:2312'; # This has to point to your INTERNAL sso instance
                    proxy_set_header Host $host;
                    proxy_set_header X-Original-URL $scheme://$host:$server_port$request_uri;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
            location @error401 {
                    return 302 https://public_sso.domain.url/auth/go/unauthenticated?url=$scheme://$host:$server_port$request_uri; # sso URL, this has to point to your PUBLIC sso instance
            }
            location /_sso/ {
                    proxy_pass http://web:2312/auth/crossorigin; # sso URL, this has to point to your INTERNAL sso instance
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

Your may also want to create a UserServiceConnection, which is basically a permission grant for a user (leave username and passwordPlain empty, those are for more advanced retrofitting)
