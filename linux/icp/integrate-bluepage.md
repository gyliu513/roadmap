
## Parameters for LDAP Connections
```
"BLUEPAGES": {
               "TYPE": "LDAP",
               "LDAP_ID": "bluepages",
               "LDAP_REALM": "w3",
               "LDAP_HOST": "bluepages.ibm.com",
               "LDAP_PORT": "389",
               "LDAP_IGNORECASE": "true",
               "LDAP_BASEDN": "o=ibm.com",
               "LDAP_BINDDN": "",
               "LDAP_BINDPASSWORD": "",
               "LDAP_TYPE": "IBM Tivoli Directory Server",
               "LDAP_USERFILTER": "(&(emailAddress=%v)(objectclass=person))",
               "LDAP_GROUPFILTER": "(&(cn=%v)(objectclass=groupOfUniqueNames))",
               "LDAP_USERIDMAP": "*:emailAddress",
               "LDAP_GROUPIDMAP": "*:cn",
               "LDAP_GROUPMEMBERIDMAP": "groupOfUniqueNames:uniquemember"
```

```

```
