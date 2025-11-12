TOKEN_URL="http://localhost:8080/realms/my-scd-realm/protocol/openid-connect/token"

curl -X POST "$TOKEN_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=my-scd-client" \
  -d "code=66375ca0-a3e1-4540-b063-2bf0e5813425.34756fd2-5a79-489d-800d-44212b4e0078.079fedf8-950a-4f56-8815-5e3c73b98acb" \
  -d "redirect_uri=https://oidcdebugger.com/debug" > data.txt
