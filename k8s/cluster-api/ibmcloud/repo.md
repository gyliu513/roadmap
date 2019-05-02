### New Repo, Staging Repo, or migrate existing
Migrate existing

### Requested name for new repository
cluster-api-provider-ibmcloud

### Which Organization should it reside
kubernetes-sigs

### If not a staging repo, who should have admin access
@gyliu513 

### If not a staging repo, who should have write access
I can set this up once we get migrated in.

### If not a staging repo, who should be listed as approvers in OWNERS
We already have OWNER and OWNERS_ALIASES:
- https://github.com/multicloudlab/cluster-api-provider-ibmcloud/blob/master/OWNERS_ALIASES
- https://github.com/multicloudlab/cluster-api-provider-ibmcloud/blob/master/OWNERS

### If not a staging repo, who should be listed in SECURITY_CONTACTS
We already have https://github.com/multicloudlab/cluster-api-provider-ibmcloud/blob/master/SECURITY_CONTACTS

### What should the repo description be
Cluster API implementation for IBM Cloud

### What SIG and subproject does this fall under in sigs.yaml
This is a new subproject for `sig-ibmclloud` called `cluster-api-provider-ibmcloud`.

### Approvals
Please prove you have followed the appropriate approval process for this new
repo by including links to the relevant approvals (meeting minutes, e-mail
thread, etc.)

Authoritative requirements are here: https://git.k8s.io/community/github-management/kubernetes-repositories.md

tl;dr (but really you should read the linked doc, this may be stale)
- If this is a core repository, then sig-architecture must approve
- If this is a SIG repository, then this must follow the procedure spelled out
  in that SIG's charter

### Additional context for request
Any additional information or context to describe the request.
