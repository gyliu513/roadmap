
/* $Id: egomodule.c,v 1.1.2.31 2013/10/09 08:23:39 gyliu Exp $
 *
 * TODO:
 *
 * - implement complete set of APIs
 * - better error checking
 */

#include <Python.h>
#include "structmember.h"
#include "vem.api.h"
#include "esc.api.h"
#include "hash.h"
#include "link.h"
#include "lib.resreq.h"

static PyObject *EGOError;

static char *safe_strdup(char *);
static void *gcalloc(size_t, size_t);
static void topo_parser(PyObject *dict, ego_topo_t **p);
static void topo_policy_parser(PyObject *dict, ego_topo_policy_t **p);
static void inter_sub_demand_policy_parser(PyObject *dict, ego_inter_sub_demand_policy_t **p);
static void ego_alloc_sub_demand_parser(PyObject *dict, ego_alloc_sub_demand_t **p);

static char *   conv_py2str(PyObject *);
static int      conv_py2int(PyObject *);
static int      get_py_list_size(PyObject *);

static char *
safe_strdup(char *p)
{
    if(NULL == p) {
        return NULL;
    } else {
        return strdup(p);
    }
}

static PyObject *
py_error()
{
    return PyErr_Format(EGOError,
            "EGO error code: %d, EGO error message: %s",
            egoerrno, ego_strerror(egoerrno));
}

static void *
gcalloc(size_t n, size_t L)
{
    void *p;

    assert(n > 0 && L > 0);

    p = calloc(n, L);
    if (p == NULL) {
        fprintf(stderr, "gcalloc: calloc failed! "
                "The number of members to be allocated from memory is %u. "
                "The size of each member is %u byte(s).", (unsigned int) n,
                (unsigned int) L);
        exit(-1);
    }

    return (p);

} /* gcalloc() */


static char *
conv_py2str(PyObject *io)
{
    if(NULL == io || !PyString_Check(io)) {
        return NULL;
    } else {
        return PyString_AsString(io);
    }
}

static int
conv_py2int(PyObject *io)
{
    if(NULL == io || !PyInt_Check(io)) {
        return 0;
    } else {
        return (int)PyInt_AsLong(io);
    }
}

static int
get_py_list_size(PyObject *io)
{
    if(NULL == io || !PyList_Check(io)) {
        return 0;
    } else {
        return PyList_Size(io);
    }
}

typedef struct {
    PyObject_HEAD ego_handle_t * handle;
    char *cred; /* User credential */
} PyEGO;

static void
PyEGO_dealloc(PyEGO * self)
{
#ifdef _DEBUG
    fprintf(stderr, "PyEGO_dealloc\n");
#endif

    if (self->handle != NULL) {
        /* Close connection to EGO */
        ego_close(&(self->handle));
        self->handle = NULL;
    }

    self->ob_type->tp_free((PyObject *) self);
}   /* PyEGO_dealloc() */

static PyMemberDef PyEGO_members[] = {
    {NULL}
};  /* PyEGO_members */

static int
PyEGO_init(PyEGO * self, PyObject * args, PyObject * kwds)
{
#ifdef _DEBUG
    fprintf(stderr, "PyEGO_init()\n");
#endif
    vem_initialize();
    return 0;
}   /* PyEGO_init() */

static PyObject *
PyEGO_new(PyTypeObject * type, PyObject * args, PyObject * kwds)
{
    PyEGO *self;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_new()\n");
#endif

    self = (PyEGO *) type->tp_alloc(type, 0);
    if (self != NULL) {
        /* TODO: do initialization stuff here */
    }

    return (PyObject *) self;
}   /* PyEGO_new() */

static PyObject *
PyEGO_uname(PyEGO * self, PyObject * args)
{

    int retval = 0;
    struct ego_name *vm = NULL;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_uname(): handle = %p\n", self->handle);
#endif

    vm = ego_uname(self->handle);
    if (!vm) {
        return py_error();
    }
#ifdef _DEBUG
    printf("Cluster name            : %s\n", vm->clustername);
    printf("EGO master host name    : %s\n", vm->sysname);
    if (vm->patch_ver == 0)
        printf("EGO master version      : %3.1f\n", vm->version);
    else
        printf("EGO master version      : %3.1f.%hd\n", vm->version,
            vm->patch_ver);
#endif
    ego_free_uname(vm);
    return Py_BuildValue("bs", (retval == 0), ego_strerror(egoerrno));
}   /* PyEGO_logoff() */


static PyObject *
PyEGO_open(PyEGO * self, PyObject * args)
{
    self->handle = ego_open(NULL);
    if (self->handle == NULL) {
        /* TODO: handle this error; throw an exception or something useful */
#ifdef _DEBUG
        fprintf(stderr, "Error: ego_open() failed (%s)\n",
            ego_strerror(egoerrno));
#endif
        PyErr_SetString(EGOError, ego_strerror(egoerrno));

        return py_error();
    }
#ifdef _DEBUG
    fprintf(stderr, "PyEGO_open(): handle = %p\n", self->handle);
#endif

    return Py_BuildValue("b", self->handle != NULL);    /* Boolean */
}   /* PyEGO_open() */

static PyObject *
PyEGO_close(PyEGO * self, PyObject * args)
{
    assert(self != NULL);

    if (self->handle == NULL) {
        /* EGO handle is not open, return an error */
        Py_RETURN_FALSE;
    }
#ifdef _DEBUG
    fprintf(stderr, "PyEGO_close(): handle = %p\n", self->handle);
#endif

    ego_close(&(self->handle));
    self->handle = NULL;

    Py_RETURN_TRUE;
}   /* PyEGO_close() */

static int
common_ego_register(PyEGO * self, const char *clientname, const char *descr)
{
    struct ego_registerreq *r = NULL;
    struct ego_recoveryinfo *info = NULL;
    int rc;

    r = ego_alloc_registerreq();
    if (r == NULL) {
        return -1;
    }

    r->name = (char *) clientname;
    r->description = (char *) descr;
    r->flags = EGO_REGISTER_TTL | EGO_REGISTER_FORCE | EGO_REGISTER_RECOVERABLE;
    r->ttl = EGO_MAX_TTL;

    rc = ego_register(self->handle, r, &info);

    ego_free_registerreq(r);
    ego_free_recoveryinfo(info);
    return (rc);
}   /* common_ego_register() */

static PyObject *
PyEGO_register(PyEGO * self, PyObject * args)
{
    int retval;
    const char *clientname = NULL;
    const char *descr = NULL;

    assert(self->handle != NULL);

    /* Both clientname and descr are optional parameters */
    PyArg_ParseTuple(args, "|ss", &clientname, &descr);

    retval = common_ego_register(self, clientname, descr);
    if (retval < 0) {
        return py_error();
    }

    return Py_BuildValue("b", (retval == 0));
}   /* PyEGO_register() */

static PyObject *
PyEGO_unregister(PyEGO * self, PyObject * args)
{
    int retval;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_unregister(): handle = %p\n", self->handle);
#endif

    retval = ego_unregister(self->handle);
    if (retval < 0) {
        return py_error();
    }

    return Py_BuildValue("b", (retval == 0));
}   /* PyEGO_unregister() */

static PyObject *
PyEGO_logon(PyEGO * self, PyObject * args)
{
    const char *username;
    const char *password;
    int retval;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_logon()\n");
#endif

    if (self->handle == NULL) {
#ifdef _DEBUG
        fprintf(stderr, "Error: ego is not connected\n");
#endif
        Py_RETURN_FALSE;
    }

    PyArg_ParseTuple(args, "ss", &username, &password);

#ifdef _DEBUG
    fprintf(stderr,
        "PyEGO_logon(): handle = %p, username = %s, password = %s\n",
        self->handle, username, password);
#endif

    retval = ego_logon(self->handle, (char *) username, (char *) password,
        &self->cred);
    if (retval != 0) {
        return py_error();
    }

    return Py_BuildValue("b", (retval == 0));
}   /* PyEGO_logon() */

static PyObject *
PyEGO_logonAndRegister(PyEGO * self, PyObject * args)
{
    const char *username = NULL;
    const char *password = NULL;
    const char *clientname = NULL;
    const char *descr = NULL;
    int retval;

    PyArg_ParseTuple(args, "ss|ss", &username, &password, &clientname, &descr);

    retval = ego_logon(self->handle, (char *) username, (char *) password,
        &self->cred);
    if (retval != 0) {
        return py_error();
    }

    retval = common_ego_register(self, clientname, descr);
    if (retval < 0) {
        return py_error();
    }

    return Py_BuildValue("b", (retval == 0));
}   /* PyEGO_logonAndRegister() */


/*
 * ego_allocreply
 *
 * allocId (string)
 * consumer (string)
 * ego_host_t (array)
 * hostattributes (array)
 * clientName (array)
 */

static PyObject *
PyEGO_read_resource_add(ego_allocreply_t * allocreply)
{
    int nCount;
    PyObject *hostList, *retval;

    hostList = PyList_New(allocreply->nhost);
    assert(hostList != NULL);

    for (nCount = 0; nCount < allocreply->nhost; nCount++) {
        PyObject *host;

        host = Py_BuildValue("(sssiss)",
                allocreply->host[nCount]->name,
                allocreply->host[nCount]->schedDecID,
                allocreply->host[nCount]->subDemandname,
                allocreply->host[nCount]->slots,
                allocreply->host[nCount]->resreq,
                allocreply->host[nCount]->resourceGroup
                );
        assert(host != NULL);

        PyList_SetItem(hostList, nCount, host);
    }

    retval = Py_BuildValue("(issOs)", 0, allocreply->allocId,
        allocreply->consumer, hostList, allocreply->clientName);

    Py_DECREF(hostList);
    return retval;
}   /* PyEGO_read_resource_add() */

static PyObject *
PyEGO_read(PyEGO * self, PyObject * args)
{
    int retval;
    ego_message_t *msg = NULL;
    PyObject *obj = NULL;

    assert(self != NULL);

    retval = ego_read(self->handle, &msg);
    if (retval != 0) {
        return py_error();
    }

    switch (msg->code) {
        case RESOURCE_ADD:
            obj = PyEGO_read_resource_add((ego_allocreply_t *) msg->content);
            break;
        default:
            obj = Py_BuildValue("(i)", 1);
            break;
    }

    ego_free_message(msg);
    return (obj);
}   /* PyEGO_read() */

static PyObject *
PyEGO_select(PyEGO * self, PyObject * args)
{
    int retval;
    struct timeval tv = { 0, 0 };
    int timeout = 0;

    assert(self != NULL);

    PyArg_ParseTuple(args, "i", &timeout);

    tv.tv_sec = timeout;

    if (self->handle == NULL) {
        return py_error();
    }

    retval = ego_select(self->handle, &tv);
    if (retval < 0) {
        return py_error();
    }

    return Py_BuildValue("i", retval);
}   /* PyEGO_select() */

static PyObject *
PyEGO_setResourceInfo(PyEGO * self, PyObject * args)
{
    char *cstr = NULL;
    int retval;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_setResourceInfo()\n");
#endif

    assert(self->handle);

    PyArg_ParseTuple(args, "s", &cstr);

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_setResourceInfo(): cstr = %s\n", cstr);
#endif

    retval = ego_updaterpiresourceinfo(self->handle, cstr);

    if (retval < 0) {
        return py_error();
    }

    return Py_BuildValue("i", retval);
}   /* PyEGO_setResourceInfo() */

static PyObject *
PyEGO_setResourcePlan(PyEGO * self, PyObject * args)
{
    char *cstr = NULL;
    int retval;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_setResourcePlan()\n");
#endif

    assert(self->handle);

    PyArg_ParseTuple(args, "s", &cstr);

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_setResourcePlan(): xmlstr = %s\n", cstr);
#endif

    retval = ego_setresourceplan(self->handle, "/", cstr, FALSE);

    if (retval < 0) {
        return py_error();
    }

    return Py_BuildValue("i", retval);
}   /* PyEGO_setResourcePlan() */

static PyObject *
PyEGO_getRPIRes(PyEGO * self, PyObject * args)
{
    struct rpiResource **rpiInfos = NULL;
    char *cstr = NULL;
    PyObject *hostlist;
    PyObject *host;
    int nCount = 0;
    int count = 0;
    struct rpiResource **resPtr = NULL;
    struct rpiAttribute **attr;
    struct ego_resreq *resreq = NULL;

#ifdef _DEBUG
    fprintf(stderr, "PyEGO_getRPIRes(): handle = %p\n", self->handle);
#endif
    PyArg_ParseTuple(args, "s", &cstr);

    resreq = ego_parseresreq(cstr);
    if (resreq == NULL) {
        return py_error();
    }
    ego_freeresreq(&resreq);

    rpiInfos = ego_getrpiresourceinfo(self->handle, cstr);

    if (rpiInfos == NULL) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        hostlist = PyList_New(0);
        return Py_BuildValue("O", hostlist);
    }
    resPtr = rpiInfos;
    while (resPtr[count]) {
        count++;
    }

    if (!count) {
        hostlist = PyList_New(0);
        return Py_BuildValue("O", hostlist);
    }

    hostlist = PyList_New(count);
    if (hostlist == NULL) {
        return NULL;
    }

    for (nCount = 0; nCount < count; nCount++) {
        attr = rpiInfos[nCount]->attributes;
        host = PyDict_New();
        PyDict_SetItem(host,
                       Py_BuildValue("s", "name"),
                       Py_BuildValue("s", rpiInfos[nCount]->name));
        PyDict_SetItem(host,
                       Py_BuildValue("s", "state"),
                       Py_BuildValue("i",rpiInfos[nCount]->state));
        PyList_SetItem(hostlist, nCount, host);
    }

    ego_free_rpiresource_array(rpiInfos);
    return hostlist;
}   /* PyEGO_getRPIRes() */


static void
topo_parser(PyObject *dict, ego_topo_t **p)
{
    if(NULL == dict) {
        return;
    }

    (*p) = gcalloc(1, sizeof(ego_topo_t));
    (*p)->pTopoNS = safe_strdup(conv_py2str(PyDict_GetItemString(dict, "namespace")));
    (*p)->pTopoLvl = safe_strdup(conv_py2str(PyDict_GetItemString(dict, "level")));
    (*p)->nMinTopoNode = conv_py2int(PyDict_GetItemString(dict, "min_nodes"));
    (*p)->nMaxSlotsPerNode = conv_py2int(PyDict_GetItemString(dict, "max_slots_per_host"));
}

/* Parse ego_topo_policy_t */
static void
topo_policy_parser(PyObject *dict, ego_topo_policy_t **p)
{
    if(NULL == dict) {
        return;
    }

    (*p) = gcalloc(1, sizeof(ego_topo_policy_t));

    (*p)->nPolicyType = conv_py2int(PyDict_GetItemString(dict, "policy_type"));

    if(PyDict_Contains(dict, PyString_FromString("policy_flag"))) {
        (*p)->nPolicyFlag = conv_py2int(PyDict_GetItemString(dict, "policy_flag"));
    } else {
        (*p)->nPolicyFlag = 1;
    }

    topo_parser(PyDict_GetItemString(dict, "topology"), &(*p)->pPolicyTopo);

}
/* Parse ego_topo_policy_t end */

/* Parse ego_inter_sub_demand_policy_t */
static void
inter_sub_demand_policy_parser(PyObject *dict, ego_inter_sub_demand_policy_t **p)
{
    int         i = 0;
    int         tmpNum = 0;
    PyObject    *tmpList = NULL;

    if(NULL == dict) {
        return;
    }

    tmpList = PyDict_GetItemString(dict, "sub_demands");
    tmpNum = get_py_list_size(tmpList);
    if(tmpNum > 0) {
        (*p) = gcalloc(1, sizeof(ego_inter_sub_demand_policy_t));

        (*p)->nSubDmd = tmpNum;

        (*p)->vecSubDmdName = gcalloc(tmpNum, sizeof(char *));
        for(i = 0; i < tmpNum; i++) {
            (*p)->vecSubDmdName[i] = safe_strdup(conv_py2str(PyList_GetItem(tmpList, i)));
        }
    }

    topo_policy_parser(PyDict_GetItemString(dict, "policy"), &(*p)->pTPolicy);
}
/* Parse ego_inter_sub_demand_policy_t end */

/* parse ego_alloc_sub_demand_t */
static void
ego_alloc_sub_demand_parser(PyObject *dict, ego_alloc_sub_demand_t **p)
{
    int         i = 0;
    int         num = 0;
    PyObject    *tmpList;

    if(NULL == dict) {
        return;
    }

    (*p) = gcalloc(1, sizeof(ego_alloc_sub_demand_t));
    (*p)->name = safe_strdup(conv_py2str(PyDict_GetItemString(dict, "name")));
    (*p)->resreq = safe_strdup(conv_py2str(PyDict_GetItemString(dict, "resreq")));
    (*p)->extraResreq = safe_strdup(conv_py2str(PyDict_GetItemString(dict, "extra_resreq")));
    (*p)->maxslots = conv_py2int(PyDict_GetItemString(dict, "maxslots"));
    (*p)->flag = 0;
    if(conv_py2int(PyDict_GetItemString(dict, "force_realloc_migrate"))) {
        (*p)->flag |= EGO_REALLOC_MIGRATE_FORCE;
    }
    if(conv_py2int(PyDict_GetItemString(dict, "clear_policy"))) {
        (*p)->flag |= EGO_FORCE_CLEAN_POLICY;
    }
    if(PyDict_Contains(dict, PyString_FromString("policy"))) {
        tmpList = PyDict_GetItemString(dict, "policy");
        num = get_py_list_size(tmpList);
        if(num > 0) {
            (*p)->nPolicy = num;
            (*p)->vecTPolicy = gcalloc(num, sizeof(ego_topo_policy_t *));
            for(i = 0; i < num; i++) {
                topo_policy_parser(PyList_GetItem(tmpList, i), &(*p)->vecTPolicy[i]);
            }
        }
    }
}
/* parse ego_alloc_sub_demand_t end */

static PyObject *
PyEGO_create_alloc(PyEGO * self, PyObject * args)
{
    ego_allocreq_t          *areq = NULL;
    ego_allocation_id_t     alocid = NULL;
    int                     rc = 0;
    int                     forceOverCommit = 0;
    char                    *name = NULL;
    char                    *consumer = NULL;
    PyObject                *interPolicies = NULL;  /* list -> dict == {subDemands:[name1,name2], policy:dict} */
    int                     nInterSubDmdPolicy = 0;
    PyObject                *subDemand = NULL;      /* list -> dict */
    int                     numSubDemand = 0;
    int                     i = 0;
    PyObject                *tmpDict = NULL;
    PyObject                *obj = NULL;

    /* allocate areq */
    areq = ego_alloc_allocreq();
    if (areq == NULL) {
        return py_error();
    }

    /* Parse args */
    PyArg_ParseTuple(args, "ssOO", &name, &consumer, &interPolicies, &subDemand);

    /* asign value */
    areq->name      = safe_strdup(name);
    areq->consumer  = safe_strdup(consumer);
    areq->resplan   = strdup(PRS_DEFAULT_PLAN_NAME);
    areq->tile      = 0;
    areq->maxslots  = 1;

    if (forceOverCommit) {
        areq->flags |= EGO_REALLOC_MIGRATE_FORCE;
    }

    numSubDemand = get_py_list_size(subDemand);
    if(numSubDemand > 0) {
        areq->flags |= VEM_ALLOC_SUB_DEMAND;
        areq->numSubDemand = numSubDemand;
        areq->subdemands = gcalloc(numSubDemand, sizeof(ego_alloc_sub_demand_t *));
        for(i = 0; i < numSubDemand; i++) {
            tmpDict = PyList_GetItem(subDemand, i);
            ego_alloc_sub_demand_parser(tmpDict, &areq->subdemands[i]);
        }
    }

    /* interPolicies */
    nInterSubDmdPolicy = get_py_list_size(interPolicies);
    if(nInterSubDmdPolicy > 0) {
        areq->nInterSubDmdPolicy = nInterSubDmdPolicy;
        areq->vecInterSubDmdPolicy = gcalloc(nInterSubDmdPolicy, sizeof(ego_inter_sub_demand_policy_t *));
        for(i=0; i<nInterSubDmdPolicy; i++) {
            tmpDict = PyList_GetItem(interPolicies,i);
            inter_sub_demand_policy_parser(tmpDict, &areq->vecInterSubDmdPolicy[i]);
        }
    }

    /* call ego native function */
    rc = ego_alloc(self->handle, areq, &alocid);

    ego_free_allocreq(areq);
    if (rc < 0) {
        return py_error();
    }

    /* Build Return Value */
    obj = Py_BuildValue("is", rc, alocid);
    ego_free_allocation_id(alocid);
    return (obj);
}

static PyObject *
PyEGO_resize_alloc(PyEGO * self, PyObject * args)
{
    /* args var */
    char                *allocId = NULL;
    PyObject            *subDemand = NULL; /* list -> dict */

    /* return var */
    int                 rc = 0;
    PyObject            *obj = NULL;

    /* temporary var */
    int                 i = 0;
    int                 numSubDemand = 0;
    ego_reallocreq_t    *req = NULL;
    PyObject            *tmpDict = NULL;

    /* allocate areq */
    req = ego_alloc_reallocreq();
    if (req == NULL) {
        return py_error();
    }

    /* parse args */
    PyArg_ParseTuple(args, "sO", &allocId, &subDemand);

    /* asign value */
    req->flags = 0;
    req->flags |= VEM_ALLOC_SUB_DEMAND;
    req->newMaxSlot = 999999;
    req->allocId = safe_strdup(allocId);

    /* subDemand */
    numSubDemand = get_py_list_size(subDemand);
    if(numSubDemand > 0) {
        req->numSubDemand = numSubDemand;
        req->subdemands = gcalloc(numSubDemand, sizeof(ego_alloc_sub_demand_t *));
        for(i = 0; i < numSubDemand; i++) {
            tmpDict = PyList_GetItem(subDemand, i);
            ego_alloc_sub_demand_parser(tmpDict, &req->subdemands[i]);
        }
    }
    /* subDemand end */

    rc = ego_realloc(self->handle, req);
    ego_free_reallocreq(req);
    if (rc < 0) {
        return py_error();
    }

    obj = Py_BuildValue("is", rc, allocId);
    return (obj);
}   /* PyEGO_resize_alloc */

static PyObject *
PyEGO_updateDecision(PyEGO *self, PyObject *args)
{
    /* args var */
    char *allocId = NULL;
    char *decId = NULL;
    char *resreq = NULL;
    char *extraResreq = NULL;
    int prefer_same_host = 0;
    int force_realloc_migrate = 0;
    int use = 0;

    /* return var */
    int rc = 0;
    PyObject *obj = NULL;

    /* temporary var */
    ego_updatedecisionreq_t *req = NULL;

    /* parse args */
    PyArg_ParseTuple(args, "ssssiii", &allocId, &decId, &resreq, &extraResreq, &prefer_same_host, &force_realloc_migrate, &use);

    req = gcalloc(1, sizeof(ego_updatedecisionreq_t));
    req->allocId = allocId;
    req->schedDecId = decId;
    req->resreq = resreq;
    req->extraResreq = extraResreq;
    req->use = use;

    if (prefer_same_host) {
        req->flag |= EGO_REALLOC_PREFERSAME;
    }
    if (force_realloc_migrate) {
        req->flag |= EGO_REALLOC_MIGRATE_FORCE;
    }

    rc = ego_update_decision(self->handle, req);
    FREEUP(req);

    if (rc < 0) {
        return py_error();
    }

    obj = Py_BuildValue("is", rc, allocId);
    return (obj);
}

static PyObject *
PyEGO_releaseDecision(PyEGO *self, PyObject *args)
{
    char *allocId = NULL;
    char *decId = NULL;

    int rc = 0;
    PyObject *obj = NULL;

    ego_releasereq_t *req = NULL;

    PyArg_ParseTuple(args, "ss", &allocId, &decId);

    req = gcalloc(1, sizeof(ego_releasereq_t));
    req->allocId = allocId;
    req->nhosts = 1;
    req->hosts = gcalloc(1, sizeof(ego_host_t));
    req->hosts->schedDecID = decId;

    rc = ego_release(self->handle, req);
    FREEUP(req->hosts);
    FREEUP(req);

    if (rc < 0) {
        return py_error();
    }

    obj = Py_BuildValue("is", rc, allocId);
    return (obj);
}

static PyObject *
PyEGO_free_alloc(PyEGO * self, PyObject * args)
{
    ego_allocfreereq_t *afree = NULL;
    char *allocid = NULL;
    int rc = 0;

    PyArg_ParseTuple(args, "s", &allocid);

    afree = ego_alloc_allocfreereq();
    afree->allocId = allocid;

    rc = ego_allocfree(self->handle, afree);

    ego_free_allocfreereq(afree);

    if (rc < 0) {
        return py_error();
    }
    return Py_BuildValue("i", rc);
}   /* PyEGO_free_alloc */


static PyObject *
PyEGO_migrate_decision(PyEGO * self, PyObject * args)
{
    char *schedDecID = NULL;
    char *allocID = NULL;
    char *extraResreq = NULL;
    int forceOverCommit = 0;

    PyArg_ParseTuple(args, "ssis", &schedDecID, &allocID,
		                    &forceOverCommit, &extraResreq);

    int cc = 0;
    struct ego_migratedecision *mig;

    mig = ego_alloc_migratedecision();
    mig->policyPlugin = "prs";
    mig->schedDecID = schedDecID;
    mig->allocID = allocID;
    mig->extraResreq= extraResreq;
    if (forceOverCommit) {
        mig->flags |= EGO_REALLOC_MIGRATE_FORCE;
    }

    cc = ego_migratedecision(self->handle, mig);
    ego_free_migratedecision(mig);
    if (cc != 0) {
        return py_error();
    }

    return Py_BuildValue("i", cc);
}   /* PyEGO_migrate_decision */

static PyObject *
PyEGO_delete_dynamic_resource_group(PyEGO *self, PyObject *args)
{

    char *name = NULL;

    PyArg_ParseTuple(args, "s", &name);

    if (ego_delhostgroup(self->handle, name) < 0){
        return py_error();
    }

    return Py_BuildValue("i", 0);
}

#define DYNAMIC_HOST 1

static PyObject *
PyEGO_create_dynamic_resource_group(PyEGO * self, PyObject * args)
{
    int resPluginNum = 1, i = 0;
    ego_hostgroupconf_t *hostGroupConf = NULL;

    char *name = NULL;
    char *resReq = NULL;
    char *schedPluginName = "prs";

    PyArg_ParseTuple(args, "ss", &name, &resReq);

    /* Allocate host group config structure, and fill it */
    hostGroupConf = ego_alloc_hostgroupconf(0);
    if (hostGroupConf == NULL) {
        return py_error();
    }

    hostGroupConf->type = DYNAMIC_HOST;

    hostGroupConf->groupname = name;
    hostGroupConf->desc = "Created by openstack";
    hostGroupConf->resreq = resReq;
    hostGroupConf->schedPlugin = schedPluginName;
    if (hostGroupConf->groupname == NULL
        || hostGroupConf->resreq == NULL
        || hostGroupConf->schedPlugin == NULL) {
        ego_free_hostgroupconf(hostGroupConf);
#ifdef _DEBUG
        fprintf(stderr, "\
PyEGO_create_dynamic_resource_group: create dynamic resource group failed because some key values are null\n");
#endif
        return py_error();
    }

    hostGroupConf->nResPlugin = 1;
    hostGroupConf->resPluginList =
        (char **) calloc(hostGroupConf->nResPlugin, sizeof(char *));
    for (i = 0; i < resPluginNum; i++) {
        hostGroupConf->resPluginList[i] = "dynamic";
    }

    /* Add resource group */
    if (ego_addhostgroup(self->handle, hostGroupConf) < 0) {
        ego_free_hostgroupconf(hostGroupConf);
        return py_error();
    }

    ego_free_hostgroupconf(hostGroupConf);
    return Py_BuildValue("i", 0);

}   /* PyEGO_create_dynamic_resource_group */


static PyObject *
PyEGO_getAllAlloc(PyEGO * self, PyObject * args)
{
    int naoc = 0;
    int nCount = 0;
    ego_allocinforeq_t *req = NULL;
    ego_allocation_t **alloc = NULL;
    PyObject *alloclist = NULL;
    PyObject *decisionlist = NULL;
    int i = 0;
    int num = 0;

    req = ego_alloc_allocinforeq();
    if (req == NULL) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
    }

    /*call the API */
    naoc = ego_getconsumerallocinfo(self->handle, req, &alloc);
    ego_free_allocinforeq(req);
    if (naoc < 0) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        alloclist = PyList_New(0);
        return Py_BuildValue("O", alloclist);
    }

    if (naoc == 0) {
        ego_free_allocation_array(alloc, naoc);
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        alloclist = PyList_New(0);
        return Py_BuildValue("O", alloclist);
    }

    alloclist = PyList_New(naoc);
    if (alloclist == NULL) {
#ifdef _DEBUG
        fprintf(stderr, "\
PyEGO_getAllAlloc() failed %s\n", ego_strerror(egoerrno));
#endif
        return Py_BuildValue("s", ego_strerror(egoerrno));
    }

    for (nCount = 0; nCount < naoc; nCount++) {
        // build decisionlist
        num = alloc[nCount]->nhost;
        decisionlist = PyList_New(num);
        for(i=0; i< num; i++) {
            PyList_SetItem(decisionlist, i,
                    Py_BuildValue("sssiss", alloc[nCount]->host[i]->name,
                            alloc[nCount]->host[i]->schedDecID,
                            alloc[nCount]->host[i]->subDemandname,
                            alloc[nCount]->host[i]->slots,
                            alloc[nCount]->host[i]->resreq,
                            alloc[nCount]->host[i]->resourceGroup));
        }

        // build alloclist
        PyList_SetItem(alloclist, nCount,
                Py_BuildValue("ssOs", alloc[nCount]->allocReq->name,
                        alloc[nCount]->allocId,
                        decisionlist,
                        alloc[nCount]->client
                )
        );
    }

    ego_free_allocation_array(alloc, naoc);
    return alloclist;
}   /* PyEGO_getAllAlloc() */

static PyObject *
PyEGO_getDecisionsByFilter(PyEGO * self, PyObject * args)
{
    int naoc = 0;
    int nCount = 0;
    ego_decisioninforeq_t *req = NULL;
    vem_host_t **decision = NULL;
    PyObject *decisionlist = NULL;
    PyObject *tmpDict = NULL;
    PyObject *tmpListKey = NULL;
    PyObject *key = NULL;
    int num = 0;
    int i = 0;

    PyArg_ParseTuple(args, "O", &tmpDict);
    if(!PyDict_Check(tmpDict)) {
        return py_error();
    }

    ego_decision_filter_spec_t  **filters = NULL;
    req = ego_decisioninforeq();
    if (req == NULL) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
    }

    num = PyDict_Size(tmpDict);
    if(num > 0){
        req->nfilter = num;
        filters = (ego_decision_filter_spec_t  **)calloc(num, sizeof(ego_decision_filter_spec_t  *));
        tmpListKey = PyDict_Keys(tmpDict);
        for(i=0;i<num;i++){
            key = PyList_GetItem(tmpListKey, i);
            filters[i] = (ego_decision_filter_spec_t  *)calloc(1, sizeof(ego_decision_filter_spec_t ));
            filters[i]->filter = PyInt_AsLong(key);
            filters[i]->value_t = PyString_AsString(PyDict_GetItem(tmpDict, key));
        }

        req->filters = filters;
    }

    /*call the API */
    naoc = ego_getdecisioninfo(self->handle, req, &decision);
    ego_free_decisioninforeq(req);
    FREEUP(filters);

    if (naoc < 0) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        decisionlist = PyList_New(0);
        return Py_BuildValue("O", decisionlist);
    }

    if (naoc == 0) {
        ego_free_decision_array(decision, naoc);
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        decisionlist = PyList_New(0);
        return Py_BuildValue("O", decisionlist);
    }

    decisionlist = PyList_New(naoc);
    if (decisionlist == NULL) {
#ifdef _DEBUG
        fprintf(stderr, "\
PyEGO_getHostDec() failed %s\n", ego_strerror(egoerrno));
#endif
        return Py_BuildValue("s", ego_strerror(egoerrno));
    }

    for (nCount = 0; nCount < naoc; nCount++) {
        if (decision[nCount]->schedDecID[0] != '\0') {
            PyList_SetItem(decisionlist, nCount,
                 Py_BuildValue("sssiss",
                     decision[nCount]->name,
                     decision[nCount]->schedDecID,
                     decision[nCount]->subDemandname,
                     decision[nCount]->slots,
                     decision[nCount]->resreq,
                     decision[nCount]->resourceGroup
                 )
            );
        } else {
            PyList_SetItem(decisionlist, nCount,
                 Py_BuildValue("sssiss",
                     decision[nCount]->name,
                     "",
                     decision[nCount]->subDemandname,
                     decision[nCount]->slots,
                     decision[nCount]->resreq,
                     decision[nCount]->resourceGroup
                )
            );
        }
    }

    ego_free_decision_array(decision, naoc);
    return decisionlist;
}   /* PyEGO_getDecisionsByFilter() */

static PyObject *
PyEGO_getReleaseCandidates(PyEGO *self, PyObject *args)
{
    int num_unit = 0;
    char *allocation_name = NULL;
    char *sub_demand_name = NULL;

    PyObject *obj = NULL;

    PyArg_ParseTuple(args, "ssi", &allocation_name, &sub_demand_name, &num_unit);

    return obj;
}

static PyObject *
PyEGO_getAllocByID(PyEGO * self, PyObject * args)
{
    int naoc = 0;
    int nCount = 0;
    ego_allocinforeq_t *req = NULL;
    ego_allocation_t **alloc = NULL;
    char *allocId = NULL;
    PyObject *obj = NULL;

    PyArg_ParseTuple(args, "s", &allocId);

    req = ego_alloc_allocinforeq();
    if (req == NULL) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
    }

    /* call the API */
    naoc = ego_getconsumerallocinfo(self->handle, req, &alloc);
    ego_free_allocinforeq(req);
    if (naoc < 0) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        obj = PyList_New(0);
        return (obj);
    }

    if (naoc == 0) {
        ego_free_allocation_array(alloc, naoc);

        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        obj = PyList_New(0);
        return (obj);
    }

    for (nCount = 0; nCount < naoc; nCount++) {
        if (strcmp(alloc[nCount]->allocId, allocId) == 0) {
            obj = Py_BuildValue("s", alloc[nCount]->host[0]->name);
            ego_free_allocation_array(alloc, naoc);
            return (obj);
        }
    }

    ego_free_allocation_array(alloc, naoc);

    return py_error();
}   /* PyEGO_getAllocByID() */

static PyObject *
PyEGO_get_possible_hosts(PyEGO * self, PyObject * args)
{
    struct rpiResource **rpiRes = NULL;
    PyObject *hostlist;
    ego_decision_id_t  schedDecId;
    char *extraResreq = NULL;
    struct rpiResource **pRec;
    struct rpiAttribute **attr;
    int nCount = 0;
    int count = 0;
    ego_getpossiblehost_req_t *req;

    PyArg_ParseTuple(args, "ss", &schedDecId, &extraResreq);

    req = ego_alloc_getpossiblehost_req();
    req->schedDecId = schedDecId;
    req->extraResreq = extraResreq;

    rpiRes = ego_getpossiblehosts(self->handle, req);
    ego_free_getpossiblehost_req(req);

    if (rpiRes == NULL) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        hostlist = PyList_New(0);
        return Py_BuildValue("O", hostlist);
    }

    while (rpiRes[count]) {
        count++;
    }
    hostlist = PyList_New(count);

    for (pRec = rpiRes; *pRec; pRec++) {
        int n = 0;
        int findAttr = FALSE;

        attr = rpiRes[nCount]->attributes;
        while (attr[n]) {
            if (strcmp(attr[n]->name, "evaluatedGoal") == 0) {
                PyList_SetItem(hostlist, nCount,
                    Py_BuildValue("sd", rpiRes[nCount]->name, attr[n]->u.dval));
                findAttr = TRUE;
                break;
            }
            ++n;
        }

        if (!findAttr) {
            PyList_SetItem(hostlist, nCount,
                Py_BuildValue("s", rpiRes[nCount]->name));
        }
        nCount++;
    }

    ego_free_rpiresource_array(rpiRes);
    return hostlist;
}   /* PyEGO_getAllocByID() */

static PyObject *
PyEGO_get_all_resource_group(PyEGO * self, PyObject * args)
{
    int num, i, cc;
    char *token = NULL;

    ego_hostgroupreq_t *req = NULL;
    ego_hostgroup_t **hginfo = NULL;

    PyObject *memberList = NULL; 
    PyObject *rslt = NULL;

    req = ego_alloc_hostgroupreq();
    if (req == NULL) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        rslt = PyDict_New();
        PyDict_SetItem(rslt, 0, 0);
        return rslt;
    }
    /* get resource group list
     */
    num = ego_gethostgroupinfo(self->handle, req, &hginfo);
    if (num < 0) {
        if (egoerrno != EGOE_NO_ERR) {
            return py_error();
        }
        rslt = PyDict_New();
        PyDict_SetItem(rslt, 0, 0);
        return rslt;
    }
    ego_free_hostgroupreq(req);

    rslt = PyDict_New();
    if (num == 0) {
        PyDict_SetItem(rslt, 0, 0);
        return rslt;
    }

    for (i = 0; i < num; i++) {
         /* count hosts */
        cc = 0;
        if (hginfo[i]->members) {
            char seps[] = " ";
            char *hostlist = safe_strdup(hginfo[i]->members);

            if (!hostlist) {
                if (egoerrno != EGOE_NO_ERR) {
                    return py_error();
                }
                rslt = PyDict_New();
                PyDict_SetItem(rslt, 0, 0);
                return rslt;
            }
            token = strtok(hostlist, seps);
            while (token != NULL) {
                cc++;
                token = strtok(NULL, seps);
            }
            FREEUP(hostlist);
        }
        memberList = PyList_New(cc);
        assert(memberList != NULL);
        if (cc == 0) {
            Py_BuildValue("O", memberList);
        }
        /* reset cc */
        cc = 0;
        PyObject *host = NULL;
        if (hginfo[i]->members) {
            char seps[] = " ";
            char *hostlist = safe_strdup(hginfo[i]->members);
             if (!hostlist) {
                if (egoerrno != EGOE_NO_ERR) {
                    return py_error();
                }
                rslt = PyDict_New();
                PyDict_SetItem(rslt, 0, 0);
                return rslt;
            }
            token = strtok(hostlist, seps);
            while (token != NULL) {
                host = Py_BuildValue("s", token);
                assert(host != NULL);
                PyList_SetItem(memberList, cc, host);
                cc++;
                token = strtok(NULL, seps);
            }
            FREEUP(hostlist);
        }
        PyDict_SetItem(rslt, Py_BuildValue("s", hginfo[i]->groupName), memberList);
        //PyDict_SetItem(rslt, Py_BuildValue("s", hginfo[i]->groupName), Py_BuildValue("O", memberList));
        Py_DECREF(memberList);
    }
    ego_free_hostgroupinfo_array(hginfo, num);
    return rslt;
} /* PyEGO_get_all_resource_group */

/*
 *-------------------------------------------------------------------
 *
 * do_creates
 *
 *  DESCRIPTION: 
 *   Create a specified service.
 *
 *  PARAMETERS:
 *   argc [IN] : the number of parameters
 *   argv [IN] : the parameter array
 *  RETURN:  
 *   NONE
 *--------------------------------------------------------------------
 */
static PyObject *
PyEGO_esc_create_service(PyEGO * self, PyObject * args){
    char      *xmlstr = NULL;
    int       cc;
    esc_security_def_t  sec;
 
    PyArg_ParseTuple(args, "s", &xmlstr);
    
    sec.username = "Admin";
    sec.password = "Admin";
    sec.credential = NULL;
    cc = esc_createservice(xmlstr,&sec);    
    if (cc != 0){
	return Py_BuildValue("b", 0 == 1);
    } else {
        printf("create service success.\n");
    }
 
    return Py_BuildValue("b", 1 == 1);    /* Boolean */
}/* PyEGO_esc_create_service() */

/*
 *-------------------------------------------------------------------
 *
 * do_removes
 *
 *  DESCRIPTION: 
 *   Remove a specified service.
 *
 *  PARAMETERS:
 *   argc [IN] : the number of parameters
 *   argv [IN] : the parameter array
 *  RETURN:  
 *   NONE
 *--------------------------------------------------------------------
 */
static PyObject *
PyEGO_esc_delete_service (PyEGO * self, PyObject * args){
    int    cc;
    char   *name = NULL;
    esc_security_def_t  sec;

    PyArg_ParseTuple(args, "s", &name);

    sec.username = "Admin";
    sec.password = "Admin";
    sec.credential = NULL;
    cc = esc_removeservice(name,&sec);
    return Py_BuildValue("b", 1 == 1);    /* Boolean */   
} /* PyEGO_esc_delete_service */

/*
 *-------------------------------------------------------------------
 *
 * do_query
 *
 *  DESCRIPTION: 
 *   Remove a specified service.
 *
 *  PARAMETERS:
 *   argc [IN] : the number of parameters
 *   argv [IN] : the parameter array
 *  RETURN:  
 *   NONE
 *--------------------------------------------------------------------
 */
static PyObject *
PyEGO_esc_query_service (PyEGO * self, PyObject * args){
    int    cc, i;
    char   *name = NULL;
    esc_security_def_t  sec;
    esc_service_info_reply_t    reply;
    PyObject *obj = NULL;
    PyObject *ilist = NULL;

    PyArg_ParseTuple(args, "s", &name);

    sec.username = "Admin";
    sec.password = "Admin";
    sec.credential = NULL;
    printf("Getting sevice %s\n", name);
    cc = esc_sec_queryservice(name, &reply, &sec);
    if (cc == 0) {
	ilist = PyList_New(reply.serviceV[0].instC);
	for(i=0; i<reply.serviceV[0].instC; i++) {
        PyList_SetItem(ilist, i,
	    Py_BuildValue("i", reply.serviceV[0].instV[i].seqno));	    
	}
	obj = Py_BuildValue("siiiO", name, reply.serviceV[0].instC,
	                    reply.serviceV[0].context.minInstances,
		            reply.serviceV[0].context.maxInstances, ilist);
	return (obj);
    } else {
	obj = Py_BuildValue("siiiO", name, -1, -1, -1, NULL);
        return (obj);
    }
} /* PyEGO_esc_query_service */

/*
 *-------------------------------------------------------------------
 *
 * do_update
 *
 *  DESCRIPTION: 
 *   Create a specified service.
 *
 *  PARAMETERS:
 *   argc [IN] : the number of parameters
 *   argv [IN] : the parameter array
 *  RETURN:  
 *   NONE
 *--------------------------------------------------------------------
 */
static PyObject *
PyEGO_esc_update_service(PyEGO * self, PyObject * args){
    char      *xmlstr = NULL;
    int       cc;
    esc_security_def_t  sec;
 
    PyArg_ParseTuple(args, "s", &xmlstr);
    
    sec.username = "Admin";
    sec.password = "Admin";
    sec.credential = NULL;
    cc = esc_updateservice(xmlstr,&sec);    
    if (cc != 0){
	return Py_BuildValue("b", 0 == 1);  
    } else {
        printf("create service success.\n");
    }
 
    return Py_BuildValue("b", 1 == 1);    /* Boolean */
}/* PyEGO_esc_update_service() */

/*
 *-------------------------------------------------------------------
 *
 * PyEGO_esc_config_service
 *
 *  DESCRIPTION:
 *   Config a specified service.
 *
 *  PARAMETERS:
 *   argc [IN] : the number of parameters
 *   argv [IN] : the parameter array
 *  RETURN:
 *   NONE
 *--------------------------------------------------------------------
 */
static PyObject *
PyEGO_esc_config_service (PyEGO * self, PyObject * args){
	esc_service_config_req_t req;
	int cc = 0;
	int minInstances = 0;
	int maxInstances = 0;
	char *seqno = NULL;
	char *sName = NULL;
	esc_security_def_t  sec;
	sec.username = "Admin";
	sec.password = "Admin";
	sec.credential = NULL;

	PyArg_ParseTuple(args, "siis", &sName, &minInstances, &maxInstances, &seqno);

	/*$7 = {serviceName = 0x14c6e40 "test", maxInstances = 5, numOfInstanceToKill = 0, seqNoArray = 0x0, maxInstancesValue = 5, 
	 *   maxInstancesFlag = 0, minInstances = 1, minInstancesValue = 1, minInstancesFlag = 0}*/
	req.serviceName = strdup(sName);
	req.maxInstances      = maxInstances;
	req.minInstances      = minInstances;
	req.numOfInstanceToKill = 0;
	req.seqNoArray = NULL;
	req.maxInstancesValue = maxInstances;
	req.maxInstancesFlag = 0;
	req.minInstancesValue = minInstances;
	req.minInstancesFlag = 0;
	printf("min %d max %d\n", minInstances, maxInstances);
	if (seqno != NULL) {
    	    req.seqNoArray = (char **)calloc(1, sizeof(char *));
	    req.numOfInstanceToKill = 1;
	    req.seqNoArray[0] = strdup(seqno);
	} else {
		printf("seqno is empty!\n");
	}

	cc = esc_configService(&req, &sec);
	if (cc<0) {
		printf("KO\n");
		return Py_BuildValue("b", 1 == 1);    /* Boolean */
	} else {
		printf("OK\n");
		return Py_BuildValue("b", 0 == 1);    /* Boolean */
	}

} /* PyEGO_esc_config_service */

static PyMethodDef PyEGO_methods[] = {
    {"open", (PyCFunction) PyEGO_open, METH_VARARGS,
        "Open connection to vemkd"},

    {"close", (PyCFunction) PyEGO_close, METH_VARARGS,
        "Close previously opened connection to vemkd"},

    {"register", (PyCFunction) PyEGO_register, METH_VARARGS,
        "Registers client with EGO"},

    {"unregister", (PyCFunction) PyEGO_unregister, METH_VARARGS,
        "Unregisters client from EGO"},

    {"logon", (PyCFunction) PyEGO_logon, METH_VARARGS,
        "Logon EGO "},

    {"logonAndRegister", (PyCFunction) PyEGO_logonAndRegister, METH_VARARGS,
        "Combined ego.logon() and ego.register()"},

    {"read", (PyCFunction) PyEGO_read, METH_VARARGS,
        "ego_read()"},

    {"select", (PyCFunction) PyEGO_select, METH_VARARGS,
        "ego_select()"},

    {"uname", (PyCFunction) PyEGO_uname, METH_VARARGS,
        "get ego cluster infomation."},

    {"setResourceInfo", (PyCFunction) PyEGO_setResourceInfo, METH_VARARGS,
        "set EGO RPI resource."},

    {"getResourceInfo", (PyCFunction) PyEGO_getRPIRes, METH_VARARGS,
        "get EGO RPI resource."},

    {"createalloc", (PyCFunction) PyEGO_create_alloc, METH_VARARGS,
        "create EGO allocation"},

    {"freealloc", (PyCFunction) PyEGO_free_alloc, METH_VARARGS,
        "free EGO allocation"},

    {"migratedecision", (PyCFunction) PyEGO_migrate_decision, METH_VARARGS,
        "migrate EGO allocation"},

    {"getAllAlloc", (PyCFunction) PyEGO_getAllAlloc, METH_VARARGS,
        "get all EGO allocations"},

    {"getDecisionsByFilter", (PyCFunction) PyEGO_getDecisionsByFilter, METH_VARARGS,
        "get decisions by filter"},

    {"getReleaseCandidates", (PyCFunction) PyEGO_getReleaseCandidates, METH_VARARGS,
        "get release candidates"},

    {"updateDecision", (PyCFunction) PyEGO_updateDecision, METH_VARARGS,
        "update decision"},

    {"releaseDecision", (PyCFunction) PyEGO_releaseDecision, METH_VARARGS,
        "release decision"},

    {"getAllocHostByID", (PyCFunction) PyEGO_getAllocByID, METH_VARARGS,
        "get EGO allocation host by ID"},

    {"getPossibleHosts", (PyCFunction) PyEGO_get_possible_hosts, METH_VARARGS,
        "get possible hosts for one EGO allocation"},

    {"setResourcePlan", (PyCFunction) PyEGO_setResourcePlan, METH_VARARGS,
        "set EGO resource plan."},

    {"resizealloc", (PyCFunction) PyEGO_resize_alloc, METH_VARARGS,
        "resize allocation"},

    {"deleteDynamicGroup", (PyCFunction) PyEGO_delete_dynamic_resource_group, METH_VARARGS,
        "delete dynamic resource group"},

    {"createDynamicGroup", (PyCFunction) PyEGO_create_dynamic_resource_group, METH_VARARGS,
        "create dynamic resource group"},

    {"getAllResourceGroups", (PyCFunction) PyEGO_get_all_resource_group, METH_VARARGS,
        "get detail info for all resource groups"},

    {"esc_create_service", (PyCFunction) PyEGO_esc_create_service, METH_VARARGS,
        "Create EGO services"},

    {"esc_delete_service", (PyCFunction) PyEGO_esc_delete_service, METH_VARARGS,
        "Delete EGO services"},

    {"esc_query_service", (PyCFunction) PyEGO_esc_query_service, METH_VARARGS,
        "Query EGO services"},
	
    {"esc_update_service", (PyCFunction) PyEGO_esc_update_service, METH_VARARGS,
        "Update EGO services"},

    {"esc_config_service", (PyCFunction) PyEGO_esc_config_service, METH_VARARGS,
        "Config EGO services"},

    {NULL, NULL, 0, NULL}   /* Sentinel */
};  /* PyEGO_methods */

static PyTypeObject PyEGOType = {
    PyObject_HEAD_INIT(NULL)
        0,  /* ob_size */
    "ego.ego",  /* tp_name */
    sizeof(PyEGO),  /* tp_basicsize */
    0,  /* tp_itemsize */
    (destructor) PyEGO_dealloc, /* tp_dealloc */
    0,  /* tp_print */
    0,  /* tp_getattr */
    0,  /* tp_setattr */
    0,  /* tp_compare */
    0,  /* tp_repr */
    0,  /* tp_as_number */
    0,  /* tp_as_sequence */
    0,  /* tp_as_mapping */
    0,  /* tp_hash */
    0,  /* tp_call */
    0,  /* tp_str */
    0,  /* tp_getattro */
    0,  /* tp_setattro */
    0,  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "EGO objects",  /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    0,  /* tp_iter */
    0,  /* tp_iternext */
    PyEGO_methods,  /* tp_methods */
    PyEGO_members,  /* tp_members */
    0,  /* tp_getset */
    0,  /* tp_base */
    0,  /* tp_dict */
    0,  /* tp_descr_get */
    0,  /* tp_descr_set */
    0,  /* tp_dictoffset */
    (initproc) PyEGO_init,  /* tp_init */
    0,  /* tp_alloc */
    PyEGO_new,  /* tp_new */
};  /* PyEGOType */

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initego(void)
{
    PyObject *m;

    if (PyType_Ready(&PyEGOType) < 0) {
        return;
    }

    m = Py_InitModule3("ego", module_methods, "EGO Python Bindings");
    if (m == NULL) {
        return;
    }

    Py_INCREF(&PyEGOType);
    PyModule_AddObject(m, "ego", (PyObject *) & PyEGOType);

    /* Add 'EGOError' exception */
    EGOError = PyErr_NewException("ego.error", NULL, NULL);
    Py_INCREF(EGOError);
    PyModule_AddObject(m, "error", EGOError);
}   /* initego() */
