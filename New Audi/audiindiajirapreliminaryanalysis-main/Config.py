JIRA_TOKEN = 'Basic YWtzaGF5LnNvbXZhbnNoaUBjZXJlbmNlLmNvbTpBVEFUVDN4RmZHRjBOY1lXR0hRU0xkMi1sZ3VfN3U1TkpqczkwTEZTOENZY3BDTU96cEtVa1UwWnhGRzE1ZmxsaFdxbER3MkN5cXNJWGE2SG5wazNhZXpFaGNuamhrNE91ZUR3Q2NfeXdNSkozaHh4QjZNalI4MXY3RDRMTzVQUXY1T3JpN2NtY1o5TFRjejNHbDZrNDUtc1F1dGV0UkoxMFpNWWpnNkRSUzNzSnpnRUJSYUdYNUk9NEZCMTEzQkQ='

# Jira APIs
WAITING_FOR_SUPPORT_TICKETS_URI = 'https://cerence.atlassian.net/rest/api/2/search?jql=project=AUDIIND AND status="Waiting for support"'
ADD_COMMENT1 = 'https://cerence.atlassian.net/rest/api/3/issue/'
ADD_COMMENT2 = '/comment'
CHANGE_TICKET_STATUS1 = 'https://cerence.atlassian.net/rest/api/2/issue/'
CHANGE_TICKET_STATUS2 = '/transitions'
CHANGE_TICKET_ASSIGNEE1 = 'https://cerence.atlassian.net/rest/api/2/issue/'
CHANGE_TICKET_ASSIGNEE2 = '/assignee'

# Audi Token generation API
TOKEN_URI = 'https://audiindia-myaudiconnect.in.onecloud.cerenceapi.com/api/identity/v1/auth/users/cerence/login'

GET_DEVICE_DETAILS = 'https://audiindia-myaudiconnect.in.onecloud.cerenceapi.com/api/inventory/v1/devices/'
GET_LAST_SEEN_DETAILS = 'https://audiindia-myaudiconnect.in.onecloud.cerenceapi.com/api/v1/car/'
GET_DEVICE_STATUS1 = 'https://audiindia-myaudiconnect.in.onecloud.cerenceapi.com/api/bff/v1/devices/user-mapped?imei='
GET_DEVICE_STATUS2 = '&page=0&size=10&sort=userMappedAt,desc'