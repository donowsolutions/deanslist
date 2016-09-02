Deanslist Python API Wrapper
============================

##Examples

Minimal example to get all users
```
DEANSLIST_SUBDOMAIN = 'my.deanslist.url'
dl_client = DeansList(DEANSLIST_SUBDOMAIN, api_key)
dl_client.get_users(show_inactive='Y')
```
